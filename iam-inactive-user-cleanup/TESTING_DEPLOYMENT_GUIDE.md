# IAM Inactive User Cleanup - Testing Deployment Guide

This guide walks you through deploying the IAM Inactive User Cleanup solution to a test AWS account with short thresholds for faster testing.

## Quick Start Summary

1. **Tag your protected user** (`sec-admin`)
2. **Deploy CloudFormation stack** with testing parameters
3. **Confirm SNS subscription** in your email
4. **Validate deployment** with test script
5. **Manually trigger a scan** to test exclusions
6. **Monitor results**

---

## Prerequisites

✅ **AWS CLI configured** with credentials for your test account  
✅ **Valid email address**: `uzi@amazon.com`  
✅ **IAM user to protect**: `sec-admin`  
✅ **AWS region selected**: (e.g., `us-east-1`)

---

## Step 0: Generate Test Users (Optional but Recommended)

**Purpose**: Create dummy IAM users to test the automation without affecting real users.

**Best Practice**: Run this in **AWS CloudShell** BEFORE deploying the stack.

### Why Generate Test Users?

- **Safe Testing**: Test without risking real user accounts
- **Immediate Results**: Newly created users have no activity and will be flagged instantly
- **Multiple Scenarios**: Test both flagging and exclusion logic
- **Easy Cleanup**: Remove all test users with one command

### Option 1: Using AWS CloudShell (Recommended)

**Step-by-step:**

1. **Open AWS CloudShell** in your AWS Console (icon in top toolbar)

2. **Upload the script** (or copy-paste the code):
   ```bash
   # Option A: Upload from your machine
   # Click Actions > Upload File > Select generate_test_users.py
   
   # Option B: Create the file directly
   cat > generate_test_users.py << 'EOF'
   # [Paste the entire script content from generate_test_users.py]
   EOF
   ```

3. **Preview what will be created** (dry run):
   ```bash
   python3 generate_test_users.py --dry-run
   ```
   
   **Expected Output:**
   ```
   🚀 Generating Test IAM Users
   ======================================================================
   🔍 DRY RUN MODE - No users will actually be created
   
   📋 Scenario: Inactive users with no credentials (should be flagged)
   ----------------------------------------------------------------------
     [DRY RUN] Would create: test-iam-cleanup-inactive-no-creds-1
     [DRY RUN] Would create: test-iam-cleanup-inactive-no-creds-2
     ...
   ```

4. **Create the test users**:
   ```bash
   python3 generate_test_users.py --create
   ```
   
   **Expected Output:**
   ```
   🚀 Generating Test IAM Users
   ======================================================================
   
   📋 Scenario: Inactive users with no credentials (should be flagged)
   ----------------------------------------------------------------------
     ✅ Created: test-iam-cleanup-inactive-no-creds-1
     ✅ Created: test-iam-cleanup-inactive-no-creds-2
     ...
   
   ======================================================================
   ✅ SUCCESS - Created 10 test users
   ======================================================================
   
   📊 Expected Behavior:
   ----------------------------------------------------------------------
   When you deploy the CloudFormation stack and run a scan:
     • 7 users should be FLAGGED for deletion
     • 2 users should be EXCLUDED (protected)
     • 1 user may not be flagged yet (recently created)
   ```

5. **List created users** to verify:
   ```bash
   python3 generate_test_users.py --list
   ```

### Option 2: Using Local Terminal

If you prefer to run locally with AWS CLI configured:

```bash
# Navigate to the scripts directory
cd iam-inactive-user-cleanup/scripts

# Preview
python3 generate_test_users.py --dry-run

# Create users
python3 generate_test_users.py --create

# List users
python3 generate_test_users.py --list
```

### Test User Scenarios Created

The script creates **10 test users** across 4 scenarios:

| Count | Username Pattern | Scenario | Expected Behavior |
|-------|-----------------|----------|-------------------|
| 5 | `test-iam-cleanup-inactive-no-creds-{1-5}` | No credentials | Should be flagged |
| 2 | `test-iam-cleanup-inactive-with-keys-{1-2}` | Has access keys | Should be flagged + keys disabled |
| 2 | `test-iam-cleanup-protected-{1-2}` | Has exclusion tag | Should NOT be flagged |
| 1 | `test-iam-cleanup-active-recent-1` | Recently created | May not be flagged initially |

### Understanding "Inactive" for Test Users

