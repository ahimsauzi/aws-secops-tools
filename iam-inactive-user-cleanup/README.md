# AWS IAM Inactive User Cleanup - CloudFormation Stack

A comprehensive CloudSecOps automation solution that automatically identifies, flags, and removes inactive IAM users in your AWS account. This implements shift-left security principles by proactively managing IAM user lifecycle.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CloudWatch Events (Daily)                    │
│                          9:00 AM UTC                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Scanner Lambda Function                       │
│  • Lists all IAM users                                           │
│  • Checks last activity (console + access keys)                  │
│  • Flags users inactive > threshold days                         │
│  • Disables access keys immediately                              │
│  • Adds to DynamoDB with TTL                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DynamoDB Table                              │
│  • Stores flagged users                                          │
│  • TTL attribute for grace period                                │
│  • Streams enabled for deletion trigger                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌─────────────────┐          ┌──────────────────┐
    │   SNS Topic     │          │  DynamoDB Stream │
    │  Notifications  │          │  (on TTL expire) │
    └─────────────────┘          └────────┬─────────┘
                                          ▼
                              ┌────────────────────────┐
                              │  Cleanup Lambda        │
                              │  • Triggered by TTL    │
                              │  • Removes all user    │
                              │    resources           │
                              │  • Deletes IAM user    │
                              │  • Sends notification  │
                              └────────────────────────┘
```

## 🔒 Security Features

- **Immediate Access Revocation**: Access keys are disabled as soon as inactivity is detected
- **Grace Period**: Configurable grace period before permanent deletion
- **Notifications**: Email alerts sent when users are flagged and deleted
- **Comprehensive Cleanup**: Removes all IAM user resources (policies, groups, keys, MFA, etc.)
- **Audit Trail**: CloudWatch Logs for all operations
- **DynamoDB Streams**: Event-driven deletion triggered by TTL expiration

## 📋 Prerequisites

- AWS Account with appropriate permissions to create CloudFormation stacks
- IAM permissions to create Lambda functions, DynamoDB tables, SNS topics, and IAM roles
- Valid email address for notifications

## 🚀 Deployment

### Using AWS Console

1. Navigate to CloudFormation in AWS Console
2. Click "Create Stack" → "With new resources"
3. Upload the `iam-inactive-user-cleanup.yaml` template
4. Fill in the parameters:
   - **InactivityThresholdDays**: Days of inactivity before flagging (default: 90)
   - **GracePeriodDays**: Days before deletion after flagging (default: 30)
   - **NotificationEmail**: Email for alerts
5. Click through and create the stack
6. **Important**: Confirm SNS subscription in your email inbox

### Using AWS CLI

```bash
aws cloudformation create-stack \
  --stack-name iam-inactive-user-cleanup \
  --template-body file://iam-inactive-user-cleanup.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=90 \
    ParameterKey=GracePeriodDays,ParameterValue=30 \
    ParameterKey=NotificationEmail,ParameterValue=security-team@example.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Confirm SNS Subscription

After deployment, you'll receive an email to confirm the SNS subscription. **You must confirm this** to receive notifications.

## ⚙️ Configuration Parameters

| Parameter | Description | Default | Min | Max |
|-----------|-------------|---------|-----|-----|
| `InactivityThresholdDays` | Days of inactivity before flagging user | 90 | 1 | 365 |
| `GracePeriodDays` | Days before deletion after flagging | 30 | 1 | 90 |
| `NotificationEmail` | Email address for alerts | - | - | - |

## 📊 How It Works

### 1. Daily Scanning (Scanner Lambda)

**Trigger**: CloudWatch Event Rule at 9:00 AM UTC daily

**Process**:
1. Lists all IAM users in the account
2. For each user, checks:
   - Last console login (PasswordLastUsed)
   - Last access key usage (GetAccessKeyLastUsed)
3. If both are older than `InactivityThresholdDays`:
   - Adds user to DynamoDB table
   - Sets TTL = current time + `GracePeriodDays`
   - **Immediately disables all access keys**
   - Sends SNS notification to the configured email

**Inactivity Detection Logic**:
```python
# User is considered inactive if:
# - Console password not used in X days AND
# - No access key used in X days
```

### 2. Grace Period (DynamoDB TTL)

**Storage**:
- Username (partition key)
- Flagged date
- Last activity date
- TTL timestamp
- Notification status

**Grace Period**:
- Users remain in the table for the configured grace period
- Access keys are already disabled to prevent further use
- Additional notifications can be sent during this period

### 3. Automated Deletion (Cleanup Lambda)

**Trigger**: DynamoDB Stream when TTL expires

**Process**:
1. Receives expired user record from DynamoDB Stream
2. Performs comprehensive IAM cleanup:
   - Removes user from all groups
   - Detaches all managed policies
   - Deletes all inline policies
   - Deletes all access keys
   - Deletes login profile (console password)
   - Deactivates and deletes MFA devices
   - Deletes SSH public keys
   - Deletes signing certificates
   - Finally deletes the IAM user
3. Sends summary notification via SNS

## 📧 Notifications

### User Flagged Notification

```
Subject: IAM User Inactive: john.doe

ALERT: IAM User Flagged for Inactivity

Username: john.doe
Flagged Date: 2025-02-07T09:00:00Z
Last Activity: 2024-11-08T14:23:45Z

ACTION REQUIRED:
This IAM user has been inactive for 90 days.
Access keys have been DISABLED immediately.

The user will be DELETED on: 2025-03-09 09:00:00 UTC

Grace Period: 30 days
```

