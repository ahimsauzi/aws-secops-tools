#!/bin/bash

# AWS SecOps Tools - Repository Setup Script
# This script helps you quickly set up the repository for development and deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "=================================================================="
    echo "$1"
    echo "=================================================================="
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_header "AWS SecOps Tools - Repository Setup"

    # Check prerequisites
    print_info "Checking prerequisites..."
    
    if ! command_exists git; then
        print_error "git is not installed. Please install git first."
        exit 1
    fi
    print_success "git is installed"

    if ! command_exists aws; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    print_success "AWS CLI is installed"

    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.12+ first."
        exit 1
    fi
    print_success "Python 3 is installed ($(python3 --version))"

    # Check AWS credentials
    print_info "Checking AWS credentials..."
    if aws sts get-caller-identity &>/dev/null; then
        print_success "AWS credentials configured"
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        print_info "Account ID: $ACCOUNT_ID"
    else
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi

    # Git repository initialization
    print_header "Git Repository Setup"
    
    if [ -d .git ]; then
        print_info "Git repository already initialized"
    else
        read -p "Initialize git repository? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git init
            print_success "Git repository initialized"
        fi
    fi

    # Set up Python virtual environment
    print_header "Python Environment Setup"
    
    read -p "Create Python virtual environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d venv ]; then
            print_info "Virtual environment already exists"
        else
            python3 -m venv venv
            print_success "Virtual environment created"
        fi
        
        print_info "Activating virtual environment..."
        source venv/bin/activate
        
        print_info "Installing dependencies..."
        pip install --upgrade pip
        pip install boto3 pytest pylint
        print_success "Dependencies installed"
    fi

    # Validate CloudFormation templates
    print_header "CloudFormation Template Validation"
    
    read -p "Validate CloudFormation templates? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for template in */cloudformation/template.yaml; do
            if [ -f "$template" ]; then
                print_info "Validating $template..."
                if aws cloudformation validate-template --template-body file://"$template" &>/dev/null; then
                    print_success "$template is valid"
                else
                    print_error "$template validation failed"
                fi
            fi
        done
    fi

    # Configure Git hooks (optional)
    print_header "Git Hooks Setup"
    
    read -p "Set up Git pre-commit hooks? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p .git/hooks
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to validate CloudFormation templates

echo "Running pre-commit checks..."

# Validate CloudFormation templates
for template in */cloudformation/template.yaml; do
    if [ -f "$template" ]; then
        echo "Validating $template..."
        if ! aws cloudformation validate-template --template-body file://"$template" &>/dev/null; then
            echo "ERROR: $template validation failed"
            exit 1
        fi
    fi
done

# Check for secrets
if git diff --cached | grep -i -E '(aws_access_key|aws_secret|password.*=|token.*=)'; then
    echo "ERROR: Potential secret detected in commit!"
    exit 1
fi

echo "Pre-commit checks passed!"
exit 0
EOF
        chmod +x .git/hooks/pre-commit
        print_success "Pre-commit hook installed"
    fi

    # Test script setup
    print_header "Test Scripts Setup"
    
    for script in */scripts/*.py; do
        if [ -f "$script" ]; then
            chmod +x "$script"
            print_success "Made $script executable"
        fi
    done

    # Example deployment
    print_header "Example Deployment (Optional)"
    
    read -p "Deploy IAM Inactive User Cleanup to test environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter notification email: " email
        read -p "Enter stack name (default: iam-cleanup-test): " stack_name
        stack_name=${stack_name:-iam-cleanup-test}
        
        print_info "Deploying stack $stack_name..."
        
        aws cloudformation create-stack \
            --stack-name "$stack_name" \
            --template-body file://iam-inactive-user-cleanup/cloudformation/template.yaml \
            --parameters \
                ParameterKey=InactivityThresholdDays,ParameterValue=30 \
                ParameterKey=GracePeriodDays,ParameterValue=7 \
                ParameterKey=NotificationEmail,ParameterValue="$email" \
            --capabilities CAPABILITY_NAMED_IAM \
            --tags \
                Key=Environment,Value=Test \
                Key=ManagedBy,Value=CloudFormation
        
        print_success "Stack deployment initiated!"
        print_info "Monitor progress: aws cloudformation describe-stacks --stack-name $stack_name"
        print_info "Don't forget to confirm the SNS subscription email!"
    fi

    # Summary
    print_header "Setup Complete!"
    
    echo "Next steps:"
    echo "1. Review the main README.md"
    echo "2. Explore individual tool documentation"
    echo "3. If you deployed a stack, confirm the SNS subscription email"
    echo "4. Run validation: python3 iam-inactive-user-cleanup/scripts/test_iam_cleanup.py --validate"
    echo ""
    echo "To push to GitHub:"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    echo "  git remote add origin https://github.com/yourusername/aws-secops-tools.git"
    echo "  git push -u origin main"
    echo ""
    print_success "Happy securing! 🔒"
}

# Run main function
main