**Important**: Newly created users are considered **infinitely inactive** because:
- They have no password last used date
- They have no access key last used date
- The scanner treats "never used" as more inactive than any threshold
- This is **perfect for testing** - no need to wait!

### When to Skip This Step

Skip test user generation if:
- You already have inactive users in your account you want to test with
- You're deploying directly to production (not recommended)
- You prefer to test with real user scenarios only

**If you skip this step**, ensure you have users that meet the inactivity criteria (7+ days for testing parameters).

---

## Step 1: Tag Your Protected User

**IMPORTANT: Do this BEFORE deploying the stack!**

This ensures your user (`sec-admin`) is excluded from cleanup from the start.

```bash
# Tag the sec-admin user for exclusion
aws iam tag-user \
  --user-name sec-admin \
  --tags Key=IAMCleanupExclude,Value=true

# Verify the tag was applied
aws iam list-user-tags --user-name sec-admin
```

**Expected Output:**
```json
{
    "Tags": [
        {
            "Key": "IAMCleanupExclude",
            "Value": "true"
        }
    ]
}
```

---

## Step 2: Deploy CloudFormation Stack

### Option A: Using AWS CLI (Recommended)

```bash
# Navigate to the cloudformation directory
cd iam-inactive-user-cleanup/cloudformation

# Deploy the stack with testing parameters
aws cloudformation create-stack \
  --stack-name iam-inactive-user-cleanup-test \
  --template-body file://template.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=7 \
    ParameterKey=GracePeriodDays,ParameterValue=1 \
    ParameterKey=NotificationEmail,ParameterValue=uzi@amazon.com \
    ParameterKey=ExclusionTagKey,ParameterValue=IAMCleanupExclude \
    ParameterKey=ExclusionTagValue,ParameterValue=true \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Wait for stack creation to complete (takes ~2-3 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name iam-inactive-user-cleanup-test \
  --region us-east-1

# Check stack status
aws cloudformation describe-stacks \
  --stack-name iam-inactive-user-cleanup-test \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus'
```

### Option B: Using AWS Console

1. Open AWS CloudFormation console
2. Click **Create Stack** → **With new resources**
3. Upload `template.yaml`
4. Configure parameters:
   - **Stack name**: `iam-inactive-user-cleanup-test`
   - **InactivityThresholdDays**: `7`
   - **GracePeriodDays**: `1`
   - **NotificationEmail**: `uzi@amazon.com`
   - **ExclusionTagKey**: `IAMCleanupExclude` (default)
   - **ExclusionTagValue**: `true` (default)
5. Check **I acknowledge that AWS CloudFormation might create IAM resources**
6. Click **Create stack**

---

## Step 3: Confirm SNS Subscription

🔔 **Check your email** (`uzi@amazon.com`) for an SNS subscription confirmation.

**Subject**: `AWS Notification - Subscription Confirmation`

Click the **Confirm subscription** link in the email.

**Verify subscription**:
```bash
aws sns list-subscriptions-by-topic \
  --topic-arn $(aws cloudformation describe-stacks \
    --stack-name iam-inactive-user-cleanup-test \
    --query 'Stacks[0].Outputs[?OutputKey==`SNSTopicArn`].OutputValue' \
    --output text) \
  --region us-east-1
```

---

✅ PASS - Stack Exists
✅ PASS - DynamoDB Table
✅ PASS - Scanner Lambda
✅ PASS - Cleanup Lambda
✅ PASS - SNS Topic
✅ PASS - DynamoDB Streams
✅ PASS - CloudWatch Event Rule

✅ All checks passed!
```
## Step 4: Validate Deployment

Run the validation script to ensure all resources are properly configured.

### Option 1: Using AWS CloudShell (Recommended)

**If you're already using CloudShell from Step 0:**

1. **Upload the validation script**:
   - In CloudShell, click **Actions** → **Upload File**
   - Select `test_iam_cleanup.py` from `iam-inactive-user-cleanup/scripts/` on your machine

2. **Run the validation**:
   ```bash
   python3 test_iam_cleanup.py \
     --stack-name iam-inactive-user-cleanup-test \
     --validate
   ```

### Option 2: Using Local Terminal

If running from your local machine:

```bash
# From the project root
python3 iam-inactive-user-cleanup/scripts/test_iam_cleanup.py \
  --stack-name iam-inactive-user-cleanup-test \
  --validate
