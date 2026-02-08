#!/usr/bin/env python3
"""
Test Gateway HTTP Access
Test if the gateway URL provides access to Ansible MCP tools using simple HTTP requests
"""

import requests
import json
import os


def test_gateway_http():
    """Test gateway using simple HTTP requests"""
    print("🌐 Testing Gateway URL with HTTP...")
    
    # Get gateway URL from environment or use default
    gateway_id = os.getenv("GATEWAY_ID", "your-gateway-id")
    region = os.getenv("AWS_REGION", "us-east-1")
    gateway_url = f"https://{gateway_id}.gateway.bedrock-agentcore.{region}.amazonaws.com/mcp"
    
    print(f"   URL: {gateway_url}")
    print(f"   Note: Testing without Cognito JWT authentication")
    
    try:
        # Create session
        session = requests.Session()
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        session.headers.update(headers)
        
        # Step 1: Initialize
        print(f"\n📤 Step 1: Initialize")
        initialize_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "gateway-http-test", "version": "1.0.0"}
            }
        }
        
        init_response = session.post(gateway_url, json=initialize_payload, timeout=15)
        
        print(f"📥 Initialize Response:")
        print(f"   Status: {init_response.status_code}")
        
        if init_response.status_code == 401:
            print(f"   ❌ 401 Unauthorized - Cognito JWT required")
            print(f"\n💡 The gateway requires Cognito authentication")
            print(f"   To test with authentication:")
            print(f"   1. Get Cognito client secret from AWS Console")
            print(f"   2. Use AWS Cognito Identity Provider to get JWT")
            print(f"   3. Add 'Authorization: Bearer <jwt>' header")
            return False
        elif init_response.status_code == 403:
            print(f"   ❌ 403 Forbidden - Authorization issue")
            return False
        elif init_response.status_code != 200:
            print(f"   ❌ Unexpected status: {init_response.text[:200]}")
            return False
        
        # Parse response
        response_text = init_response.text
        print(f"   Raw Response: {response_text[:200]}...")
        
        # Check for session ID
        session_id = init_response.headers.get('mcp-session-id')
        if session_id:
            print(f"   🆔 Session ID: {session_id}")
            session.headers.update({"mcp-session-id": session_id})
        
        # Parse initialize response
        if response_text.startswith('event:'):
            lines = response_text.split('\n')
            data_lines = [line.replace('data: ', '') for line in lines if line.startswith('data: ')]
            if data_lines:
                init_result = json.loads(data_lines[0])
        else:
            init_result = init_response.json()
        
        server_info = init_result.get('result', {}).get('serverInfo', {})
        print(f"   ✅ Server: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
        
        # Step 2: Request tools
        print(f"\n📤 Step 2: Tools List")
        tools_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        tools_response = session.post(gateway_url, json=tools_payload, timeout=15)
        
        print(f"📥 Tools Response:")
        print(f"   Status: {tools_response.status_code}")
        
        if tools_response.status_code != 200:
            print(f"   ❌ Tools request failed: {tools_response.text[:200]}")
            return False
        
        # Parse tools response
        tools_text = tools_response.text
        
        if tools_text.startswith('event:'):
            lines = tools_text.split('\n')
            data_lines = [line.replace('data: ', '') for line in lines if line.startswith('data: ')]
            if data_lines:
                tools_result = json.loads(data_lines[0])
        else:
            tools_result = tools_response.json()
        
        # Get tools
        tools = tools_result.get('result', {}).get('tools', [])
        
        print(f"\n🔧 Tools Available Through Gateway:")
        print(f"   Total: {len(tools)} tools")
        
        if len(tools) == 0:
            print(f"   ⚠️  No tools found")
            print(f"   Full response: {json.dumps(tools_result, indent=2)[:500]}")
            return False
        
        # Display tools
        for i, tool in enumerate(tools[:10], 1):
            name = tool.get('name', 'Unknown')
            description = tool.get('description', 'No description')
            print(f"   {i}. {name}")
            print(f"      {description[:60]}...")
        
        if len(tools) > 10:
            print(f"   ... and {len(tools) - 10} more tools")
        
        print(f"\n✅ Successfully accessed {len(tools)} tools through gateway!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_mcp():
    """Test direct MCP connection for comparison"""
    print("\n🔗 Testing Direct MCP Connection (for comparison)...")
    
    from oauth_manager import create_oauth_token_manager
    
    # Get MCP server URL from environment or use placeholder
    server_url = os.getenv("MCP_SERVER_URL", "https://your-mcp-server.example.com/mcp")
    
    try:
        # Get OAuth token
        token_manager = create_oauth_token_manager()
        token = token_manager.get_token()
        
        session = requests.Session()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        session.headers.update(headers)
        
        # Initialize
        initialize_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "direct-test", "version": "1.0.0"}
            }
        }
        
        init_response = session.post(server_url, json=initialize_payload, timeout=15)
        
        if init_response.status_code != 200:
            print(f"   ❌ Initialize failed: {init_response.status_code}")
            return False
        
        # Get session ID
        session_id = init_response.headers.get('mcp-session-id')
        if session_id:
            session.headers.update({"mcp-session-id": session_id})
        
        # Request tools
        tools_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        tools_response = session.post(server_url, json=tools_payload, timeout=15)
        
        if tools_response.status_code != 200:
            print(f"   ❌ Tools request failed: {tools_response.status_code}")
            return False
        
        # Parse response
        tools_text = tools_response.text
        if tools_text.startswith('event:'):
            lines = tools_text.split('\n')
            data_lines = [line.replace('data: ', '') for line in lines if line.startswith('data: ')]
            if data_lines:
                tools_result = json.loads(data_lines[0])
        else:
            tools_result = tools_response.json()
        
        tools = tools_result.get('result', {}).get('tools', [])
        print(f"   ✅ Found {len(tools)} tools via direct connection")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Testing Gateway HTTP Access to Ansible MCP Tools\n")
    print("="*70)
    
    # Test 1: Direct connection (baseline)
    direct_ok = test_direct_mcp()
    
    # Test 2: Gateway connection
    print("\n" + "="*70)
    gateway_ok = test_gateway_http()
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Results:")
    print(f"   Direct MCP Connection: {'✅ SUCCESS' if direct_ok else '❌ FAILED'}")
    print(f"   Gateway Connection: {'✅ SUCCESS' if gateway_ok else '❌ FAILED'}")
    
    print(f"\n💡 Conclusions:")
    
    if gateway_ok:
        print(f"   🎉 SUCCESS! Gateway provides access to Ansible MCP tools!")
        print(f"   ✅ The gateway is working correctly")
        print(f"   ✅ OAuth authentication (gateway → MCP) is working")
        print(f"   ℹ️  Tools not showing in AWS Console UI is just a display bug")
        print(f"\n🚀 You can now:")
        print(f"   1. Use the gateway URL in your agents")
        print(f"   2. Share the gateway with other teams")
        print(f"   3. Centralize OAuth credential management")
        return 0
    else:
        print(f"   ⚠️  Gateway requires authentication or has issues")
        print(f"   Continue using direct MCP connection for now")
        return 1


if __name__ == "__main__":
    exit(main())
