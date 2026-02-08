#!/bin/bash
# Deployment examples for IAM Inactive User Cleanup

# =============================================================================
# BASIC DEPLOYMENTS
# =============================================================================

# Deploy to development environment
aws cloudformation create-stack \
  --stack-name iam-cleanup-dev \
  --template-body file://cloudformation/template.yaml \
  --parameters file://cloudformation/parameters/dev.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --tags \
    Key=Environment,Value=Development \
    Key=ManagedBy,Value=CloudFormation

# Deploy to production environment
aws cloudformation create-stack \
  --stack-name iam-cleanup-prod \
  --template-body file://cloudformation/template.yaml \
  --parameters file://cloudformation/parameters/prod.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --tags \
    Key=Environment,Value=Production \
    Key=ManagedBy,Value=CloudFormation

# =============================================================================
# DEPLOYMENT WITH INLINE PARAMETERS
# =============================================================================

# Deploy with custom parameters
aws cloudformation create-stack \
  --stack-name iam-inactive-user-cleanup \
  --template-body file://cloudformation/template.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=90 \
    ParameterKey=GracePeriodDays,ParameterValue=30 \
    ParameterKey=NotificationEmail,ParameterValue=security@example.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# =============================================================================
# MULTI-REGION DEPLOYMENT
# =============================================================================

# Deploy to multiple regions
for region in us-east-1 us-west-2 eu-west-1; do
  aws cloudformation create-stack \
    --stack-name iam-cleanup-prod \
    --template-body file://cloudformation/template.yaml \
    --parameters file://cloudformation/parameters/prod.json \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $region \
    --tags \
      Key=Environment,Value=Production \
      Key=Region,Value=$region
done

# =============================================================================
# VALIDATION AND TESTING
# =============================================================================

# Validate template before deployment
aws cloudformation validate-template \
  --template-body file://cloudformation/template.yaml

# Create change set to preview changes
aws cloudformation create-change-set \
  --stack-name iam-cleanup-prod \
  --change-set-name update-$(date +%Y%m%d-%H%M%S) \
  --template-body file://cloudformation/template.yaml \
  --parameters file://cloudformation/parameters/prod.json \
  --capabilities CAPABILITY_NAMED_IAM

# Review change set
aws cloudformation describe-change-set \
  --stack-name iam-cleanup-prod \
  --change-set-name update-20250207-120000

# Execute change set
aws cloudformation execute-change-set \
  --stack-name iam-cleanup-prod \
  --change-set-name update-20250207-120000

# =============================================================================
# STACK UPDATES
# =============================================================================

# Update stack with new parameters
aws cloudformation update-stack \
  --stack-name iam-cleanup-prod \
  --template-body file://cloudformation/template.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=60 \
    ParameterKey=GracePeriodDays,ParameterValue=14 \
    ParameterKey=NotificationEmail,UsePreviousValue=true \
  --capabilities CAPABILITY_NAMED_IAM

# Update stack with new template
aws cloudformation update-stack \
  --stack-name iam-cleanup-prod \
  --template-body file://cloudformation/template.yaml \
  --parameters file://cloudformation/parameters/prod.json \
  --capabilities CAPABILITY_NAMED_IAM

# =============================================================================
# STACK MONITORING
# =============================================================================

# Monitor stack creation
aws cloudformation describe-stacks \
  --stack-name iam-cleanup-prod \
  --query 'Stacks[0].StackStatus'

# Watch stack events
aws cloudformation describe-stack-events \
  --stack-name iam-cleanup-prod \
  --max-items 20

# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name iam-cleanup-prod \
  --query 'Stacks[0].Outputs'

# =============================================================================
# TESTING DEPLOYED STACK
# =============================================================================

# Run validation tests
python3 scripts/test_iam_cleanup.py --stack-name iam-cleanup-prod --validate

# Check IAM user status
python3 scripts/test_iam_cleanup.py --stack-name iam-cleanup-prod --check-users

# Trigger manual scan
python3 scripts/test_iam_cleanup.py --stack-name iam-cleanup-prod --scan

# List flagged users
python3 scripts/test_iam_cleanup.py --stack-name iam-cleanup-prod --list-flagged

