# Troubleshooting Guide

Common issues and solutions for IAM Inactive User Cleanup automation.

## Table of Contents

- [Deployment Issues](#deployment-issues)
- [Scanner Lambda Issues](#scanner-lambda-issues)
- [Cleanup Lambda Issues](#cleanup-lambda-issues)
- [DynamoDB Issues](#dynamodb-issues)
- [SNS Notification Issues](#sns-notification-issues)
- [IAM Permission Issues](#iam-permission-issues)
- [Performance Issues](#performance-issues)

---

## Deployment Issues

### Stack Creation Fails

**Symptom**: CloudFormation stack fails with `CREATE_FAILED` status

**Possible Causes & Solutions**:

1. **Insufficient IAM Permissions**
   ```bash
   # Check your current permissions
   aws iam get-user
   
   # Verify you can create the required resources
   aws cloudformation validate-template \
     --template-body file://cloudformation/template.yaml
   ```
   **Solution**: Ensure you have `CAPABILITY_NAMED_IAM` and permissions to create Lambda, DynamoDB, SNS, IAM roles.

2. **Stack Name Already Exists**
   ```bash
   # Check existing stacks
   aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
   ```
   **Solution**: Use a different stack name or delete the existing stack.

3. **Invalid Parameter Values**
   ```
   Parameter validation failed: Parameter value X is invalid
   ```
   **Solution**: Check parameter constraints:
   - `InactivityThresholdDays`: 1-365
   - `GracePeriodDays`: 1-90
   - `NotificationEmail`: Valid email format

### SNS Subscription Not Created

**Symptom**: No subscription confirmation email received

**Diagnostics**:
```bash
# Check SNS topic
aws sns list-topics | grep InactiveUser

# Check subscriptions
aws sns list-subscriptions-by-topic \
  --topic-arn <TOPIC_ARN>
```

**Solutions**:
1. Check spam/junk folder
2. Verify email address is correct
3. Manually subscribe:
   ```bash
   aws sns subscribe \
     --topic-arn <TOPIC_ARN> \
     --protocol email \
     --notification-endpoint your-email@example.com
   ```

---

## Scanner Lambda Issues

### Users Not Being Flagged

**Symptom**: Lambda runs successfully but no users are flagged

**Diagnostics**:
```bash
# Check Lambda logs
aws logs tail /aws/lambda/{STACK_NAME}-InactiveUserScanner --follow

# Manually invoke Lambda to see output
aws lambda invoke \
  --function-name {STACK_NAME}-InactiveUserScanner \
  --log-type Tail \
  response.json && cat response.json
```

**Possible Causes**:

1. **All Users Are Active**
   - Check actual user activity:
     ```bash
     python3 scripts/test_iam_cleanup.py --check-users
     ```

2. **Threshold Too High**
   - Default is 90 days. Users might not be that old.
   - **Solution**: Lower threshold temporarily for testing:
     ```bash
     aws cloudformation update-stack \
       --stack-name {STACK_NAME} \
       --use-previous-template \
       --parameters \
         ParameterKey=InactivityThresholdDays,ParameterValue=30 \
         ParameterKey=GracePeriodDays,UsePreviousValue=true \
         ParameterKey=NotificationEmail,UsePreviousValue=true
     ```

3. **IAM Permissions Missing**
   - Lambda can't read IAM data
   - **Check**: CloudWatch Logs for permission errors
   - **Solution**: Verify Scanner Lambda role has these permissions:
     ```json
     {
       "Effect": "Allow",
       "Action": [
         "iam:ListUsers",
         "iam:GetUser",
         "iam:ListAccessKeys",
         "iam:GetAccessKeyLastUsed"
       ],
       "Resource": "*"
     }
     ```

4. **Access Key Last Used Data Lag**
   - AWS IAM can take up to 4 hours to update access key usage data
   - **Solution**: Wait and re-run scan

### Lambda Timeout

**Symptom**: Lambda execution times out (>300 seconds)

**Diagnostics**:
```bash
# Check execution duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value={STACK_NAME}-InactiveUserScanner \
  --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Maximum
```

**Solutions**:

1. **Too Many Users**
   - For accounts with 1000+ users, increase timeout:
     ```yaml
     ScannerLambdaFunction:
       Properties:
         Timeout: 600  # 10 minutes
     ```

2. **Implement Pagination**
   - Modify Lambda to process users in batches

3. **Increase Memory**
   - More memory = more CPU
     ```yaml
     ScannerLambdaFunction:
       Properties:
         MemorySize: 512  # Up from 256
     ```

### Access Keys Not Being Disabled

**Symptom**: Flagged users still have active access keys

**Diagnostics**:
```bash
# Check specific user
aws iam list-access-keys --user-name john.doe

# Check Lambda logs for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/{STACK_NAME}-InactiveUserScanner \
  --filter-pattern "Error disabling access keys"
```

**Solutions**:

1. **Permission Issues**
   - Lambda needs `iam:UpdateAccessKey` permission
   - Add to Scanner Lambda role

2. **User Doesn't Have Access Keys**
   - Console-only users won't have keys
   - This is normal - check logs to confirm

---

## Cleanup Lambda Issues

### Users Not Being Deleted

**Symptom**: TTL expired but user still exists

**Diagnostics**:
```bash
# Check DynamoDB TTL status
aws dynamodb describe-time-to-live \
  --table-name {STACK_NAME}-InactiveUsers

# Check DynamoDB Streams
aws dynamodb describe-table \
  --table-name {STACK_NAME}-InactiveUsers \
  --query 'Table.StreamSpecification'

# Check Event Source Mapping
aws lambda list-event-source-mappings \
  --function-name {STACK_NAME}-InactiveUserCleanup
```

**Possible Causes**:

1. **TTL Not Enabled**
   ```bash
   # Enable TTL
   aws dynamodb update-time-to-live \
     --table-name {STACK_NAME}-InactiveUsers \
     --time-to-live-specification Enabled=true,AttributeName=ttl
   ```

2. **TTL Delay (Up to 48 Hours)**
   - DynamoDB TTL is not immediate
   - **Solution**: Wait up to 48 hours after expiration

3. **Event Source Mapping Disabled**
   ```bash
   # Check status
   aws lambda list-event-source-mappings \
     --function-name {STACK_NAME}-InactiveUserCleanup
   
   # Enable if disabled
   aws lambda update-event-source-mapping \
     --uuid {EVENT_SOURCE_MAPPING_UUID} \
     --enabled
   ```

4. **Cleanup Lambda Errors**
   ```bash
   # Check logs
   aws logs tail /aws/lambda/{STACK_NAME}-InactiveUserCleanup --follow
   ```

### User Deletion Fails

**Symptom**: Lambda runs but user still exists, errors in logs

**Common Error Messages & Solutions**:

1. **"Cannot delete entity, must detach all policies first"**
   - Lambda might be missing some cleanup steps
   - **Manual Cleanup**:
     ```bash
     # Detach all policies
     aws iam list-attached-user-policies --user-name john.doe | \
       jq -r '.AttachedPolicies[].PolicyArn' | \
       xargs -I {} aws iam detach-user-policy --user-name john.doe --policy-arn {}
     
     # Remove from groups
     aws iam list-groups-for-user --user-name john.doe | \
       jq -r '.Groups[].GroupName' | \
       xargs -I {} aws iam remove-user-from-group --user-name john.doe --group-name {}
     
     # Delete user
     aws iam delete-user --user-name john.doe
     ```

2. **"DeleteConflict: Cannot delete entity, must delete login profile first"**
   - Lambda should handle this, but manual fix:
     ```bash
     aws iam delete-login-profile --user-name john.doe
     aws iam delete-user --user-name john.doe
     ```

3. **Permission Errors**
   - Cleanup Lambda needs extensive IAM permissions
   - Verify role has all required `iam:Delete*` permissions

---

## DynamoDB Issues

### Items Not Appearing in Table

**Symptom**: Scanner runs but DynamoDB table is empty

**Diagnostics**:
```bash
# Scan table
aws dynamodb scan --table-name {STACK_NAME}-InactiveUsers

# Check Scanner Lambda logs for write errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/{STACK_NAME}-InactiveUserScanner \
  --filter-pattern "Error"
```

**Solutions**:

1. **No Inactive Users**
   - Normal if all users are active
   
2. **DynamoDB Write Permission Missing**
   - Check Scanner Lambda role has `dynamodb:PutItem`

3. **Table Name Mismatch**
   - Check environment variable in Lambda:
     ```bash
     aws lambda get-function-configuration \
       --function-name {STACK_NAME}-InactiveUserScanner \
       --query 'Environment.Variables.TABLE_NAME'
     ```

### TTL Not Working

**Symptom**: Items past TTL still in table

**Diagnostics**:
```bash
# Check TTL configuration
aws dynamodb describe-time-to-live \
  --table-name {STACK_NAME}-InactiveUsers
```

**Expected Output**:
```json
{
  "TimeToLiveDescription": {
    "TimeToLiveStatus": "ENABLED",
    "AttributeName": "ttl"
  }
}
```

**Solutions**:

1. **TTL Not Enabled**
   ```bash
   aws dynamodb update-time-to-live \
     --table-name {STACK_NAME}-InactiveUsers \
     --time-to-live-specification Enabled=true,AttributeName=ttl
   ```

2. **Wait for Background Process**
   - TTL deletions happen within 48 hours
   - Not immediate

3. **TTL Value Format**
   - Must be Unix timestamp (epoch seconds)
   - Check an item:
     ```bash
     aws dynamodb get-item \
       --table-name {STACK_NAME}-InactiveUsers \
       --key '{"username": {"S": "john.doe"}}' \
       --query 'Item.ttl.N'
     ```

---

## SNS Notification Issues

### Not Receiving Emails

**Symptom**: Operations complete but no email notifications

**Diagnostics**:
```bash
# Check SNS topic
aws sns list-subscriptions-by-topic \
  --topic-arn {TOPIC_ARN}

# Test notification
aws sns publish \
  --topic-arn {TOPIC_ARN} \
  --subject "Test" \
  --message "Test notification"
```

**Solutions**:

1. **Subscription Not Confirmed**
   - Check email for confirmation link
   - Resend confirmation:
     ```bash
     aws sns subscribe \
       --topic-arn {TOPIC_ARN} \
       --protocol email \
       --notification-endpoint your-email@example.com
     ```

2. **Email in Spam/Junk**
   - Check spam folder
   - Add `no-reply@sns.amazonaws.com` to contacts

3. **SNS Permission Issues**
   - Lambda needs `sns:Publish` permission

4. **Topic ARN Incorrect**
   - Verify environment variable:
     ```bash
     aws lambda get-function-configuration \
       --function-name {STACK_NAME}-InactiveUserScanner \
       --query 'Environment.Variables.SNS_TOPIC_ARN'
     ```

---

## IAM Permission Issues

### "AccessDenied" Errors

**Symptom**: Lambda executions fail with permission errors

**Diagnostics**:
```bash
# Check CloudWatch Logs for specific permission errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/{STACK_NAME}-InactiveUserScanner \
  --filter-pattern "AccessDenied"
```

**Common Scenarios**:

1. **Scanner Lambda Missing Permissions**
   - Required: `iam:ListUsers`, `iam:GetUser`, `iam:ListAccessKeys`, `iam:GetAccessKeyLastUsed`
   
2. **Cleanup Lambda Missing Permissions**
   - Required: All `iam:Delete*` and `iam:Detach*` permissions
   
3. **Cross-Account Issues**
   - Lambda cannot delete users in other accounts
   - Deploy stack per account

**Solution**: Verify role policies match template

---

## Performance Issues

### High Costs

**Symptom**: AWS bill higher than expected

**Investigation**:
```bash
# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value={STACK_NAME}-InactiveUserScanner \
  --start-time $(date -u -d '1 month ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum

# Check DynamoDB read/write usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value={STACK_NAME}-InactiveUsers \
  --start-time $(date -u -d '1 month ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum
```

**Solutions**:

1. **Too Frequent Scanning**
   - Default is daily (9 AM UTC)
   - Change schedule if needed:
     ```yaml
     ScheduleExpression: 'cron(0 9 ? * MON *)'  # Weekly on Monday
     ```

2. **DynamoDB Over-Provisioned**
   - Use on-demand billing (already in template)
   
3. **CloudWatch Logs Retention**
   - Default 30 days
   - Reduce if needed

### Slow Execution

**Symptom**: Lambda takes too long to complete

**Optimization**:

1. **Batch Operations**
   - Process users in parallel (modify Lambda)
   
2. **Increase Memory**
   ```yaml
   MemorySize: 512  # More memory = more CPU
   ```

3. **Filter Users Earlier**
   - Skip service accounts, excluded users upfront

---

## Getting Help

If issues persist:

1. **Enable Debug Logging**
   - Add `print()` statements in Lambda code
   - Redeploy stack

2. **Check CloudWatch Insights**
   ```
   fields @timestamp, @message
   | filter @message like /ERROR/
   | sort @timestamp desc
   | limit 20
   ```

3. **Open GitHub Issue**
   - Include sanitized logs
   - Describe expected vs actual behavior
   - Provide CloudFormation parameters used

4. **AWS Support**
   - For AWS service-specific issues
   - Especially for DynamoDB TTL delays

---

## Quick Reference

### Useful Commands

```bash
# Validate deployment
python3 scripts/test_iam_cleanup.py --validate

# Manual scan
python3 scripts/test_iam_cleanup.py --scan

# Check logs
aws logs tail /aws/lambda/{STACK_NAME}-InactiveUserScanner --follow

# List flagged users
aws dynamodb scan --table-name {STACK_NAME}-InactiveUsers

# Remove user from tracking
aws dynamodb delete-item \
  --table-name {STACK_NAME}-InactiveUsers \
  --key '{"username": {"S": "username"}}'

# Disable automation temporarily
aws events disable-rule --name {STACK_NAME}-DailyScan
```

### Important ARNs and Names

Get from stack outputs:
```bash
aws cloudformation describe-stacks \
  --stack-name {STACK_NAME} \
  --query 'Stacks[0].Outputs'
```

---

**Still having issues? Check the logs first!** 90% of problems can be diagnosed from CloudWatch Logs.
