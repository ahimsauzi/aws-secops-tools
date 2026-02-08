# Repository Structure

This document explains the organization and layout of the AWS SecOps Tools repository.

## 📁 Repository Layout

```
aws-secops-tools/
├── README.md                          # Main repository overview
├── QUICK_START.md                     # 5-minute getting started guide
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore patterns
├── setup.sh                           # Interactive setup script
│
├── .github/                           # GitHub-specific files
│   ├── workflows/
│   │   └── validate.yml               # CI/CD for validation
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md              # Bug report template
│   │   └── feature_request.md         # Feature request template
│   └── pull_request_template.md       # PR template
│
├── iam-inactive-user-cleanup/         # IAM inactive user automation tool
│   ├── README.md                      # Tool-specific overview
│   ├── DEPLOYMENT_GUIDE.md            # Detailed deployment guide
│   │
│   ├── cloudformation/                # CloudFormation templates
│   │   ├── template.yaml              # Main CFN template
│   │   └── parameters/                # Sample parameter files
│   │       ├── dev.json               # Dev environment params
│   │       └── prod.json              # Prod environment params
│   │
│   ├── scripts/                       # Utility scripts
│   │   └── test_iam_cleanup.py        # Testing & validation script
│   │
│   ├── examples/                      # Example usage
│   │   └── deployment-examples.sh     # Sample deployment commands
│   │
│   └── docs/                          # Additional documentation
│       └── troubleshooting.md         # Troubleshooting guide
│
└── [future-tools]/                    # Additional security tools
    └── (same structure as above)
```

## 📄 File Descriptions

### Root Level Files

#### README.md
- **Purpose**: Main entry point for the repository
- **Contents**: Overview of all tools, quick links, repository philosophy
- **Audience**: All users - first file they should read

#### QUICK_START.md
- **Purpose**: Fast-track guide for getting started
- **Contents**: Step-by-step deployment in 5 minutes
- **Audience**: Users who want to deploy quickly

#### CONTRIBUTING.md
- **Purpose**: Guide for contributors
- **Contents**: How to contribute, code standards, PR process
- **Audience**: Contributors and maintainers

#### LICENSE
- **Purpose**: Legal licensing information
- **Contents**: MIT License terms
- **Audience**: Legal/compliance teams, contributors

#### .gitignore
- **Purpose**: Git exclusion patterns
- **Contents**: Credentials, logs, build artifacts to exclude
- **Audience**: Developers

#### setup.sh
- **Purpose**: Interactive setup and validation
- **Contents**: Environment checks, deployment helper
- **Audience**: New users, automation

### .github/ Directory

Contains GitHub-specific configurations and templates.

#### workflows/validate.yml
- **Purpose**: CI/CD pipeline
- **Actions**: 
  - Validate CloudFormation templates
  - Lint Python code
  - Run security scans
  - Check markdown formatting

#### ISSUE_TEMPLATE/bug_report.md
- **Purpose**: Standardize bug reports
- **Contents**: Template for reporting issues
- **Usage**: Automatically shown when creating a bug report issue

#### ISSUE_TEMPLATE/feature_request.md
- **Purpose**: Standardize feature requests
- **Contents**: Template for suggesting enhancements
- **Usage**: Automatically shown when creating a feature request

#### pull_request_template.md
- **Purpose**: Standardize pull requests
- **Contents**: Checklist for PR submissions
- **Usage**: Automatically shown when creating a PR

### Tool Directory Structure

Each tool follows a consistent structure:

#### README.md (Tool Level)
- **Purpose**: Tool-specific documentation
- **Contents**:
  - Architecture diagram
  - Features and benefits
  - Quick deployment
  - How it works
  - Monitoring and troubleshooting
  - Cost estimates

#### DEPLOYMENT_GUIDE.md
- **Purpose**: Comprehensive deployment instructions
- **Contents**:
  - Step-by-step deployment
  - Production best practices
  - Multi-account strategies
  - Security hardening
  - Testing procedures
  - Rollback plans

#### cloudformation/template.yaml
- **Purpose**: Infrastructure-as-Code
- **Contents**:
  - All AWS resources needed
  - IAM roles and policies
  - Lambda functions (inline code)
  - DynamoDB tables
  - SNS topics
  - EventBridge rules
  - CloudWatch log groups

#### cloudformation/parameters/*.json
- **Purpose**: Environment-specific configurations
- **Files**:
  - `dev.json`: Development/test parameters
  - `prod.json`: Production parameters
- **Usage**: 
  ```bash
  aws cloudformation create-stack \
    --parameters file://cloudformation/parameters/prod.json
  ```

#### scripts/test_*.py
- **Purpose**: Testing and validation
- **Contents**:
  - Deployment validation
  - Functional testing
  - Manual triggers
  - Health checks
- **Usage**: Run after deployment to verify

#### examples/deployment-examples.sh
- **Purpose**: Reference implementation
- **Contents**:
  - AWS CLI commands for deployment
  - Multi-region examples
  - Update procedures
  - Monitoring commands
  - Cleanup commands

#### docs/troubleshooting.md
- **Purpose**: Problem resolution
- **Contents**:
  - Common issues and solutions
  - Diagnostic commands
  - Error messages explained
  - Performance tuning

## 🗂️ File Naming Conventions

### CloudFormation Templates
- Main template: `template.yaml` (always)
- Parameters: `{environment}.json` (dev.json, prod.json, staging.json)

### Python Scripts
- Test scripts: `test_{tool_name}.py`
- All Python files: lowercase with underscores

### Shell Scripts
- Examples: `deployment-examples.sh`
- Setup: `setup.sh`
- All scripts: lowercase with hyphens

