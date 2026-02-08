# InfraGenie AgentCore Infrastructure

Infrastructure-as-code for deploying and managing AWS Bedrock AgentCore Gateways that provide shared MCP (Model Context Protocol) tool access across multiple AI agents.

## Overview

This project creates reusable MCP gateways that:
- Centralize authentication and credential management
- Provide shared tool access across multiple agents
- Enable team collaboration without duplicating MCP server connections
- Support OAuth 2.0 authentication flows

## Current Gateways

### Ansible MCP Gateway
Provides Ansible Automation Platform tools to AI agents for infrastructure automation tasks.

- **Gateway Name**: `ansible-mcp-gateway`
- **MCP Server**: Your Ansible MCP server endpoint
- **Authentication**: 
  - Inbound (agents → gateway): Cognito JWT
  - Outbound (gateway → MCP): OAuth 2.0 Client Credentials (Auth0)
- **Tools Available**: 19 Ansible automation tools
- **Status**: Deployed and operational

## Prerequisites

### AWS Configuration
- AWS CLI configured with appropriate permissions
- AWS Bedrock AgentCore access enabled in your account
- Region: `us-east-1`

### Python Environment
```bash
# Install AgentCore CLI (requires Python 3.9+)
pip install bedrock-agentcore

# Install project dependencies
pip install -r requirements.txt
```

### OAuth Credentials
Store OAuth credentials in AWS Systems Manager Parameter Store:

```bash
aws ssm put-parameter \
  --name "/infragenie/oauth/client_id" \
  --value "YOUR_CLIENT_ID" \
  --type "String"

aws ssm put-parameter \
  --name "/infragenie/oauth/client_secret" \
  --value "YOUR_CLIENT_SECRET" \
  --type "SecureString"

aws ssm put-parameter \
  --name "/infragenie/oauth/issuer_url" \
  --value "https://your-auth-provider.com/" \
  --type "String"

aws ssm put-parameter \
  --name "/infragenie/oauth/audience" \
  --value "your-api-audience" \
  --type "String"
```

## Deployment

### 1. Deploy the Gateway
```bash
python deploy_gateway.py
```

This creates the MCP gateway with Cognito JWT authentication.

### 2. Create OAuth Provider
```bash
python create_oauth_provider.py
```

This creates an OAuth 2.0 credential provider for authenticating to the MCP server.

### 3. Create Gateway Target
```bash
python create_mcp_target.py
```

This connects the gateway to the MCP server using the OAuth provider.

### 4. Verify Deployment
```bash
# Check gateway status
python check_gateway.py

# Test gateway connectivity
python test_gateway_http.py
```

## Management Scripts

### Core Scripts
- `deploy_gateway.py` - Deploy a new MCP gateway
- `create_oauth_provider.py` - Create OAuth credential provider
- `create_mcp_target.py` - Create gateway target (MCP server connection)
- `oauth_manager.py` - OAuth token management utilities

### Monitoring & Testing
- `check_gateway.py` - Check gateway and target status
- `list_gateway_targets.py` - List all targets for a gateway
- `test_gateway_http.py` - Test gateway tool access via HTTP
- `get_auth0_token.py` - Get OAuth token for testing

## Gateway Architecture

```
┌─────────────┐         Cognito JWT          ┌──────────────┐
│   AI Agent  │ ─────────────────────────────>│   Gateway    │
└─────────────┘                               │              │
                                              │  (AgentCore) │
                                              │              │
                                              └──────┬───────┘
                                                     │
                                              OAuth Bearer
                                                     │
                                              ┌──────▼───────┐
                                              │  MCP Server  │
                                              │   (Ansible)  │
                                              └──────────────┘
```

## Using the Gateway in Agents

### Option 1: Direct HTTP (requires Cognito JWT)
```python
import requests
import os

# Get gateway URL from environment
gateway_id = os.getenv("GATEWAY_ID")
region = os.getenv("AWS_REGION", "us-east-1")
gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.{region}.amazonaws.com/mcp"

# Get Cognito JWT token (implementation depends on your auth setup)
jwt_token = get_cognito_jwt_token()

# Make MCP requests
response = requests.post(
    gateway_url,
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {...}
    },
    headers={
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
)
```

### Option 2: Strands Agent Integration
```python
from strands import Agent
from strands.tools.mcp import MCPClient
import os

# Get gateway URL from environment
gateway_id = os.getenv("GATEWAY_ID")
region = os.getenv("AWS_REGION", "us-east-1")
gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.{region}.amazonaws.com/mcp"

# Configure MCP client to use gateway
mcp_client = MCPClient(
    gateway_url=gateway_url,
    auth_provider=cognito_jwt_provider
)

agent = Agent(tools=[mcp_client])
```

## Troubleshooting

### Gateway shows READY but tools don't appear in AWS Console UI
This is a known display issue. The gateway is functional - tools are accessible via API even if they don't show in the UI. Use `test_gateway_http.py` to verify tool access.

### 401 Unauthorized errors
The gateway requires Cognito JWT authentication. Ensure you have:
1. Valid Cognito user pool credentials
2. JWT token included in Authorization header
3. Proper IAM permissions for gateway access

### Target shows FAILED status
Check the OAuth credentials in Parameter Store:
```bash
python get_auth0_token.py  # Test OAuth token retrieval
```

Verify the MCP server is accessible and OAuth credentials are correct.

## Project Structure

```
infragenie_agentcore_infrastructure/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
│
├── deploy_gateway.py              # Deploy MCP gateway
├── create_oauth_provider.py       # Create OAuth provider
├── create_mcp_target.py           # Create gateway target
├── oauth_manager.py               # OAuth utilities
│
├── check_gateway.py               # Status checking
├── list_gateway_targets.py        # List targets
├── test_gateway_http.py           # Test gateway access
└── get_auth0_token.py             # OAuth token testing
```

## Security Considerations

- OAuth credentials are stored in AWS Parameter Store (encrypted)
- Gateway uses Cognito JWT for inbound authentication
- All communication over HTTPS
- Credentials never stored in code or version control

## Contributing

When adding new gateways:
1. Follow the naming convention: `{service}-mcp-gateway`
2. Document authentication requirements
3. Add deployment scripts following existing patterns
4. Update this README with gateway details

## License

[Your License Here]

## Support

For issues or questions, please open an issue in the GitHub repository.
