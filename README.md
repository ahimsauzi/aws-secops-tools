# AWS SecOps Tools 🔒☁️

A collection of production-ready security operations automation tools for AWS environments. Built with shift-left security principles and cloud-native best practices.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS](https://img.shields.io/badge/AWS-CloudFormation-orange.svg)](https://aws.amazon.com/cloudformation/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🎯 Overview

This repository contains a curated set of CloudFormation templates and automation scripts designed to enhance security posture in AWS environments. Each tool is production-tested, follows AWS best practices, and can be deployed independently.

## 🛠️ Available Tools

### [IAM Inactive User Cleanup](./iam-inactive-user-cleanup/)
Automatically identifies, flags, and removes inactive IAM users to reduce attack surface.

**Features:**
- 🔍 Daily scanning for inactive users
- 🚫 Immediate access key revocation
- ⏰ Configurable grace period
- 📧 Email notifications via SNS
- 🗑️ Automated cleanup with DynamoDB TTL
- 💰 Cost: <$1/month

**Status:** ✅ Production Ready

---

## 🚀 Quick Start

Each tool has its own directory with complete documentation:

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-secops-tools.git
cd aws-secops-tools

# Navigate to a specific tool
cd iam-inactive-user-cleanup

# Follow the tool's README for deployment
```

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Python 3.12+ (for testing scripts)
- Basic understanding of CloudFormation and AWS services

## 🏗️ Repository Structure

```
aws-secops-tools/
├── README.md                          # This file
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore patterns
│
├── iam-inactive-user-cleanup/         # IAM inactive user automation
│   ├── README.md                      # Tool-specific documentation
│   ├── DEPLOYMENT_GUIDE.md            # Detailed deployment guide
│   ├── cloudformation/
│   │   └── template.yaml              # CloudFormation template
│   ├── scripts/
│   │   └── test_iam_cleanup.py        # Testing and validation script
│   └── examples/
│       └── deployment-examples.sh     # Sample deployment commands
│
└── [future-tools]/                    # Additional security tools
```

## 🔒 Security Philosophy

All tools in this repository follow these core principles:

1. **Shift-Left Security**: Proactive rather than reactive
2. **Least Privilege**: Minimal IAM permissions required
3. **Defense in Depth**: Multiple layers of security controls
4. **Audit & Compliance**: Full logging and traceability
5. **Automation First**: Reduce human error and toil
6. **Cost-Conscious**: Serverless, event-driven architectures

## 📊 Tool Comparison

| Tool | Purpose | AWS Services | Deployment Time | Monthly Cost* |
|------|---------|--------------|-----------------|---------------|
| IAM Inactive User Cleanup | Remove inactive users | Lambda, DynamoDB, SNS | ~5 minutes | <$1 |
| *More tools coming soon* | | | | |

*Costs based on typical usage in small-to-medium AWS accounts

## 🎓 Best Practices

- **Test in non-production first**: Always deploy to dev/test environments
- **Review before production**: Understand what each tool does
- **Monitor after deployment**: Use CloudWatch and SNS alerts
- **Version control your parameters**: Track configuration changes
- **Use CloudFormation StackSets**: For multi-account deployments
- **Enable AWS Config**: For compliance tracking

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- Submitting new tools
- Reporting bugs
- Suggesting enhancements
- Code standards and testing requirements

### Adding a New Tool

1. Create a new directory under the repository root
2. Include complete documentation (README, deployment guide)
3. Provide CloudFormation template or Infrastructure-as-Code
4. Include testing/validation scripts
5. Update this main README with tool information
6. Submit a pull request

## 📖 Documentation

Each tool includes:
- **README.md**: Overview, features, and quick start
- **DEPLOYMENT_GUIDE.md**: Detailed deployment instructions and best practices
- **CloudFormation Templates**: Infrastructure-as-Code for deployment
- **Test Scripts**: Validation and testing utilities
- **Examples**: Sample configurations and use cases

## 🐛 Issues & Support

- **Bug Reports**: [Open an issue](../../issues/new?template=bug_report.md)
- **Feature Requests**: [Submit an enhancement](../../issues/new?template=feature_request.md)
- **Questions**: [Start a discussion](../../discussions)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK**

These tools perform automated actions in your AWS account. While production-tested, you should:

1. Thoroughly review all code and CloudFormation templates
2. Test in non-production environments first
3. Understand the impact of each tool on your environment
4. Maintain proper backups and rollback procedures
5. Ensure compliance with your organization's policies

The authors and contributors are not responsible for any damage, data loss, or costs incurred from using these tools.

## 🗺️ Roadmap

Planned tools and enhancements:

- [ ] S3 Bucket Security Auditor
- [ ] Security Group Cleanup Automation
- [ ] CloudTrail Log Analysis & Alerting
- [ ] Unused EBS Volume Identifier
- [ ] Compliance Reporting Dashboard
- [ ] Multi-account security orchestration
- [ ] Terraform versions of CloudFormation templates

## 🙏 Acknowledgments

Built with ❤️ by security engineers, for security engineers.

Special thanks to the AWS community and contributors who help make cloud environments more secure.

## 📞 Contact

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Security Vulnerabilities**: Please report privately via security@yourcompany.com

---

**⭐ If you find these tools useful, please star this repository!**

Made with ☕ and Python | Deployed with ☁️ CloudFormation
