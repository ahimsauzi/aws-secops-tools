# Pull Request

## 📋 Description
<!-- Provide a brief description of the changes in this PR -->

## 🔧 Type of Change
<!-- Mark the relevant option with an 'x' -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature/tool (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📖 Documentation update
- [ ] 🧪 Test improvement
- [ ] 🔧 Configuration change
- [ ] ♻️ Code refactoring

## 🎯 Related Issue
<!-- Link to the related issue -->
Fixes #(issue number)

## 📝 Changes Made
<!-- Provide a detailed list of changes -->

- 
- 
- 

## 🧪 Testing Performed

### CloudFormation Testing
- [ ] Template validated with `aws cloudformation validate-template`
- [ ] Stack deployed successfully in test account
- [ ] All resources created as expected
- [ ] Stack outputs are correct
- [ ] Stack deletes cleanly

**Test Account Details:**
- Region: 
- Stack Name: 
- Parameters: 
  ```json
  {
    "InactivityThresholdDays": X,
    "GracePeriodDays": Y
  }
  ```

### Functionality Testing
- [ ] Feature works as described
- [ ] No errors in CloudWatch Logs
- [ ] Notifications sent correctly
- [ ] Edge cases handled

**Test Results:**
```
# Paste relevant test output
```

### Python Script Testing
- [ ] Script runs without errors
- [ ] All functions work as expected
- [ ] Error handling works correctly
- [ ] Help/usage documentation is clear

**Python Version:** 3.12
**boto3 Version:** 

### Documentation Testing
- [ ] README is accurate and clear
- [ ] Code examples work as shown
- [ ] Troubleshooting steps are helpful
- [ ] All links are valid

## 📸 Screenshots/Logs
<!-- If applicable, add screenshots or log snippets (SANITIZE sensitive data) -->

### CloudFormation Stack Output
```yaml
# Stack create/update output
```

### Lambda Execution Results
```
# CloudWatch Logs snippets
```

## ✅ Checklist
<!-- Verify all items before submitting -->

### Code Quality
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] No secrets or credentials are hardcoded

### Testing
- [ ] I have tested this in a non-production AWS account
- [ ] I have tested edge cases and error scenarios
- [ ] All existing tests still pass
- [ ] I have added tests that prove my fix is effective or that my feature works

### Documentation
- [ ] I have updated the README.md (if applicable)
- [ ] I have updated the DEPLOYMENT_GUIDE.md (if applicable)
- [ ] I have added/updated code comments
- [ ] I have added usage examples
- [ ] I have updated the troubleshooting guide (if applicable)

### CloudFormation Specific
- [ ] Template follows AWS best practices
- [ ] IAM policies follow least privilege principle
- [ ] Resources are properly tagged
- [ ] Parameters have clear descriptions
- [ ] Outputs are properly defined
- [ ] Resource names follow naming conventions

### Security
- [ ] No sensitive data (credentials, account IDs) in code
- [ ] IAM policies are least-privilege
- [ ] Security best practices followed
- [ ] No introduction of security vulnerabilities

## 💰 Cost Impact
<!-- Estimate the cost impact of this change -->

**Monthly Cost Estimate:**
- Before: $X.XX
- After: $X.XX
- Change: +/- $X.XX

**Justification:** 

## 🔄 Deployment Notes
<!-- Any special deployment considerations? -->

**Breaking Changes:**
- 

**Migration Steps:**
```bash
# Commands needed to update existing deployments
```

**Rollback Plan:**
```bash
# How to rollback if issues arise
```

## 📚 Additional Context
<!-- Add any other context about the PR here -->

### For New Tools:
- [ ] Tool directory structure follows convention
- [ ] CloudFormation template in `cloudformation/` directory
- [ ] Test scripts in `scripts/` directory
- [ ] Examples in `examples/` directory
- [ ] Documentation in `docs/` directory
- [ ] Main README updated with new tool

### Architecture Diagram
```
<!-- If adding/changing architecture, include ASCII diagram -->
┌──────────┐
│ Service  │──> Lambda
└──────────┘
```

## 🙏 Reviewer Notes
<!-- Anything specific you want reviewers to focus on? -->



---

## 📝 Post-Merge Checklist
<!-- To be completed after merge -->
- [ ] Update CHANGELOG.md
- [ ] Tag release if applicable
- [ ] Update documentation site
- [ ] Announce in discussions/Discord
- [ ] Close related issues

---

**By submitting this PR, I confirm:**
- I have read and agree to the project's Contributing Guidelines
- My contributions are my own work
- I agree to license my contributions under the MIT License
