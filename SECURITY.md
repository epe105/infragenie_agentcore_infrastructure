# Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please email security@example.com (replace with your actual security contact). Do not open a public issue.

## Security Best Practices

### Credential Management

**DO:**
- ✅ Store OAuth credentials in AWS Parameter Store (encrypted)
- ✅ Use environment variables for configuration
- ✅ Rotate credentials regularly
- ✅ Use least-privilege IAM policies
- ✅ Enable MFA on AWS accounts

**DON'T:**
- ❌ Commit credentials to version control
- ❌ Hardcode secrets in code
- ❌ Share credentials via email or chat
- ❌ Use production credentials for testing
- ❌ Store credentials in plain text files

### AWS Parameter Store Setup

Store sensitive values securely:

```bash
# Client Secret (encrypted)
aws ssm put-parameter \
  --name "/infragenie/oauth/client_secret" \
  --value "YOUR_SECRET" \
  --type "SecureString" \
  --region us-east-1

# Other values (not encrypted but access-controlled)
aws ssm put-parameter \
  --name "/infragenie/oauth/client_id" \
  --value "YOUR_CLIENT_ID" \
  --type "String" \
  --region us-east-1
```

### IAM Permissions

Minimum required permissions for deployment:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:CreateGateway",
        "bedrock-agentcore:CreateGatewayTarget",
        "bedrock-agentcore:GetGateway",
        "bedrock-agentcore:GetGatewayTarget",
        "bedrock-agentcore:ListGateways",
        "bedrock-agentcore:ListGatewayTargets"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:*:*:parameter/infragenie/oauth/*"
    }
  ]
}
```

### Network Security

- All communication uses HTTPS/TLS
- Gateway requires Cognito JWT authentication
- MCP server requires OAuth 2.0 authentication
- No credentials transmitted in URLs or query parameters

### Monitoring

Enable CloudWatch logging for:
- Gateway access logs
- Failed authentication attempts
- Unusual access patterns
- Parameter Store access

### Credential Rotation

Rotate OAuth credentials:
1. Generate new credentials in your identity provider
2. Update AWS Parameter Store
3. Test with new credentials
4. Revoke old credentials

### Audit

Regular security audits should include:
- Review IAM policies and permissions
- Check Parameter Store access logs
- Verify credential rotation schedule
- Review gateway access patterns
- Update dependencies for security patches

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < 1.0   | :x:                |

## Security Updates

Security updates will be released as soon as possible after discovery. Subscribe to repository notifications to stay informed.

## Compliance

This project follows:
- AWS Well-Architected Framework Security Pillar
- OWASP Top 10 security practices
- Principle of least privilege
- Defense in depth

## Contact

For security concerns: security@example.com (replace with actual contact)