# Send test notification
python3 scripts/test_iam_cleanup.py --stack-name iam-cleanup-prod --test-notification

# Run all tests
python3 scripts/test_iam_cleanup.py --stack-name iam-cleanup-prod --all

# =============================================================================
# STACK DELETION
# =============================================================================

# Delete stack
aws cloudformation delete-stack \
  --stack-name iam-cleanup-prod

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name iam-cleanup-prod

# =============================================================================
# MULTI-ACCOUNT DEPLOYMENT (AWS Organizations)
# =============================================================================

# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name iam-cleanup-org-wide \
  --template-body file://cloudformation/template.yaml \
  --parameters file://cloudformation/parameters/prod.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --description "Organization-wide IAM inactive user cleanup"

# Deploy to specific accounts
aws cloudformation create-stack-instances \
  --stack-set-name iam-cleanup-org-wide \
  --accounts 123456789012 234567890123 \
  --regions us-east-1 \
  --parameter-overrides \
    ParameterKey=NotificationEmail,ParameterValue=central-security@example.com

# Deploy to organizational units
aws cloudformation create-stack-instances \
  --stack-set-name iam-cleanup-org-wide \
  --deployment-targets OrganizationalUnitIds=ou-xxxx-yyyyyyyy \
  --regions us-east-1 us-west-2

# =============================================================================
# CLOUDWATCH LOG INSPECTION
# =============================================================================

# Tail Scanner Lambda logs
aws logs tail /aws/lambda/iam-cleanup-prod-InactiveUserScanner --follow

# Tail Cleanup Lambda logs
aws logs tail /aws/lambda/iam-cleanup-prod-InactiveUserCleanup --follow

# Query logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/iam-cleanup-prod-InactiveUserScanner \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000

# =============================================================================
# DYNAMODB OPERATIONS
# =============================================================================

# Scan DynamoDB table for flagged users
aws dynamodb scan \
  --table-name iam-cleanup-prod-InactiveUsers \
  --output table

# Get specific user
aws dynamodb get-item \
  --table-name iam-cleanup-prod-InactiveUsers \
  --key '{"username": {"S": "john.doe"}}'

# Remove user from tracking (prevent deletion)
aws dynamodb delete-item \
  --table-name iam-cleanup-prod-InactiveUsers \
  --key '{"username": {"S": "john.doe"}}'

# =============================================================================
# SNS OPERATIONS
# =============================================================================

# List SNS subscriptions
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:iam-cleanup-prod-InactiveUserNotifications

# Publish test message
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:iam-cleanup-prod-InactiveUserNotifications \
  --subject "Test Notification" \
  --message "This is a test notification from IAM cleanup automation"

# =============================================================================
# LAMBDA OPERATIONS
# =============================================================================

# Invoke Scanner Lambda manually
aws lambda invoke \
  --function-name iam-cleanup-prod-InactiveUserScanner \
  --invocation-type RequestResponse \
  --log-type Tail \
  response.json

# View response
cat response.json | jq

# Get Lambda function configuration
aws lambda get-function-configuration \
  --function-name iam-cleanup-prod-InactiveUserScanner

# Update Lambda environment variables
aws lambda update-function-configuration \
  --function-name iam-cleanup-prod-InactiveUserScanner \
  --environment Variables={TABLE_NAME=iam-cleanup-prod-InactiveUsers}

# =============================================================================
# EVENTBRIDGE OPERATIONS
# =============================================================================

# Describe EventBridge rule
aws events describe-rule \
  --name iam-cleanup-prod-DailyScan

# Disable daily scanning
aws events disable-rule \
  --name iam-cleanup-prod-DailyScan

# Enable daily scanning
aws events enable-rule \
  --name iam-cleanup-prod-DailyScan

# =============================================================================
# COST ANALYSIS
# =============================================================================

# Get cost for the last month (requires Cost Explorer API)
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '1 month ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --filter file://cost-filter.json

# Example cost-filter.json:
# {
#   "Tags": {
#     "Key": "aws:cloudformation:stack-name",
#     "Values": ["iam-cleanup-prod"]
#   }
# }
