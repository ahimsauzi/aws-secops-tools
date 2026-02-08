# Deployment Guide & Best Practices

## 🚀 Quick Start Deployment

### Step 1: Prepare Your Environment

```bash
# Clone or download the files
# Ensure you have AWS CLI configured
aws sts get-caller-identity

# Verify you have necessary permissions
aws iam get-user
```

### Step 2: Deploy the Stack

```bash
# Deploy with default parameters (90 days inactivity, 30 days grace)
aws cloudformation create-stack \
  --stack-name iam-inactive-user-cleanup \
  --template-body file://iam-inactive-user-cleanup.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=90 \
    ParameterKey=GracePeriodDays,ParameterValue=30 \
    ParameterKey=NotificationEmail,ParameterValue=security-team@yourcompany.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --tags \
    Key=Environment,Value=Production \
    Key=Purpose,Value=SecurityAutomation \
    Key=ManagedBy,Value=CloudFormation
```

### Step 3: Confirm SNS Subscription

**CRITICAL**: You must confirm the SNS email subscription!

1. Check your email inbox for "AWS Notification - Subscription Confirmation"
2. Click the "Confirm subscription" link
3. You should see "Subscription confirmed!"

### Step 4: Validate Deployment

```bash
# Make the test script executable
chmod +x test_iam_cleanup.py

# Run validation
python3 test_iam_cleanup.py --validate

# Check current IAM user status
python3 test_iam_cleanup.py --check-users

# Test notifications
python3 test_iam_cleanup.py --test-notification
```

### Step 5: Monitor First Scan

```bash
# Wait for the scheduled scan (9 AM UTC daily) or trigger manually
python3 test_iam_cleanup.py --scan

# Check CloudWatch Logs
aws logs tail /aws/lambda/iam-inactive-user-cleanup-InactiveUserScanner --follow

# List flagged users
python3 test_iam_cleanup.py --list-flagged
```

## 🏢 Production Deployment Best Practices

### 1. Staged Rollout

**Phase 1: Test Environment (Week 1-2)**
```bash
# Deploy to test/dev account first
aws cloudformation create-stack \
  --stack-name iam-inactive-user-cleanup-test \
  --template-body file://iam-inactive-user-cleanup.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=30 \
    ParameterKey=GracePeriodDays,ParameterValue=7 \
    ParameterKey=NotificationEmail,ParameterValue=devops@yourcompany.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --profile test-account
```

**Phase 2: Production with Long Grace Period (Week 3-4)**
```bash
# Deploy to production with extended grace period initially
aws cloudformation create-stack \
  --stack-name iam-inactive-user-cleanup \
  --template-body file://iam-inactive-user-cleanup.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=90 \
    ParameterKey=GracePeriodDays,ParameterValue=60 \
    ParameterKey=NotificationEmail,ParameterValue=security-team@yourcompany.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --profile production
```

**Phase 3: Optimize (Week 5+)**
```bash
# After validating behavior, reduce grace period
aws cloudformation update-stack \
  --stack-name iam-inactive-user-cleanup \
  --template-body file://iam-inactive-user-cleanup.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=90 \
    ParameterKey=GracePeriodDays,ParameterValue=30 \
    ParameterKey=NotificationEmail,UsePreviousValue=true \
  --capabilities CAPABILITY_NAMED_IAM
```

### 2. Pre-Deployment Assessment

**Analyze Your Current IAM Users:**
```bash
# Run assessment before deployment
python3 test_iam_cleanup.py --check-users > iam_assessment.txt

# Review the output
cat iam_assessment.txt
```

**Expected Output:**
```
Total IAM Users: 45
Inactive Users (>90 days): 12

Inactive Users:
  • old-contractor-account - 365 days (2024-02-07)
  • test-user-2023 - 200 days (2024-07-20)
  ...
```

**Action Items:**
1. Review the list with your team
2. Identify service accounts (exclude them - see below)
3. Contact users proactively before deployment
4. Document any exceptions

### 3. Excluding Service Accounts

**Option A: Tag-Based Exclusion (Recommended)**

Modify the Scanner Lambda to check for tags:

```python
# Add this function to scanner Lambda
def should_exclude_user(username):
    """Check if user should be excluded from scanning"""
    try:
        response = iam.list_user_tags(UserName=username)
        tags = response.get('Tags', [])
        
        # Check for exclusion tag
        for tag in tags:
            if tag['Key'] == 'IAMCleanupExclude' and tag['Value'] == 'true':
                return True
        return False
    except Exception as e:
        print(f"Error checking tags for {username}: {str(e)}")
        return False

# Then in the main loop, add:
if should_exclude_user(username):
    print(f"Excluding user {username} (tagged for exclusion)")
    continue
```

