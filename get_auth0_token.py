#!/usr/bin/env python3
"""
Get Auth0 Token
Test script to get OAuth token for testing MCP connections
"""

import requests
import json
import os
import sys

# OAuth configuration - load from environment or Parameter Store
CLIENT_ID = os.getenv("ANSIBLE_MCP_CLIENT_ID")
CLIENT_SECRET = os.getenv("ANSIBLE_MCP_CLIENT_SECRET")
ISSUER_URL = os.getenv("ANSIBLE_MCP_ISSUER_URL")
AUDIENCE = os.getenv("ANSIBLE_MCP_AUDIENCE")

if not all([CLIENT_ID, CLIENT_SECRET, ISSUER_URL, AUDIENCE]):
    print("❌ Missing OAuth configuration!")
    print("\nSet environment variables:")
    print("  export ANSIBLE_MCP_CLIENT_ID='your-client-id'")
    print("  export ANSIBLE_MCP_CLIENT_SECRET='your-client-secret'")
    print("  export ANSIBLE_MCP_ISSUER_URL='https://your-auth-provider.com/'")
    print("  export ANSIBLE_MCP_AUDIENCE='your-api-audience'")
    print("\nOr load from AWS Parameter Store using oauth_manager.py")
    sys.exit(1)

def get_auth0_token():
    """Get OAuth token for testing"""
    token_url = f"{ISSUER_URL.rstrip('/')}/oauth/token"
    
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": AUDIENCE
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(token_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data["access_token"]
        
        print("🔑 OAuth Token Retrieved:")
        print(f"Bearer {access_token[:50]}...")
        print(f"\n📋 Use this token for testing:")
        print(f"Authorization: Bearer {access_token}")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Failed to get OAuth token: {e}")
        return None

if __name__ == "__main__":
    get_auth0_token()
