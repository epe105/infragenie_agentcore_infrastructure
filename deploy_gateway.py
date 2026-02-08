#!/usr/bin/env python3
"""
Deploy Ansible MCP Gateway
Creates an AgentCore Gateway that connects to the Ansible MCP server with OAuth authentication
"""

import subprocess
import sys
import json
from oauth_manager import create_oauth_token_manager


def run_command(cmd: list[str]) -> dict:
    """Run a command and return the result"""
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Try to parse JSON output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"stdout": result.stdout, "stderr": result.stderr}
            
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return {"error": str(e), "stdout": e.stdout, "stderr": e.stderr}


def check_existing_gateway() -> dict:
    """Check if gateway already exists"""
    print("Checking for existing gateways...")
    result = run_command(["agentcore", "gateway", "list-mcp-gateways", "--region", "us-east-1"])
    
    if result.get("status") == "success":
        for gateway in result.get("items", []):
            if gateway.get("name") == "ansible-mcp-gateway":
                print(f"Found existing gateway: {gateway['gatewayId']}")
                return gateway
    
    return None


def delete_gateway(gateway_id: str) -> bool:
    """Delete existing gateway"""
    print(f"Deleting existing gateway: {gateway_id}")
    result = run_command(["agentcore", "gateway", "delete-mcp-gateway", "--id", gateway_id])
    
    if "error" not in result:
        print("Gateway deleted successfully")
        return True
    else:
        print(f"Failed to delete gateway: {result}")
        return False


def create_gateway() -> dict:
    """Create new MCP gateway"""
    print("Creating new Ansible MCP gateway...")
    
    result = run_command([
        "agentcore", "gateway", "create-mcp-gateway",
        "--name", "ansible-mcp-gateway",
        "--region", "us-east-1"
    ])
    
    if result.get("status") == "success":
        gateway_id = result.get("gatewayId")
        print(f"Gateway created successfully: {gateway_id}")
        return result
    else:
        print(f"Failed to create gateway: {result}")
        return None


def create_gateway_target(gateway_id: str, oauth_token: str) -> dict:
    """Create gateway target with OAuth authentication"""
    print(f"Creating gateway target for gateway: {gateway_id}")
    
    # MCP server configuration - get from environment or use placeholder
    mcp_server_url = os.getenv("MCP_SERVER_URL", "https://your-mcp-server.example.com/mcp")
    
    result = run_command([
        "agentcore", "gateway", "create-mcp-gateway-target",
        "--gateway-id", gateway_id,
        "--name", "ansible-mcp-target",
        "--url", mcp_server_url,
        "--description", "Ansible MCP Server Target",
        "--auth-type", "bearer",
        "--auth-token", oauth_token,
        "--region", "us-east-1"
    ])
    
    if result.get("status") == "success":
        print("Gateway target created successfully")
        return result
    else:
        print(f"Failed to create gateway target: {result}")
        return None


def main():
    """Main deployment function"""
    print("🚀 Deploying Ansible MCP Gateway...")
    
    try:
        # Get OAuth token
        print("Getting OAuth token...")
        token_manager = create_oauth_token_manager()
        oauth_token = token_manager.get_token()
        print("✅ OAuth token obtained")
        
        # Check for existing gateway
        existing_gateway = check_existing_gateway()
        
        if existing_gateway:
            response = input(f"Gateway '{existing_gateway['name']}' already exists. Delete and recreate? (y/N): ")
            if response.lower() == 'y':
                if not delete_gateway(existing_gateway['gatewayId']):
                    print("❌ Failed to delete existing gateway")
                    sys.exit(1)
                # Wait a moment for deletion to complete
                import time
                time.sleep(5)
            else:
                print("Using existing gateway")
                gateway_id = existing_gateway['gatewayId']
                
                # Try to create target (might already exist)
                create_gateway_target(gateway_id, oauth_token)
                return
        
        # Create new gateway
        gateway_result = create_gateway()
        if not gateway_result:
            print("❌ Failed to create gateway")
            sys.exit(1)
        
        gateway_id = gateway_result.get("gatewayId")
        
        # Wait for gateway to be ready
        print("Waiting for gateway to be ready...")
        import time
        time.sleep(10)
        
        # Create gateway target
        target_result = create_gateway_target(gateway_id, oauth_token)
        if not target_result:
            print("❌ Failed to create gateway target")
            sys.exit(1)
        
        print("✅ Gateway deployment completed successfully!")
        print(f"Gateway ID: {gateway_id}")
        print(f"Gateway Name: ansible-mcp-gateway")
        print(f"Target: ansible-mcp-target")
        print(f"MCP Server: {os.getenv('MCP_SERVER_URL', 'https://your-mcp-server.example.com/mcp')}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()