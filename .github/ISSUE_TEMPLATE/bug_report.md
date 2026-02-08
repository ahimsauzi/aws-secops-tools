---
name: Bug Report
about: Report a bug or issue with an AWS SecOps tool
title: '[BUG] '
labels: bug
assignees: ''

---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔧 Tool Affected
- [ ] IAM Inactive User Cleanup
- [ ] Other (specify):

## 📋 To Reproduce
Steps to reproduce the behavior:
1. Deploy CloudFormation stack with parameters '...'
2. Execute command '...'
3. Check CloudWatch Logs '...'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## ❌ Actual Behavior
What actually happened instead.

## 🌍 Environment
**AWS Environment:**
- AWS Region: [e.g., us-east-1]
- Account Type: [e.g., Organization Member, Standalone]
- IAM Users Count: [e.g., 50]

**Deployment Details:**
- CloudFormation Stack Name: [e.g., iam-cleanup-prod]
- Parameters Used:
  ```json
  {
    "InactivityThresholdDays": 90,
    "GracePeriodDays": 30,
    "NotificationEmail": "security@example.com"
  }
  ```

**Tool Versions:**
- AWS CLI Version: [e.g., 2.9.0]
- Python Version: [e.g., 3.12.1]

## 📊 CloudWatch Logs
Provide relevant log snippets (SANITIZE account IDs and sensitive data):

```
[2025-02-07 10:30:15] ERROR: Failed to delete user...
```

## 🖼️ Screenshots
If applicable, add screenshots to help explain your problem.

## 🔍 Additional Context
Add any other context about the problem here.

**CloudFormation Events:**
```bash
# Output from: aws cloudformation describe-stack-events --stack-name <stack-name>
```

**DynamoDB Table Status:**
```bash
# Output from: aws dynamodb describe-table --table-name <table-name>
```

## ✔️ Checklist
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have tested in a non-production environment
- [ ] I have reviewed the troubleshooting documentation
- [ ] I have sanitized all sensitive information (account IDs, emails, etc.)
- [ ] I have included relevant logs and error messages

## 🆘 Severity
- [ ] Critical - Production system down
- [ ] High - Major feature broken
- [ ] Medium - Feature partially broken
- [ ] Low - Minor issue or cosmetic

---

**Note:** For security vulnerabilities, please DO NOT open a public issue. Email security@yourcompany.com instead.
