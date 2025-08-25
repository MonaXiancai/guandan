#!/usr/bin/env python3
"""
WebSocket connection test script
Used to verify that WebSocket endpoints are working properly
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test WebSocket connection"""
    uri = "ws://127.0.0.1:8000/api/v1/ws/test_client_1"
    
    try:
        print(f"Connecting to: {uri}")
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接成功!")
            
            # Wait for connection success message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Received server message: {data}")
                
                if data.get("type") == "CONNECTION_ESTABLISHED":
                    print("Connection establishment confirmed!")
                else:
                    print(f"Received unexpected message type: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("Timeout waiting for connection confirmation message")
            
            # Test sending player registration message
            register_message = {
                "type": "REGISTER_PLAYER",
                "player_id": "player_1"
            }
            
            print(f"Sending player registration message: {register_message}")
            await websocket.send(json.dumps(register_message))
            
            # Wait for registration confirmation
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Received registration confirmation: {data}")
                
                if data.get("type") == "PLAYER_REGISTERED":
                    print(" Player registration successful!")
                else:
                    print(f" Received unexpected registration response: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("Timeout waiting for registration confirmation")
            
            # Test heartbeat
            ping_message = {
                "type": "PING",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            print(f"Sending heartbeat message: {ping_message}")
            await websocket.send(json.dumps(ping_message))
            
            # Wait for heartbeat response
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Received heartbeat response: {data}")
                
                if data.get("type") == "PONG":
                    print("Heartbeat test successful!")
                else:
                    print(f" Received unexpected heartbeat response: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("Timeout waiting for heartbeat response")
                
            print("WebSocket functionality test completed!")
            
    except websockets.exceptions.ConnectionRefused:
        print("Connection refused, please ensure server is running")
        print("Start command: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
    except Exception as e:
        print(f"Connection failed: {e}")
        return False
    
    return True

async def test_http_endpoints():
    """Test HTTP endpoints"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test root endpoint
            async with session.get("http://127.0.0.1:8000/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f" Root endpoint test successful: {data}")
                else:
                    print(f" Root endpoint test failed: {response.status}")
            
            # Test health check endpoint
            async with session.get("http://127.0.0.1:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f" Health check endpoint test successful: {data}")
                else:
                    print(f" Health check endpoint test failed: {response.status}")
            
            # Test connections endpoint
            async with session.get("http://127.0.0.1:8000/connections") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Connections endpoint test successful: {data}")
                else:
                    print(f"Connections endpoint test failed: {response.status}")
                    
    except Exception as e:
        print(f" HTTP endpoints test failed: {e}")

async def main():
    """Main function"""
    print("Starting Guandan Masters API test...")
    print("=" * 50)
    
    # Test HTTP endpoints
    print("\nTesting HTTP endpoints...")
    await test_http_endpoints()
    
    # Test WebSocket endpoints
    print("\nTesting WebSocket endpoints...")
    success = await test_websocket_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("All tests completed!")
    else:
        print("Some tests failed")

if __name__ == "__main__":
    asyncio.run(main())