### Documentation
- Tool READMEs: `README.md`
- Guides: `{GUIDE_NAME}.md` (uppercase, e.g., DEPLOYMENT_GUIDE.md)
- Docs: `{topic}.md` (lowercase, e.g., troubleshooting.md)

## 📐 Design Principles

### 1. Consistency
- All tools follow the same directory structure
- Similar features have similar implementations
- Consistent naming across tools

### 2. Self-Contained
- Each tool can be deployed independently
- No cross-tool dependencies
- Complete documentation per tool

### 3. Production-Ready
- CloudFormation for IaC
- Testing scripts included
- Troubleshooting guides provided
- Examples for common scenarios

### 4. Developer-Friendly
- Clear README at every level
- Examples for all operations
- Inline comments in code
- Pre-commit hooks available

### 5. Security-First
- Least-privilege IAM policies
- No hardcoded credentials
- Security scanning in CI/CD
- Secrets excluded via .gitignore

## 🔄 Workflow

### For Users

1. **Discovery**: Read main `README.md`
2. **Quick Start**: Follow `QUICK_START.md`
3. **Tool Selection**: Choose a tool (e.g., `iam-inactive-user-cleanup/`)
4. **Deep Dive**: Read tool's `README.md`
5. **Deployment**: Follow `DEPLOYMENT_GUIDE.md`
6. **Testing**: Run `scripts/test_*.py`
7. **Production**: Use `cloudformation/parameters/prod.json`
8. **Troubleshooting**: Check `docs/troubleshooting.md`

### For Contributors

1. **Setup**: Run `setup.sh`
2. **Guidelines**: Read `CONTRIBUTING.md`
3. **Create Branch**: `git checkout -b feature/new-tool`
4. **Develop**: Follow directory structure
5. **Test**: Validate templates, test scripts
6. **Document**: Update READMEs, add examples
7. **PR**: Use PR template, pass CI/CD

## 📦 Adding a New Tool

To add a new security tool to the repository:

### 1. Create Directory Structure

```bash
mkdir -p new-tool/{cloudformation/parameters,scripts,examples,docs}
```

### 2. Create Required Files

```bash
touch new-tool/README.md
touch new-tool/DEPLOYMENT_GUIDE.md
touch new-tool/cloudformation/template.yaml
touch new-tool/cloudformation/parameters/{dev,prod}.json
touch new-tool/scripts/test_new_tool.py
touch new-tool/examples/deployment-examples.sh
touch new-tool/docs/troubleshooting.md
```

### 3. Populate Files

Use existing tools as templates. Key sections:

**README.md**:
- Overview and features
- Architecture diagram
- Quick start
- How it works
- Monitoring

**DEPLOYMENT_GUIDE.md**:
- Prerequisites
- Step-by-step deployment
- Production best practices
- Testing procedures

**template.yaml**:
- All AWS resources
- Parameters with descriptions
- Outputs with export names

**test_*.py**:
- Deployment validation
- Functional testing
- Health checks

### 4. Update Main README

Add new tool to the tools list in root `README.md`:

```markdown
### [New Tool Name](./new-tool/)
Brief description of what it does.

**Features:**
- Feature 1
- Feature 2

**Status:** ✅ Production Ready / ⚠️ Beta / 🚧 Development
```

### 5. Submit PR

Follow the PR template and contribution guidelines.

## 🎨 Styling Guidelines

### Markdown
- Use ATX-style headers (`#` not underlines)
- Code blocks with language specifiers
- Emoji for visual organization (sparingly)
- Tables for comparisons

### CloudFormation
- YAML format (not JSON)
- Meaningful resource names
- Comprehensive descriptions
- Logical resource grouping
- Comments for complex logic

### Python
- PEP 8 style guide
- Type hints
- Docstrings for functions
- Error handling with logging

### Shell Scripts
- Bash shebang: `#!/bin/bash`
- Error handling: `set -e`
- Comments for complex operations
- Executable permissions

## 📊 Metrics and Stats

To keep the repository organized:

- **Max directory depth**: 4 levels
- **Max file size**: 500 KB (except CloudFormation)
- **Required files per tool**: 7 minimum (README, guide, template, etc.)
- **Documentation coverage**: 100% of features documented

## 🔍 Finding Files

### By Purpose

| Looking for... | Location |
|----------------|----------|
| Getting started | `QUICK_START.md` |
| Tool overview | `{tool}/README.md` |
| Deployment steps | `{tool}/DEPLOYMENT_GUIDE.md` |
| CloudFormation | `{tool}/cloudformation/template.yaml` |
| Testing | `{tool}/scripts/test_*.py` |
| Examples | `{tool}/examples/` |
| Troubleshooting | `{tool}/docs/troubleshooting.md` |
| Contributing | `CONTRIBUTING.md` |
| CI/CD | `.github/workflows/` |

### By File Type

```bash
# Find all CloudFormation templates
find . -name "template.yaml"

# Find all Python scripts
find . -name "*.py"

# Find all documentation
find . -name "*.md"

# Find all examples
find . -path "*/examples/*"
```

## 🚀 Repository Evolution

As the repository grows:

1. **New tools** follow the established structure
2. **Common utilities** may be extracted to a shared directory
3. **Documentation** remains at the tool level
4. **Examples** stay specific to each tool

The structure is designed to scale from 1 to 100+ tools while maintaining clarity and usability.

---

**Questions about the structure?** Open a [discussion](https://github.com/yourusername/aws-secops-tools/discussions) or check [CONTRIBUTING.md](CONTRIBUTING.md).
