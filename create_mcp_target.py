#!/usr/bin/env python3
"""
Create MCP Gateway Target
Creates the MCP server target for the Ansible MCP Gateway using OAuth credential provider
"""

import json
import boto3
import sys
import os


def find_oauth_provider_arn():
    """Find the OAuth credential provider ARN for ansible-mcp"""
    print("🔍 Looking for OAuth credential provider...")
    
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        # Try to get the specific provider by name
        try:
            response = client.get_oauth2_credential_provider(
                name='ansible-mcp-auth0-custom-provider'
            )
            provider_arn = response['credentialProviderArn']
            print(f"✅ Found OAuth provider: {provider_arn}")
            return provider_arn
        except client.exceptions.ResourceNotFoundException:
            print("❌ OAuth credential provider 'ansible-mcp-auth0-custom-provider' not found")
            print("Run 'python create_oauth_provider.py' first to create the provider")
            return None
        
    except Exception as e:
        print(f"❌ Failed to get OAuth provider: {e}")
        # Try listing as fallback
        try:
            response = client.list_oauth2_credential_providers()
            
            # Look for our provider
            for provider in response.get('oauth2CredentialProviders', []):
                if provider['name'] == 'ansible-mcp-auth0-custom-provider':
                    provider_arn = provider['credentialProviderArn']
                    print(f"✅ Found OAuth provider via list: {provider_arn}")
                    return provider_arn
            
            print("❌ OAuth credential provider 'ansible-mcp-auth0-custom-provider' not found in list")
            return None
            
        except Exception as list_error:
            print(f"❌ Failed to list OAuth providers: {list_error}")
            return None


def create_mcp_target():
    """Create MCP server target with OAuth credential provider"""
    print("🎯 Creating MCP Gateway Target...")
    
    # Find OAuth provider ARN
    provider_arn = find_oauth_provider_arn()
    if not provider_arn:
        return False
    
    # Gateway details - get from environment or use defaults
    gateway_identifier = os.getenv("GATEWAY_ID", "your-gateway-id")
    
    # Create AgentCore Control client
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    # Prepare the request
    request_data = {
        'gatewayIdentifier': gateway_identifier,
        'name': 'ansible-mcp-target-no-scopes',
        'targetConfiguration': {
            'mcp': {
                'mcpServer': {
                    'endpoint': os.getenv("MCP_SERVER_URL", "https://your-mcp-server.example.com/mcp")
                }
            }
        },
        'credentialProviderConfigurations': [
            {
                'credentialProviderType': 'OAUTH',
                'credentialProvider': {
                    'oauthCredentialProvider': {
                        'providerArn': provider_arn,
                        'grantType': 'CLIENT_CREDENTIALS',
                        'scopes': [],  # Empty scopes for client credentials
                        'customParameters': {
                            'audience': 'infragenie-mcp'
                        }
                    }
                }
            }
        ]
    }
    
    try:
        print(f"Creating MCP target with OAuth provider: {provider_arn}")
        response = client.create_gateway_target(**request_data)
        
        target_id = response['targetId']
        status = response['status']
        
        print(f"✅ MCP target created successfully!")
        print(f"   Target ID: {target_id}")
        print(f"   Status: {status}")
        
        # Check target status
        print("⏳ Checking target status...")
        target_response = client.get_gateway_target(
            gatewayIdentifier=gateway_identifier,
            targetId=target_id
        )
        
        final_status = target_response['status']
        print(f"✅ Target status: {final_status}")
        
        if final_status in ['READY', 'ACTIVE']:
            print("✅ Target is ready!")
        else:
            print(f"ℹ️  Target is in {final_status} state. It may take a few minutes to become ready.")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create MCP target: {e}")
        return False


def main():
    """Main function"""
    print("🎯 Creating Ansible MCP Gateway Target...\n")
    
    success = create_mcp_target()
    
    if success:
        print("\n✅ MCP Gateway Target created successfully!")
        print("Run 'python test_gateway.py' to test the connection")
    else:
        print("\n❌ Failed to create MCP Gateway Target")
        sys.exit(1)


if __name__ == "__main__":
    main()