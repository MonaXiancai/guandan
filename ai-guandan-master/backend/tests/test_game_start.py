#!/usr/bin/env python3
"""
测试游戏开始和状态广播功能
"""

import asyncio
import websockets
import json
import time

async def test_game_start():
    """测试游戏开始功能"""
    print("Starting game start test...")
    
    # 创建4个客户端连接
    clients = []
    client_ids = [f"client_{i}" for i in range(4)]
    
    try:
        # 连接4个客户端
        for i, client_id in enumerate(client_ids):
            print(f"Connecting client {i+1}: {client_id}")
            websocket = await websockets.connect(f"ws://127.0.0.1:8000/api/v1/ws/{client_id}")
            clients.append(websocket)
            
            # 等待连接确认
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Client {i+1} connected: {data}")
            
            # 注册玩家
            player_id = f"player_{i+1}"
            register_message = {
                "type": "REGISTER_PLAYER",
                "player_id": player_id
            }
            
            print(f"Registering player: {player_id}")
            await websocket.send(json.dumps(register_message))
            
            # 等待注册确认
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Player registration response: {data}")
            
            # 等待玩家加入确认
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Player join confirmation: {data}")
            
            # 等待玩家加入广播（如果有其他玩家的话）
            if i > 0:  # 不是第一个玩家
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"Player join broadcast: {data}")
                    
                    # 如果这是第4个玩家，检查是否已经收到游戏状态更新
                    if i == 3 and data.get("type") == "GAME_STATE_UPDATE":
                        game_state = data.get("game_state", {})
                        print(f"Game started successfully!")
                        print(f"Game ID: {game_state.get('game_id')}")
                        print(f"Current Level: {game_state.get('current_level')}")
                        print(f"Phase: {game_state.get('phase')}")
                        print(f"Players: {len(game_state.get('players', []))}")
                        
                        # 检查手牌
                        my_hand = game_state.get("my_hand", [])
                        print(f"My hand ({len(my_hand)} cards): {my_hand[:5]}...")  # 只显示前5张
                        
                        return True
                        
                except asyncio.TimeoutError:
                    print("No broadcast message received (expected for first player)")
            
            # 如果这是第4个玩家且还没有收到游戏状态更新，等待游戏开始
            if i == 3:
                print("Waiting for game start...")
                try:
                    # 等待游戏状态更新
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    print(f"Game state update: {data}")
                    
                    if data.get("type") == "GAME_STATE_UPDATE":
                        game_state = data.get("game_state", {})
                        print(f"Game started successfully!")
                        print(f"Game ID: {game_state.get('game_id')}")
                        print(f"Current Level: {game_state.get('current_level')}")
                        print(f"Phase: {game_state.get('phase')}")
                        print(f"Players: {len(game_state.get('players', []))}")
                        
                        # 检查手牌
                        my_hand = game_state.get("my_hand", [])
                        print(f"My hand ({len(my_hand)} cards): {my_hand[:5]}...")  # 只显示前5张
                        
                        return True
                    else:
                        print(f"Unexpected message type: {data.get('type')}")
                        return False
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for game state update")
                    return False
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
        
    finally:
        # 关闭所有连接
        for websocket in clients:
            await websocket.close()
        print("All connections closed")

async def main():
    """主函数"""
    print("=" * 50)
    print("Testing Game Start and State Broadcast")
    print("=" * 50)
    
    success = await test_game_start()
    
    print("\n" + "=" * 50)
    if success:
        print("Test PASSED: Game start and state broadcast working correctly!")
    else:
        print("Test FAILED: Issues with game start or state broadcast")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
