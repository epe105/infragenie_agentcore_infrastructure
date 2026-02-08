# Deployment Guide

Step-by-step guide for deploying an MCP Gateway using AWS Bedrock AgentCore.

## Prerequisites Checklist

- [ ] AWS account with Bedrock AgentCore enabled
- [ ] AWS CLI configured (`aws configure`)
- [ ] Python 3.9 or higher installed
- [ ] OAuth credentials from your identity provider (Auth0, Okta, etc.)

## Step 1: Environment Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/infragenie_agentcore_infrastructure.git
cd infragenie_agentcore_infrastructure

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure OAuth Credentials

Store your OAuth credentials in AWS Systems Manager Parameter Store:

```bash
# Client ID (public)
aws ssm put-parameter \
  --name "/infragenie/oauth/client_id" \
  --value "YOUR_CLIENT_ID" \
  --type "String" \
  --region us-east-1

# Client Secret (encrypted)
aws ssm put-parameter \
  --name "/infragenie/oauth/client_secret" \
  --value "YOUR_CLIENT_SECRET" \
  --type "SecureString" \
  --region us-east-1

# Issuer URL
aws ssm put-parameter \
  --name "/infragenie/oauth/issuer_url" \
  --value "https://your-auth-provider.com/" \
  --type "String" \
  --region us-east-1

# API Audience
aws ssm put-parameter \
  --name "/infragenie/oauth/audience" \
  --value "your-api-audience" \
  --type "String" \
  --region us-east-1
```

## Step 3: Deploy Gateway Infrastructure

### 3.1 Deploy the Gateway
```bash
python deploy_gateway.py
```

Expected output:
```
🚀 Deploying Ansible MCP Gateway...
✅ Gateway created successfully!
   Gateway ID: ansible-mcp-gateway-XXXXXXXXXX
   Status: READY
```

### 3.2 Create OAuth Provider
```bash
python create_oauth_provider.py
```

Expected output:
```
🔐 Creating OAuth2 Credential Provider...
✅ OAuth provider created successfully!
   Provider ARN: arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:token-vault/...
```

### 3.3 Create Gateway Target
```bash
python create_mcp_target.py
```

Expected output:
```
🎯 Creating MCP Gateway Target...
✅ MCP target created successfully!
   Target ID: XXXXXXXXXX
   Status: READY
```

## Step 4: Verify Deployment

### Check Gateway Status
```bash
python check_gateway.py
```

Expected output:
```
✅ Gateway: ansible-mcp-gateway is READY
✅ Target: ansible-mcp-target-no-scopes is READY
   Last Sync: 2026-02-08 22:08:49
```

### Test Gateway Connectivity
```bash
python test_gateway_http.py
```

Expected output:
```
✅ Found 19 tools via direct connection
❌ 401 Unauthorized - Cognito JWT required (expected)
```

Note: The 401 error is expected - it confirms the gateway is working and requires authentication.

## Step 5: Configure Agent Access

### Get Gateway URL
Your gateway URL will be:
```
https://GATEWAY_ID.gateway.bedrock-agentcore.REGION.amazonaws.com/mcp
```

### Configure Cognito Authentication
To use the gateway, agents need a Cognito JWT token. Set up Cognito user pool authentication:

1. Create Cognito User Pool (if not exists)
2. Configure app client with appropriate scopes
3. Implement JWT token retrieval in your agent
4. Include token in Authorization header

## Troubleshooting

### Gateway shows READY but tools don't appear in UI
This is a known display issue. Tools are accessible via API. Verify with:
```bash
python test_gateway_http.py
```

### Target shows FAILED status
Check OAuth credentials:
```bash
python get_auth0_token.py
```

If this fails, verify Parameter Store values:
```bash
aws ssm get-parameter --name "/infragenie/oauth/client_id" --region us-east-1
```

### 401 Unauthorized errors
The gateway requires Cognito JWT authentication. This is expected behavior for production use.

### Connection timeouts
Verify:
- MCP server is accessible from AWS
- Security groups allow outbound HTTPS
- OAuth credentials are correct

## Maintenance

### Update OAuth Credentials
```bash
aws ssm put-parameter \
  --name "/infragenie/oauth/client_secret" \
  --value "NEW_SECRET" \
  --type "SecureString" \
  --overwrite \
  --region us-east-1
```

### Check Gateway Logs
View CloudWatch logs for the gateway (if enabled):
```bash
aws logs tail /aws/bedrock-agentcore/gateway/GATEWAY_ID --follow
```

### Delete Gateway (cleanup)
```bash
# Delete target first
agentcore gateway delete-mcp-gateway-target \
  --id GATEWAY_ID \
  --target-id TARGET_ID \
  --region us-east-1

# Then delete gateway
agentcore gateway delete-mcp-gateway \
  --id GATEWAY_ID \
  --region us-east-1
```

## Next Steps

- Configure Cognito authentication for your agents
- Integrate gateway URL into agent configurations
- Set up monitoring and alerting
- Document gateway usage for your team

## Support

For issues or questions:
- Check the [README.md](README.md) for detailed documentation
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Open an issue on GitHub

## Security Notes

- Never commit credentials to version control
- Use AWS Parameter Store for all secrets
- Rotate OAuth credentials regularly
- Monitor gateway access logs
- Use least-privilege IAM policies
