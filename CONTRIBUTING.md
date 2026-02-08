# Contributing to AWS SecOps Tools

First off, thank you for considering contributing to AWS SecOps Tools! 🎉

Following these guidelines helps communicate that you respect the time of the developers managing and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

## 🤔 What kinds of contributions are we looking for?

AWS SecOps Tools is an open source project and we love to receive contributions from our community! There are many ways to contribute:

- 🐛 **Bug reports and fixes**
- 🚀 **New security automation tools**
- 📖 **Documentation improvements**
- 💡 **Feature requests and enhancements**
- 🧪 **Testing and validation scripts**
- 🎨 **CloudFormation template improvements**

## 🚫 What we're NOT looking for

- Tools that are AWS-specific marketing materials
- Malicious code or security vulnerabilities
- Tools without proper documentation
- Untested or experimental code without clear warnings

## 📋 Ground Rules

### Responsibilities

- Ensure CloudFormation templates are tested and valid
- Create issues for any major changes and enhancements you wish to make
- Keep feature versions as small as possible, preferably one new feature per version
- Be welcoming to newcomers and encourage diverse new contributors
- Follow security best practices - never commit credentials or sensitive data
- Write clear, comprehensive documentation for all tools

### Code Standards

#### CloudFormation Templates

- Use YAML format (not JSON)
- Include meaningful descriptions for all resources
- Follow AWS CloudFormation best practices
- Include proper IAM policies with least privilege
- Add comprehensive parameter descriptions
- Use outputs for important resource ARNs
- Tag all resources appropriately

```yaml
# Good example
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${AWS::StackName}-data-bucket'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      Tags:
        - Key: Purpose
          Value: SecurityAutomation
```

#### Python Code

- Use Python 3.12+ features
- Follow PEP 8 style guide
- Include type hints where appropriate
- Write comprehensive docstrings
- Handle exceptions gracefully
- Add logging for debugging
- Include unit tests for complex logic

```python
# Good example
import boto3
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def get_inactive_users(threshold_days: int) -> List[Dict[str, str]]:
    """
    Retrieve list of IAM users inactive for more than threshold days.
    
    Args:
        threshold_days: Number of days to consider a user inactive
        
    Returns:
        List of dictionaries containing username and last activity date
        
    Raises:
        boto3.exceptions.Boto3Error: If AWS API call fails
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Failed to get inactive users: {str(e)}")
        raise
```

#### Documentation

- Use clear, concise language
- Include code examples
- Add architecture diagrams where helpful
- Document all parameters and outputs
- Provide troubleshooting sections
- Include cost estimates
- Add security considerations

## 🎯 Your First Contribution

Unsure where to begin contributing? You can start by looking through these issue labels:

- `good-first-issue` - Issues that should only require a few lines of code
- `help-wanted` - Issues that are a bit more involved
- `documentation` - Documentation improvements

**Working on your first Pull Request?** You can learn how from this free series:
[How to Contribute to an Open Source Project on GitHub](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github)

## 🚀 Getting Started

### For Small Changes

Small contributions such as fixing spelling errors can be submitted directly as pull requests.

### For Larger Changes

1. **Create an issue** describing your proposed changes
2. **Wait for feedback** from maintainers
3. **Fork the repository** and create your branch from `main`
4. **Make your changes** following our code standards
5. **Test thoroughly** in a non-production AWS account
6. **Update documentation** to reflect your changes
7. **Submit a pull request**

### Process for Adding a New Tool

1. **Discuss first**: Create an issue describing the tool and its purpose
2. **Get approval**: Wait for maintainer approval before starting work
3. **Create structure**: Follow the standard tool directory structure
4. **Develop**: Build your CloudFormation template and supporting scripts
5. **Test**: Validate in multiple AWS regions if applicable
6. **Document**: Write comprehensive README and deployment guide
7. **Submit**: Create a pull request with your new tool

## 📁 Tool Directory Structure

Each new tool should follow this structure:

```
tool-name/
├── README.md                      # Tool overview and features
├── DEPLOYMENT_GUIDE.md            # Detailed deployment instructions
├── cloudformation/
│   ├── template.yaml              # Main CloudFormation template
│   └── parameters/                # Sample parameter files
│       ├── dev.json
│       └── prod.json
├── scripts/
│   ├── test_tool.py              # Testing/validation script
│   └── deploy.sh                 # Deployment helper script
├── examples/
│   └── usage-examples.sh         # Example commands
└── docs/
    ├── architecture.png          # Architecture diagram
    └── troubleshooting.md        # Common issues and solutions
```

## 🧪 Testing Requirements

### CloudFormation Templates

- [ ] Validate template syntax: `aws cloudformation validate-template`
- [ ] Deploy successfully in a test account
- [ ] All resources created correctly
- [ ] All outputs are accurate
- [ ] Stack deletes cleanly
- [ ] Works in multiple AWS regions
- [ ] Cost is documented and reasonable

### Python Scripts

- [ ] Runs without errors
- [ ] Handles AWS API errors gracefully
- [ ] Includes helpful error messages
- [ ] Works with Python 3.12+
- [ ] Dependencies are documented
- [ ] Includes usage examples

### Documentation

- [ ] All features are documented
- [ ] Deployment steps are clear and tested
- [ ] Code examples work as shown
- [ ] Troubleshooting section is comprehensive
- [ ] Security considerations are documented

## 📝 Pull Request Process

1. **Update documentation** with details of changes
2. **Update the main README.md** if adding a new tool
3. **Include test results** from your AWS account (sanitize account IDs!)
4. **Add examples** of how to use new features
5. **Request review** from maintainers
6. **Address feedback** promptly and professionally
7. **Squash commits** if requested before merging

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New tool
- [ ] Enhancement
- [ ] Documentation update

## Testing
- [ ] Tested in AWS account (region: us-east-1)
- [ ] CloudFormation template validated
- [ ] Scripts tested with Python 3.12
- [ ] Documentation reviewed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No hardcoded credentials
- [ ] Tests pass

## Screenshots (if applicable)
Add screenshots showing the tool in action

## Additional Notes
Any other context about the PR
```

## 🐛 Reporting Bugs

### Before Submitting a Bug Report

- Check the documentation to confirm expected behavior
- Search existing issues to avoid duplicates
- Test in the latest version
- Collect relevant logs and error messages

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Deploy stack with parameters '...'
2. Trigger Lambda function '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- AWS Region: us-east-1
- Python version: 3.12
- AWS CLI version: 2.x

**CloudFormation Stack Output**
```
Stack creation failed...
```

**CloudWatch Logs**
```
Lambda error: ...
```

**Additional context**
Any other context about the problem.
```

## 💡 Feature Requests

We love feature requests! Before submitting:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** clearly
3. **Explain the value** it would provide
4. **Consider implementation** complexity
5. **Be open to discussion** about alternatives

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Use case**
Describe how this would be used in practice.

**Additional context**
Any other context or screenshots.
```

## 🔒 Security Vulnerabilities

**DO NOT** open public issues for security vulnerabilities.

Instead, please email security@yourcompany.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We'll respond within 48 hours and work with you on a fix.

## 💬 Community Guidelines

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience
- Nationality, personal appearance, race
- Religion, sexual identity and orientation

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct reasonably considered inappropriate

## ❓ Questions?

Don't hesitate to ask! You can:
- Open a discussion on GitHub Discussions
- Comment on relevant issues
- Reach out to maintainers

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- The project README
- Release notes for significant contributions
- Our hearts forever ❤️

---

**Thank you for contributing to making AWS environments more secure! 🔒**