**Tag your service accounts:**
```bash
# Tag service accounts to exclude them
aws iam tag-user \
  --user-name service-account-ci-cd \
  --tags Key=IAMCleanupExclude,Value=true

aws iam tag-user \
  --user-name automation-bot \
  --tags Key=IAMCleanupExclude,Value=true
```

**Option B: Prefix-Based Exclusion**

```python
# Add to scanner Lambda
EXCLUDED_PREFIXES = ['svc-', 'service-', 'automation-', 'bot-']

def should_exclude_user(username):
    return any(username.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
```

**Option C: Explicit Exclusion List**

```python
# Add to Lambda environment variables
EXCLUDED_USERS = os.environ.get('EXCLUDED_USERS', '').split(',')

def should_exclude_user(username):
    return username in EXCLUDED_USERS
```

### 4. Multi-Account Deployment

**Using AWS Organizations:**

```bash
# Deploy to all accounts in an OU using StackSets
aws cloudformation create-stack-set \
  --stack-set-name iam-inactive-user-cleanup \
  --template-body file://iam-inactive-user-cleanup.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=90 \
    ParameterKey=GracePeriodDays,ParameterValue=30 \
    ParameterKey=NotificationEmail,ParameterValue=security@yourcompany.com \
  --capabilities CAPABILITY_NAMED_IAM

# Deploy to specific OUs
aws cloudformation create-stack-instances \
  --stack-set-name iam-inactive-user-cleanup \
  --deployment-targets OrganizationalUnitIds=ou-xxxx-xxxxxxxx \
  --regions us-east-1
```

### 5. Monitoring & Alerting

**Create CloudWatch Alarms:**

```bash
# Alarm for Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name iam-cleanup-scanner-errors \
  --alarm-description "Alert on Scanner Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=iam-inactive-user-cleanup-InactiveUserScanner

# Alarm for cleanup Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name iam-cleanup-deletion-errors \
  --alarm-description "Alert on Cleanup Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=iam-inactive-user-cleanup-InactiveUserCleanup
```

**Set up CloudWatch Dashboard:**

```bash
# Create dashboard (save as dashboard.json first)
aws cloudwatch put-dashboard \
  --dashboard-name IAMCleanupMonitoring \
  --dashboard-body file://dashboard.json
```

### 6. Backup & Recovery

**Before Deployment - Backup IAM Users:**

```bash
# Export all IAM users and their configurations
aws iam list-users --output json > iam_users_backup_$(date +%Y%m%d).json

# Export user policies
for user in $(aws iam list-users --query 'Users[*].UserName' --output text); do
    aws iam list-user-policies --user-name $user > "backup_${user}_policies.json"
    aws iam list-attached-user-policies --user-name $user > "backup_${user}_attached.json"
done
```

**Recovery Process:**

If a user is mistakenly deleted:

1. **Recreate the user:**
```bash
aws iam create-user --user-name john.doe
```

2. **Restore policies from backup:**
```bash
# Reattach managed policies
aws iam attach-user-policy \
  --user-name john.doe \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Restore inline policies
aws iam put-user-policy \
  --user-name john.doe \
  --policy-name CustomPolicy \
  --policy-document file://policy.json
```

3. **Notify the user to reset credentials**

### 7. Compliance & Audit

**Enable CloudTrail for IAM Actions:**

```bash
# Ensure CloudTrail is logging IAM actions
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::IAM::User \
  --max-results 50
```

**Regular Audit Reports:**

```bash
# Weekly report of flagged users
python3 test_iam_cleanup.py --list-flagged | \
  mail -s "Weekly IAM Cleanup Report" security-team@yourcompany.com

# Monthly summary
aws dynamodb scan \
  --table-name iam-inactive-user-cleanup-InactiveUsers \
  --output json > monthly_report_$(date +%Y%m).json
```

### 8. Integration with Ticketing Systems

**Jira Integration Example:**

Modify the Scanner Lambda to create Jira tickets:

```python
import requests

def create_jira_ticket(username, deletion_date):
    """Create Jira ticket for inactive user"""
    jira_url = os.environ.get('JIRA_URL')
    jira_token = os.environ.get('JIRA_TOKEN')
    
    ticket = {
        "fields": {
            "project": {"key": "SEC"},
            "summary": f"IAM User {username} flagged for deletion",
            "description": f"""
IAM user {username} has been flagged for inactivity.

Deletion scheduled: {deletion_date}

Please review and:
1. Contact the user
2. Determine if account should be retained
3. Remove from DynamoDB if keeping active
            """,
            "issuetype": {"name": "Task"},
            "priority": {"name": "Medium"}
        }
    }
    
    response = requests.post(
        f"{jira_url}/rest/api/2/issue",
        headers={"Authorization": f"Bearer {jira_token}"},
        json=ticket
    )
    
    return response.json()
```

