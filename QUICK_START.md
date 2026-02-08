# Quick Start Guide

Get up and running with AWS SecOps Tools in 5 minutes!

## 🚀 Prerequisites

Before you begin, ensure you have:

- ✅ AWS Account with admin access
- ✅ [AWS CLI](https://aws.amazon.com/cli/) installed and configured
- ✅ Python 3.12 or higher
- ✅ Git installed
- ✅ Basic knowledge of CloudFormation and AWS services

## 📥 Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-secops-tools.git
cd aws-secops-tools

# Or if you're setting up your own:
mkdir aws-secops-tools
cd aws-secops-tools
# Copy files from this download
```

## 🔧 Step 2: Run Setup (Optional)

The setup script will validate your environment and optionally deploy a test stack:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Check prerequisites (AWS CLI, Python, git)
- ✅ Validate AWS credentials
- ✅ Create Python virtual environment
- ✅ Install dependencies
- ✅ Validate CloudFormation templates
- ✅ Set up git hooks
- ✅ Optionally deploy a test stack

## 🎯 Step 3: Deploy Your First Tool

### IAM Inactive User Cleanup

**Quick Deploy to Test Environment:**

```bash
cd iam-inactive-user-cleanup

# Validate the template
aws cloudformation validate-template \
  --template-body file://cloudformation/template.yaml

# Deploy with test parameters
aws cloudformation create-stack \
  --stack-name iam-cleanup-test \
  --template-body file://cloudformation/template.yaml \
  --parameters file://cloudformation/parameters/dev.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Monitor deployment
aws cloudformation describe-stacks \
  --stack-name iam-cleanup-test \
  --query 'Stacks[0].StackStatus'
```

**Watch the deployment:**
```bash
aws cloudformation wait stack-create-complete \
  --stack-name iam-cleanup-test

echo "Stack deployed successfully!"
```

## 📧 Step 4: Confirm SNS Subscription

**CRITICAL**: Check your email inbox!

1. You'll receive an email: "AWS Notification - Subscription Confirmation"
2. Click "Confirm subscription"
3. You should see: "Subscription confirmed!"

## ✅ Step 5: Validate the Deployment

```bash
# Run validation script
python3 scripts/test_iam_cleanup.py \
  --stack-name iam-cleanup-test \
  --validate

# Check current IAM user status
python3 scripts/test_iam_cleanup.py \
  --stack-name iam-cleanup-test \
  --check-users

# Send a test notification
python3 scripts/test_iam_cleanup.py \
  --stack-name iam-cleanup-test \
  --test-notification
```

## 🧪 Step 6: Test the Automation

### Trigger a Manual Scan

```bash
# Manually invoke the scanner Lambda
python3 scripts/test_iam_cleanup.py \
  --stack-name iam-cleanup-test \
  --scan

# Check if any users were flagged
python3 scripts/test_iam_cleanup.py \
  --stack-name iam-cleanup-test \
  --list-flagged
```

### View CloudWatch Logs

```bash
# Tail Scanner Lambda logs
aws logs tail /aws/lambda/iam-cleanup-test-InactiveUserScanner --follow

# Tail Cleanup Lambda logs
aws logs tail /aws/lambda/iam-cleanup-test-InactiveUserCleanup --follow
```

## 📊 Step 7: Monitor the Stack

### Check Stack Resources

```bash
# List all resources
aws cloudformation describe-stack-resources \
  --stack-name iam-cleanup-test

# Get stack outputs
aws cloudformation describe-stacks \
  --stack-name iam-cleanup-test \
  --query 'Stacks[0].Outputs'
```

### Check DynamoDB Table

```bash
# Scan the table for flagged users
aws dynamodb scan \
  --table-name iam-cleanup-test-InactiveUsers \
  --output table
```

## 🎓 Step 8: Learn More

Now that you have a working deployment, explore:

1. **Full Documentation**: Read `iam-inactive-user-cleanup/README.md`
2. **Deployment Guide**: See `iam-inactive-user-cleanup/DEPLOYMENT_GUIDE.md`
3. **Troubleshooting**: Check `iam-inactive-user-cleanup/docs/troubleshooting.md`
4. **Examples**: Review `iam-inactive-user-cleanup/examples/deployment-examples.sh`

## 🏭 Step 9: Deploy to Production

Once tested, deploy to production:

```bash
# Update parameters for production
aws cloudformation create-stack \
  --stack-name iam-cleanup-prod \
  --template-body file://cloudformation/template.yaml \
  --parameters file://cloudformation/parameters/prod.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --tags \
    Key=Environment,Value=Production \
    Key=ManagedBy,Value=CloudFormation
```

**Don't forget to:**
- ✅ Confirm SNS subscription for production email
- ✅ Adjust parameters for your security requirements
- ✅ Review and exclude service accounts
- ✅ Set up monitoring and alerting

## 🧹 Step 10: Clean Up (Optional)

To remove the test deployment:

```bash
# Delete the stack
aws cloudformation delete-stack \
  --stack-name iam-cleanup-test

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name iam-cleanup-test

echo "Test stack deleted!"
```

---

## 🆘 Common Issues

### "Stack already exists"
```bash
# Use a different stack name or delete the existing one
aws cloudformation delete-stack --stack-name iam-cleanup-test
```

### "Insufficient permissions"
```bash
# Verify your AWS credentials
aws sts get-caller-identity

# Ensure you have admin access or the required permissions
```

### "SNS subscription not confirmed"
```bash
# Resend confirmation
aws sns subscribe \
  --topic-arn <TOPIC_ARN_FROM_OUTPUTS> \
  --protocol email \
  --notification-endpoint your-email@example.com
```

### "No users being flagged"
```bash
# Lower the threshold for testing
aws cloudformation update-stack \
  --stack-name iam-cleanup-test \
  --use-previous-template \
  --parameters \
    ParameterKey=InactivityThresholdDays,ParameterValue=1 \
    ParameterKey=GracePeriodDays,UsePreviousValue=true \
    ParameterKey=NotificationEmail,UsePreviousValue=true
```

---

## 📚 Next Steps

### For Security Teams
1. Review flagged users weekly
2. Set up CloudWatch dashboards
3. Integrate with SIEM/logging tools
4. Create runbooks for exceptions

### For Developers
1. Explore the Lambda code
2. Customize notifications
3. Add new features (see CONTRIBUTING.md)
4. Submit improvements via PR

### For Compliance
1. Document the automation in compliance artifacts
2. Set up audit reports
3. Integrate with compliance tools
4. Track user lifecycle in ticketing systems

---

## 🎯 Success Checklist

- [ ] AWS CLI configured and working
- [ ] CloudFormation stack deployed successfully
- [ ] SNS subscription confirmed
- [ ] Test notification received
- [ ] Manual scan executed
- [ ] CloudWatch Logs accessible
- [ ] DynamoDB table visible
- [ ] Documentation reviewed
- [ ] Production deployment planned

---

## 💡 Pro Tips

1. **Start with a long grace period** (60+ days) initially
2. **Test in a sandbox account** before production
3. **Tag service accounts** to exclude them
4. **Set up CloudWatch alarms** for Lambda errors
5. **Document your exceptions** (service accounts, etc.)
6. **Review flagged users** before the grace period expires
7. **Keep CloudFormation parameters** in version control

---

**Need Help?** 
- 📖 Check the [troubleshooting guide](iam-inactive-user-cleanup/docs/troubleshooting.md)
- 🐛 [Open an issue](https://github.com/yourusername/aws-secops-tools/issues)
- 💬 [Start a discussion](https://github.com/yourusername/aws-secops-tools/discussions)

**Ready to contribute?**
- 🤝 Read [CONTRIBUTING.md](CONTRIBUTING.md)
- ✨ Submit feature requests
- 🐛 Report bugs
- 📖 Improve documentation

---

**That's it! You're now securing your AWS environment with automation! 🔒**