### Deletion Notification

```
Subject: IAM Users Deleted - Cleanup Summary

IAM User Cleanup Summary

The following IAM users have been automatically deleted:
  - john.doe
  - jane.smith

Total deleted: 2

These users exceeded their grace period and have been removed.
```

## 🔍 Monitoring & Logs

### CloudWatch Logs

Two log groups are created:
- `/aws/lambda/{StackName}-InactiveUserScanner`
- `/aws/lambda/{StackName}-InactiveUserCleanup`

Retention: 30 days

### DynamoDB Table

Table name: `{StackName}-InactiveUsers`

Query to see flagged users:
```bash
aws dynamodb scan \
  --table-name iam-inactive-user-cleanup-InactiveUsers \
  --region us-east-1
```

## 🛡️ Security Best Practices

### Recommended Configuration

- **Production**: 90 days inactivity, 30 days grace
- **Strict**: 60 days inactivity, 14 days grace
- **Lenient**: 180 days inactivity, 60 days grace

### Service Accounts / Bot Users

For users that should never be deleted (service accounts, automation users):

**Option 1**: Tag-based exclusion (requires template modification)
```python
# Add to scanner Lambda
user_tags = iam.list_user_tags(UserName=username)
if any(tag['Key'] == 'DoNotDelete' for tag in user_tags['Tags']):
    continue  # Skip this user
```

**Option 2**: Separate OU/Account
- Keep service accounts in a different AWS account
- Only deploy this stack to accounts with human users

**Option 3**: Manual removal from DynamoDB
```bash
aws dynamodb delete-item \
  --table-name iam-inactive-user-cleanup-InactiveUsers \
  --key '{"username": {"S": "service-account-user"}}'
```

## 🧪 Testing

### Manual Scanner Invocation

```bash
# Trigger the scanner Lambda manually
aws lambda invoke \
  --function-name iam-inactive-user-cleanup-InactiveUserScanner \
  --region us-east-1 \
  response.json

cat response.json
```

### View Flagged Users

```bash
# Scan DynamoDB table
aws dynamodb scan \
  --table-name iam-inactive-user-cleanup-InactiveUsers \
  --region us-east-1
```

### Test Notification

```bash
# Publish test message to SNS
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:iam-inactive-user-cleanup-InactiveUserNotifications \
  --subject "Test Notification" \
  --message "This is a test"
```

## 🚨 Troubleshooting

### Users Not Being Flagged

**Check**:
1. Lambda execution logs in CloudWatch
2. IAM permissions for the Scanner Lambda role
3. Inactivity threshold configuration

**Common Issues**:
- Access key usage data may take up to 4 hours to update in IAM
- Console login requires a password (users with only access keys won't show PasswordLastUsed)

### Users Not Being Deleted

**Check**:
1. DynamoDB Streams are enabled
2. Cleanup Lambda has EventSourceMapping configured
3. TTL is enabled on the DynamoDB table
4. Cleanup Lambda execution logs

**Common Issues**:
- TTL deletion can take up to 48 hours after expiration
- Check DynamoDB Stream lag in CloudWatch metrics

### SNS Notifications Not Received

**Check**:
1. SNS subscription is confirmed (check email)
2. Email not in spam folder
3. SNS topic permissions

## 🔄 Updating the Stack

```bash
aws cloudformation update-stack \
  --stack-name iam-inactive-user-cleanup \
  --template-body file://iam-inactive-user-cleanup.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=60 \
    ParameterKey=GracePeriodDays,ParameterValue=14 \
    ParameterKey=NotificationEmail,UsePreviousValue=true \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

## 🗑️ Cleanup / Deletion

To remove the entire stack:

```bash
aws cloudformation delete-stack \
  --stack-name iam-inactive-user-cleanup \
  --region us-east-1
```

**Note**: This will:
- Delete all Lambda functions
- Delete the DynamoDB table (and all flagged user records)
- Delete the SNS topic
- Remove CloudWatch Event rules

## 📊 Costs

Estimated monthly costs (for account with 100 IAM users):

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| Lambda (Scanner) | 30 executions/month @ 100ms | < $0.01 |
| Lambda (Cleanup) | ~5 executions/month @ 200ms | < $0.01 |
| DynamoDB | On-demand, ~10 items | < $0.10 |
| SNS | ~35 notifications/month | < $0.01 |
| CloudWatch Logs | 30-day retention | < $0.50 |
| **Total** | | **< $1.00/month** |

## 🔐 IAM Permissions Required for Deployment

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "sns:CreateTopic",
        "sns:Subscribe",
        "events:PutRule",
        "events:PutTargets",
        "logs:CreateLogGroup"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🎯 Future Enhancements

Potential improvements:
- [ ] Slack/Teams integration for notifications
- [ ] Tag-based exclusion for service accounts
- [ ] Multi-region support
- [ ] Custom notification templates
- [ ] Reactivation workflow
- [ ] Dashboard for monitoring flagged users
- [ ] Integration with AWS Organizations for multi-account scanning

## 📝 License

This CloudFormation template is provided as-is for educational and operational purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK**: This automation will permanently delete IAM users and their credentials. Ensure you:
1. Test in a non-production environment first
2. Configure appropriate grace periods
3. Have a recovery plan for mistakenly deleted users
4. Review the flagged users before they're deleted
5. Maintain proper backups and audit logs

**This is a powerful security tool that should be deployed with careful consideration of your organization's needs.**