```

### Expected Output (Both Options)

```
🔍 Validating CloudFormation Stack Deployment...
✅ PASS - Stack Exists
✅ PASS - DynamoDB Table
✅ PASS - Scanner Lambda
✅ PASS - Cleanup Lambda
✅ PASS - SNS Topic
✅ PASS - DynamoDB Streams
✅ PASS - CloudWatch Event Rule

✅ All checks passed!
```
============================================================
✅ PASS - Stack Exists
✅ PASS - DynamoDB Table
✅ PASS - Scanner Lambda
✅ PASS - Cleanup Lambda
✅ PASS - SNS Topic
✅ PASS - DynamoDB Streams
✅ PASS - CloudWatch Event Rule
============================================================

✅ All checks passed!
```

---

## Step 5: Check IAM User Activity Status

Before triggering a scan, check which users would be flagged:

```bash
python3 iam-inactive-user-cleanup/scripts/test_iam_cleanup.py \
  --stack-name iam-inactive-user-cleanup-test \
  --check-users
```

**This shows**:
- Total IAM users in the account
- Users inactive for 7+ days
- Days since last activity for each user
- **Note**: `sec-admin` may appear here, but will be excluded during the scan due to the tag

---

## Step 6: Manually Trigger a Scan

Test the automation by manually triggering the Scanner Lambda:

```bash
python3 iam-inactive-user-cleanup/scripts/test_iam_cleanup.py \
  --stack-name iam-inactive-user-cleanup-test \
  --scan
```

**Expected Output:**
```
🚀 Triggering Manual Scan...
============================================================
✅ Scan completed successfully!

Results:
  Total Inactive Users: 2
  Newly Flagged: 2
  Users: test-user-1, test-user-2
```

**Important**: `sec-admin` should NOT appear in the flagged users list!

---

## Step 7: Verify Exclusion Works

Check the Scanner Lambda logs to confirm `sec-admin` was excluded:

```bash
# View recent logs
aws logs tail /aws/lambda/iam-inactive-user-cleanup-test-InactiveUserScanner \
  --since 5m \
  --follow \
  --region us-east-1
```

**Look for this log entry**:
```
User sec-admin excluded via tag IAMCleanupExclude=true
```

---

## Step 8: List Flagged Users

View all users currently flagged for deletion:

```bash
python3 iam-inactive-user-cleanup/scripts/test_iam_cleanup.py \
  --stack-name iam-inactive-user-cleanup-test \
  --list-flagged
```

**Expected Output:**
```
📋 Currently Flagged Users:
============================================================

User: test-user-1
  Flagged: 2026-02-11T18:30:00Z
  Deletion: 2026-02-12 18:30:00 UTC
  Last Activity: 2025-12-15T10:23:45Z
  Keys Disabled: True
```

**Verify**: `sec-admin` is NOT in this list!

---

## Step 9: Test Notification

Send a test notification to verify SNS is working:

```bash
python3 iam-inactive-user-cleanup/scripts/test_iam_cleanup.py \
  --stack-name iam-inactive-user-cleanup-test \
  --test-notification
```

Check your email for the test notification.

---

## Understanding Testing Parameters

### Current Configuration

| Parameter | Value | Production Value | Explanation |
|-----------|-------|------------------|-------------|
| **Inactivity Threshold** | 7 days | 90 days | Users inactive for 7+ days will be flagged |
| **Grace Period** | 1 day | 30 days | Users deleted 1 day after flagging |
| **Scan Schedule** | 9 AM UTC daily | 9 AM UTC daily | Runs automatically every day |

### Testing Timeline

```
Day 0: Deploy stack + Tag sec-admin
Day 0: Manual scan identifies inactive users
Day 0: Users flagged, access keys disabled, notification sent
Day 1: TTL expires, users automatically deleted
```

**Fast testing!** Much quicker than waiting 90+ days.

---

## Monitoring & Troubleshooting

### View CloudWatch Logs

**Scanner Lambda:**
```bash
aws logs tail /aws/lambda/iam-inactive-user-cleanup-test-InactiveUserScanner \
  --follow --region us-east-1
```

**Cleanup Lambda:**
```bash
aws logs tail /aws/lambda/iam-inactive-user-cleanup-test-InactiveUserCleanup \
  --follow --region us-east-1
```

### Check DynamoDB Table

```bash
aws dynamodb scan \
  --table-name iam-inactive-user-cleanup-test-InactiveUsers \
  --region us-east-1
```

### View Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name iam-inactive-user-cleanup-test \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

---

## Additional Users to Exclude

If you need to exclude additional users, simply tag them:

