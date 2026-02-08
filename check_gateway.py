#!/usr/bin/env python3
"""
Check Gateway Status
Displays the current status of the Ansible MCP Gateway and its targets
"""

import subprocess
import json
import sys
from datetime import datetime


def run_command(cmd: list[str]) -> dict:
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Try to parse JSON output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"stdout": result.stdout, "stderr": result.stderr}
            
    except subprocess.CalledProcessError as e:
        return {"error": str(e), "stdout": e.stdout, "stderr": e.stderr}


def format_datetime(dt_str):
    """Format datetime string for display"""
    if isinstance(dt_str, str):
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            return dt_str
    return str(dt_str)


def check_gateways():
    """Check all gateways"""
    print("🔍 Checking MCP Gateways...")
    
    result = run_command(["agentcore", "gateway", "list-mcp-gateways", "--region", "us-east-1"])
    
    if result.get("status") == "success":
        gateways = result.get("items", [])
        print(f"Found {len(gateways)} gateway(s)")
        
        for gateway in gateways:
            print(f"\n📡 Gateway: {gateway.get('name', 'Unknown')}")
            print(f"   ID: {gateway.get('gatewayId', 'Unknown')}")
            print(f"   Status: {gateway.get('status', 'Unknown')}")
            print(f"   Protocol: {gateway.get('protocolType', 'Unknown')}")
            print(f"   Auth Type: {gateway.get('authorizerType', 'Unknown')}")
            print(f"   Created: {format_datetime(gateway.get('createdAt', 'Unknown'))}")
            print(f"   Updated: {format_datetime(gateway.get('updatedAt', 'Unknown'))}")
            
            # Check targets for this gateway
            check_gateway_targets(gateway.get('gatewayId'))
        
        return gateways
    else:
        print(f"❌ Failed to list gateways: {result}")
        return []


def check_gateway_targets(gateway_id: str):
    """Check targets for a specific gateway"""
    print(f"\n🎯 Checking targets for gateway: {gateway_id}")
    
    result = run_command([
        "agentcore", "gateway", "list-mcp-gateway-targets",
        "--id", gateway_id,
        "--region", "us-east-1"
    ])
    
    if result.get("status") == "success":
        targets = result.get("items", [])
        print(f"   Found {len(targets)} target(s)")
        
        for target in targets:
            print(f"\n   🎯 Target: {target.get('name', 'Unknown')}")
            print(f"      ID: {target.get('targetId', 'Unknown')}")
            print(f"      URL: {target.get('url', 'Unknown')}")
            print(f"      Status: {target.get('status', 'Unknown')}")
            print(f"      Auth Type: {target.get('authType', 'Unknown')}")
            print(f"      Created: {format_datetime(target.get('createdAt', 'Unknown'))}")
            print(f"      Updated: {format_datetime(target.get('updatedAt', 'Unknown'))}")
            
            # Check if there are any sync errors
            if target.get('lastSyncError'):
                print(f"      ❌ Last Sync Error: {target.get('lastSyncError')}")
            elif target.get('lastSyncTime'):
                print(f"      ✅ Last Sync: {format_datetime(target.get('lastSyncTime'))}")
    
    elif "error" in result:
        print(f"   ❌ Failed to list targets: {result['error']}")
    else:
        print(f"   ❌ Unexpected response: {result}")


def get_gateway_details(gateway_name: str = "ansible-mcp-gateway"):
    """Get detailed information about a specific gateway"""
    print(f"\n🔍 Getting details for gateway: {gateway_name}")
    
    result = run_command([
        "agentcore", "gateway", "get-mcp-gateway",
        "--name", gateway_name,
        "--region", "us-east-1"
    ])
    
    if result.get("status") == "success":
        gateway = result.get("gateway", {})
        print(f"✅ Gateway Details:")
        print(f"   Name: {gateway.get('name', 'Unknown')}")
        print(f"   ID: {gateway.get('gatewayId', 'Unknown')}")
        print(f"   Status: {gateway.get('status', 'Unknown')}")
        print(f"   ARN: {gateway.get('arn', 'Unknown')}")
        return gateway
    else:
        print(f"❌ Failed to get gateway details: {result}")
        return None


def main():
    """Main check function"""
    print("🔍 Checking Ansible MCP Gateway Status...\n")
    
    # Check all gateways
    gateways = check_gateways()
    
    # Look for our specific gateway
    ansible_gateway = None
    for gateway in gateways:
        if gateway.get('name') == 'ansible-mcp-gateway':
            ansible_gateway = gateway
            break
    
    if ansible_gateway:
        print(f"\n✅ Ansible MCP Gateway found and {'READY' if ansible_gateway.get('status') == 'READY' else 'NOT READY'}")
        
        # Get detailed information
        get_gateway_details("ansible-mcp-gateway")
        
    else:
        print("\n❌ Ansible MCP Gateway not found")
        print("Run 'python deploy_gateway.py' to create it")
        sys.exit(1)


if __name__ == "__main__":
    main()