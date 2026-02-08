#!/usr/bin/env python3
"""
Create OAuth2 Credential Provider
Creates an OAuth2 credential provider for Auth0 to be used with MCP Gateway targets
"""

import json
import boto3
from oauth_manager import get_oauth_config


def create_oauth2_credential_provider():
    """Create OAuth2 credential provider for Auth0"""
    print("🔐 Creating OAuth2 Credential Provider...")
    
    # Get OAuth configuration
    try:
        client_id, client_secret, issuer_url, audience = get_oauth_config()
        print("✅ OAuth configuration obtained")
    except Exception as e:
        print(f"❌ Failed to get OAuth configuration: {e}")
        return None
    
    # Create AgentCore Control client
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    # Prepare the request
    request_data = {
        'name': 'ansible-mcp-auth0-custom-provider',
        'credentialProviderVendor': 'CustomOauth2',
        'oauth2ProviderConfigInput': {
            'customOauth2ProviderConfig': {
                'clientId': client_id,
                'clientSecret': client_secret,
                'oauthDiscovery': {
                    'discoveryUrl': f"{issuer_url.rstrip('/')}/.well-known/openid-configuration"
                }
            }
        },
        'tags': {
            'Project': 'InfraGenie',
            'Purpose': 'Ansible-MCP-Gateway'
        }
    }
    
    try:
        print(f"Creating OAuth2 provider with issuer: {issuer_url}")
        response = client.create_oauth2_credential_provider(**request_data)
        
        provider_arn = response['credentialProviderArn']
        callback_url = response.get('callbackUrl', 'N/A')
        
        print(f"✅ OAuth2 credential provider created successfully!")
        print(f"   Provider ARN: {provider_arn}")
        print(f"   Callback URL: {callback_url}")
        
        return provider_arn
        
    except Exception as e:
        print(f"❌ Failed to create OAuth2 credential provider: {e}")
        return None


def main():
    """Main function"""
    print("🔐 Creating OAuth2 Credential Provider for Ansible MCP...\n")
    
    provider_arn = create_oauth2_credential_provider()
    
    if provider_arn:
        print(f"\n✅ OAuth2 Credential Provider created successfully!")
        print(f"Provider ARN: {provider_arn}")
        print("\nNext step: Run 'python create_mcp_target.py' to create the gateway target")
    else:
        print("\n❌ Failed to create OAuth2 Credential Provider")


if __name__ == "__main__":
    main()