## 🔒 Security Hardening

### 1. Restrict Lambda IAM Roles

The default roles are permissive. For production, restrict them:

**Scanner Role - Restrict to specific user paths:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListUsers",
        "iam:GetUser",
        "iam:ListAccessKeys",
        "iam:GetAccessKeyLastUsed"
      ],
      "Resource": "arn:aws:iam::*:user/employees/*"
    }
  ]
}
```

### 2. Encrypt SNS Topics

Add encryption to the SNS topic:

```yaml
NotificationTopic:
  Type: AWS::SNS::Topic
  Properties:
    KmsMasterKeyId: !Ref SNSEncryptionKey
    # ... rest of properties

SNSEncryptionKey:
  Type: AWS::KMS::Key
  Properties:
    KeyPolicy:
      # Define key policy
```

### 3. Enable VPC Endpoints (if in VPC)

```yaml
ScannerLambdaFunction:
  Type: AWS::Lambda::Function
  Properties:
    VpcConfig:
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
```

## 📊 Cost Optimization

### Reduce Lambda Memory

For smaller accounts (<100 users):

```yaml
ScannerLambdaFunction:
  Properties:
    MemorySize: 128  # Reduce from 256 MB
    Timeout: 120     # Reduce from 300 seconds
```

### Use Reserved Capacity (if high volume)

For very large accounts with thousands of users:

```yaml
InactiveUsersTable:
  Properties:
    BillingMode: PROVISIONED
    ProvisionedThroughput:
      ReadCapacityUnits: 5
      WriteCapacityUnits: 5
```

## 🧪 Testing Checklist

Before going to production:

- [ ] Deploy to test environment
- [ ] Validate all resources created successfully
- [ ] Confirm SNS subscription
- [ ] Test notification delivery
- [ ] Manually trigger scanner Lambda
- [ ] Verify inactive users are detected
- [ ] Check DynamoDB table for flagged users
- [ ] Verify access keys are disabled
- [ ] Wait for TTL expiration (or manually delete item to test cleanup)
- [ ] Verify user cleanup Lambda executes
- [ ] Check CloudWatch Logs for errors
- [ ] Validate deletion notification sent
- [ ] Review IAM audit trail in CloudTrail
- [ ] Test recovery process (recreate deleted user)
- [ ] Load test with multiple users
- [ ] Verify cost estimates match actual usage

## 🚨 Rollback Plan

If something goes wrong:

1. **Immediate Stop:**
```bash
# Disable the EventBridge rule to stop scans
aws events disable-rule --name iam-inactive-user-cleanup-DailyScan

# Disable DynamoDB Streams to stop deletions
aws lambda delete-event-source-mapping \
  --uuid <EVENT_SOURCE_MAPPING_UUID>
```

2. **Remove Flagged Users from DynamoDB:**
```bash
# Clear all items from DynamoDB (prevents deletion)
aws dynamodb scan \
  --table-name iam-inactive-user-cleanup-InactiveUsers \
  --attributes-to-get username | \
jq -r '.Items[].username.S' | \
while read user; do
  aws dynamodb delete-item \
    --table-name iam-inactive-user-cleanup-InactiveUsers \
    --key "{\"username\": {\"S\": \"$user\"}}"
done
```

3. **Full Stack Deletion:**
```bash
aws cloudformation delete-stack --stack-name iam-inactive-user-cleanup
```

## 📞 Support & Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Users not being flagged | Check IAM permissions, review CloudWatch Logs |
| Notifications not received | Confirm SNS subscription, check spam folder |
| TTL not triggering deletions | TTL can take up to 48 hours, check DynamoDB TTL status |
| Lambda timeout | Increase timeout, reduce memory, or batch operations |
| High costs | Switch to provisioned capacity, reduce log retention |

## 📝 Change Log Template

Track all changes to your deployment:

```markdown
# Deployment Change Log

## 2025-02-07 - Initial Deployment
- Stack: iam-inactive-user-cleanup
- Parameters: 90 days inactivity, 30 days grace
- Environment: Production
- Deployed by: security-team

## 2025-02-14 - Updated Grace Period
- Changed grace period from 30 to 45 days
- Reason: Business requirement for longer notice
```

---

**Remember**: This is a powerful automation tool. Always test thoroughly in non-production environments before deploying to production!