```bash
# Tag another user for exclusion
aws iam tag-user \
  --user-name service-account \
  --tags Key=IAMCleanupExclude,Value=true

# Verify
aws iam list-user-tags --user-name service-account
```

The next scan will automatically exclude these users.

---

## Cleanup / Removal

When testing is complete, follow these steps to clean up all resources:

### Step 1: Delete Test Users (if you created them)

If you generated test users in Step 0, delete them first:

```bash
# Preview which test users will be deleted
python3 generate_test_users.py --cleanup

# Actually delete them (requires --confirm flag)
python3 generate_test_users.py --cleanup --confirm
```

**Expected Output:**
```
🗑️  Cleanup Test IAM Users

Found 10 test user(s) to delete:
  • test-iam-cleanup-inactive-no-creds-1
  • test-iam-cleanup-inactive-no-creds-2
  ...

🚨 PROCEEDING WITH DELETION...

  ├─ Deleted access key for test-iam-cleanup-inactive-with-keys-1
  ✅ Deleted user: test-iam-cleanup-inactive-with-keys-1
  ...

✅ Deleted 10 of 10 test users
```

**Note**: The script automatically removes access keys before deleting users.

### Step 2: Delete the CloudFormation Stack

```bash
# Delete the CloudFormation stack
aws cloudformation delete-stack \
  --stack-name iam-inactive-user-cleanup-test \
  --region us-east-1

# Wait for deletion to complete (takes ~2-3 minutes)
aws cloudformation wait stack-delete-complete \
  --stack-name iam-inactive-user-cleanup-test \
  --region us-east-1
```

**This will delete**:
- Lambda functions
- DynamoDB table (and all flagged user records)
- SNS topic and subscriptions
- CloudWatch Event rules and log groups
- IAM roles

### Step 3: Remove Protection Tags (Optional)

Remove tags from users that were protected during testing:

```bash
# Remove tag from sec-admin
aws iam untag-user \
  --user-name sec-admin \
  --tag-keys IAMCleanupExclude

# Verify tag was removed
aws iam list-user-tags --user-name sec-admin
```

### Verify Complete Cleanup

Confirm all resources are deleted:

```bash
# Check for any remaining test users
aws iam list-users --query 'Users[?starts_with(UserName, `test-iam-cleanup-`)].UserName' --output table

# Verify stack is deleted
aws cloudformation describe-stacks \
  --stack-name iam-inactive-user-cleanup-test \
  --region us-east-1 2>&1 | grep -q "does not exist" && echo "✅ Stack deleted" || echo "❌ Stack still exists"
```

---

## Production Deployment

When ready for production, update parameters:

```bash
aws cloudformation update-stack \
  --stack-name iam-inactive-user-cleanup-prod \
  --template-body file://template.yaml \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=90 \
    ParameterKey=GracePeriodDays,ParameterValue=30 \
    ParameterKey=NotificationEmail,ParameterValue=security-team@amazon.com \
    ParameterKey=ExclusionTagKey,UsePreviousValue=true \
    ParameterKey=ExclusionTagValue,UsePreviousValue=true \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

---

## Key Features Summary

✅ **Tag-Based Exclusion**: Users with `IAMCleanupExclude=true` tag are automatically excluded  
✅ **Federated Users**: Automatically excluded (they use IAM Roles, not IAM Users)  
✅ **Short Testing Thresholds**: 7-day inactivity, 1-day grace period for fast testing  
✅ **Immediate Access Revocation**: Access keys disabled as soon as user is flagged  
✅ **Email Notifications**: Alerts when users are flagged and deleted  
✅ **Automated Cleanup**: TTL-based deletion via DynamoDB Streams  

---

## Next Steps

1. ✅ **Deploy stack** following this guide
2. ✅ **Validate** everything works
3. ✅ **Monitor** for 24-48 hours
4. 🔄 **Create unit tests** for Lambda functions (optional)
5. 📝 **Document** any custom exclusion rules for your team
6. 🚀 **Deploy to production** with updated thresholds

---

## Support & Troubleshooting

If you encounter issues:

1. **Check CloudWatch Logs** - Most issues show up in Lambda logs
2. **Review validation output** - Identifies misconfigured resources
3. **Verify SNS subscription** - Confirm email subscription is active
4. **Check IAM permissions** - Ensure Lambda roles have required permissions
5. **Review** `iam-inactive-user-cleanup/docs/troubleshooting.md`

---

**Happy Testing! 🎉**
