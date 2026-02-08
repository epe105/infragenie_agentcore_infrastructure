#!/usr/bin/env python3
"""
List Gateway Targets
Lists all targets for the Ansible MCP Gateway
"""

import boto3
import json
import os


def list_gateway_targets():
    """List all targets for the gateway"""
    print("📋 Listing Gateway Targets...")
    
    # Get gateway ID from environment or use default
    gateway_identifier = os.getenv("GATEWAY_ID", "your-gateway-id")
    
    client = boto3.client('bedrock-agentcore-control', region_name='us-east-1')
    
    try:
        response = client.list_gateway_targets(
            gatewayIdentifier=gateway_identifier
        )
        
        targets = response.get('targets', [])
        
        if not targets:
            print("No targets found for the gateway")
            return
        
        print(f"Found {len(targets)} target(s):")
        
        for target in targets:
            print(f"\n📌 Target: {target['name']}")
            print(f"   ID: {target['targetId']}")
            print(f"   Status: {target['status']}")
            print(f"   Type: {target.get('targetType', 'N/A')}")
            
            # Get detailed target info
            try:
                detail_response = client.get_gateway_target(
                    gatewayIdentifier=gateway_identifier,
                    targetId=target['targetId']
                )
                
                print(f"   Configuration: {json.dumps(detail_response.get('targetConfiguration', {}), indent=6)}")
                print(f"   Credentials: {json.dumps(detail_response.get('credentialProviderConfigurations', []), indent=6)}")
                
            except Exception as e:
                print(f"   Error getting details: {e}")
        
    except Exception as e:
        print(f"❌ Failed to list gateway targets: {e}")


def main():
    """Main function"""
    print("📋 Listing Ansible MCP Gateway Targets...\n")
    list_gateway_targets()


if __name__ == "__main__":
    main()