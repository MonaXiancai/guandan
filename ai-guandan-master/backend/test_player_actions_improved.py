#!/usr/bin/env python3
"""
掼蛋游戏玩家测试脚本
每个脚本代表一个玩家，通过命令行参数指定玩家ID
使用方法: python test_player_actions_improved.py <player_id>
例如: python test_player_actions_improved.py 1
"""

import asyncio
import websockets
import json
import time
import sys
import random
from typing import List, Dict, Optional

class GuandanPlayer:
    """掼蛋游戏玩家类"""
    
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.client_id = f"client_{player_id - 1}"
        self.websocket = None
        self.game_state = None
        self.my_hand = []
        self.my_index = -1
        self.my_team = -1
        self.is_my_turn = False
        self.game_started = False
        
    async def connect_to_game(self):
        """连接到游戏服务器"""
        try:
            print(f"🎮 Player {self.player_id} connecting to game server...")
            
            # 连接WebSocket
            self.websocket = await websockets.connect(f"ws://127.0.0.1:8000/api/v1/ws/{self.client_id}")
            
            # 等待连接确认
            message = await self.websocket.recv()
            data = json.loads(message)
            print(f"✅ Connected: {data.get('message', '')}")
            
            # 注册玩家
            await self.register_player()
            
            # 等待游戏开始
            await self.wait_for_game_start()
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def register_player(self):
        """注册玩家"""
        register_message = {
            "type": "REGISTER_PLAYER",
            "player_id": f"player_{self.player_id}"
        }
        
        print(f"📝 Registering as player_{self.player_id}...")
        await self.websocket.send(json.dumps(register_message))
        
        # 等待注册确认
        message = await self.websocket.recv()
        data = json.loads(message)
        print(f"✅ Registration: {data.get('message', '')}")
        
        # 等待玩家加入确认
        message = await self.websocket.recv()
        data = json.loads(message)
        print(f"🎯 Player joined: {data.get('message', '')}")
        
        # 等待其他玩家加入广播（如果不是第一个玩家）
        if self.player_id > 1:
            try:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📢 Broadcast: {data.get('type', '')}")
            except asyncio.TimeoutError:
                print("⏰ No broadcast message received")
    
    async def wait_for_game_start(self):
        """等待游戏开始"""
        print("⏳ Waiting for game to start...")
        
        while not self.game_started:
            try:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=10.0)
                data = json.loads(message)
                
                if data.get("type") == "GAME_STATE_UPDATE":
                    self.game_started = True
                    self.update_game_state(data.get("game_state", {}))
                    print(f"🎉 Game started! I am player_{self.my_index + 1} (team {self.my_team})")
                    print(f"🃏 My hand: {len(self.my_hand)} cards")
                    break
                else:
                    print(f"📨 Received: {data.get('type', '')}")
                    
            except asyncio.TimeoutError:
                print("⏰ Still waiting for game start...")
    
    async def play_game(self):
        """开始游戏循环"""
        print("🚀 Starting game loop...")
        
        try:
            while self.game_started:
                # 检查是否是我的回合
                if self.is_my_turn:
                    await self.take_my_turn()
                    # 行动后等待状态更新
                    await self.wait_for_state_update()
                else:
                    # 等待其他玩家的动作
                    await self.wait_for_other_players()
                
                # 短暂延迟
                await asyncio.sleep(0.5)
                
        except Exception as e:
            print(f"❌ Game loop error: {e}")
    
    async def take_my_turn(self):
        """执行我的回合"""
        print(f"🎯 My turn! I have {len(self.my_hand)} cards")
        
        if not self.my_hand:
            print("🃏 No cards left, passing turn")
            await self.pass_turn()
            return
        
        # 简单的AI决策：随机选择出牌或过牌
        if random.random() < 0.7:  # 70%概率出牌
            await self.play_cards()
        else:
            await self.pass_turn()
    
    async def play_cards(self):
        """出牌"""
        if not self.my_hand:
            print("❌ No cards to play")
            return
        
        # 选择要出的牌（第一张）
        cards_to_play = [self.my_hand[0]]
        print(f"🃏 Playing cards: {cards_to_play}")
        
        # 临时从手牌中移除（等待服务器确认）
        temp_hand = self.my_hand[1:]  # 移除第一张牌
        print(f"🃏 Temporary hand after play: {len(temp_hand)} cards")
        
        play_message = {
            "type": "PLAY_CARDS",
            "cards": cards_to_play
        }
        
        await self.websocket.send(json.dumps(play_message))
        print("📤 Play cards message sent")
        
        # 注意：手牌的实际更新需要等待服务器响应
    
    async def pass_turn(self):
        """过牌"""
        print("⏭️ Passing turn")
        
        pass_message = {
            "type": "PASS_TURN"
        }
        
        await self.websocket.send(json.dumps(pass_message))
        print("📤 Pass turn message sent")
    
    async def wait_for_other_players(self):
        """等待其他玩家的动作"""
        try:
            # 等待游戏状态更新
            message = await asyncio.wait_for(self.websocket.recv(), timeout=2.0)
            data = json.loads(message)
            
            if data.get("type") == "GAME_STATE_UPDATE":
                self.update_game_state(data.get("game_state", {}))
                
                # 检查游戏是否结束
                if self.check_game_end():
                    print("🏁 Game ended!")
                    self.game_started = False
                    return
                
                # 检查是否轮到我了
                if self.is_my_turn:
                    print("🎯 Now it's my turn!")
                else:
                    current_turn_index = self.game_state.get("current_turn_index", -1)
                    current_player = f"player_{current_turn_index + 1}"
                    print(f"👀 {current_player} is playing...")
                    
            elif data.get("type") == "PLAYER_FINISHED":
                player_id = data.get("player_id", "")
                print(f"🏆 {player_id} has finished the round!")
                
            elif data.get("type") == "PLAY_CARDS_SUCCESS":
                print(f"✅ My play cards action was successful")
                
            elif data.get("type") == "PASS_TURN_SUCCESS":
                print(f"✅ My pass turn action was successful")
                
            else:
                print(f"📨 Received: {data.get('type', '')}")
                
        except asyncio.TimeoutError:
            # 超时是正常的，继续等待
            pass
    
    async def wait_for_state_update(self):
        """等待状态更新（行动后调用）"""
        print("⏳ Waiting for state update after my action...")
        
        try:
            # 等待游戏状态更新
            message = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
            data = json.loads(message)
            
            if data.get("type") == "GAME_STATE_UPDATE":
                self.update_game_state(data.get("game_state", {}))
                print("✅ State updated after my action")
            else:
                print(f"📨 Received after action: {data.get('type', '')}")
                
        except asyncio.TimeoutError:
            print("⏰ Timeout waiting for state update after action")
    
    def update_game_state(self, game_state: Dict):
        """更新游戏状态"""
        self.game_state = game_state
        self.my_index = game_state.get("my_index", -1)
        self.my_team = game_state.get("my_team", -1)
        
        # 更新我的手牌
        old_hand_size = len(self.my_hand)
        self.my_hand = game_state.get("my_hand", [])
        new_hand_size = len(self.my_hand)
        
        if old_hand_size != new_hand_size:
            print(f"🃏 Hand updated: {old_hand_size} -> {new_hand_size} cards")
        
        # 检查是否是我的回合
        current_turn_index = game_state.get("current_turn_index", -1)
        was_my_turn = self.is_my_turn
        self.is_my_turn = (current_turn_index == self.my_index)
        
        if self.is_my_turn and not was_my_turn:
            print(f"🎯 It's my turn! (index {self.my_index})")
        elif not self.is_my_turn and was_my_turn:
            print(f"⏸️ Turn passed to player_{current_turn_index + 1}")
        elif not self.is_my_turn:
            current_player = f"player_{current_turn_index + 1}"
            print(f"👀 Waiting for {current_player}'s turn...")
    
    def check_game_end(self) -> bool:
        """检查游戏是否结束"""
        if not self.game_state:
            return False
        
        # 检查是否有玩家出完牌
        players = self.game_state.get("players", [])
        finished_players = [p for p in players if p.get("is_finished", False)]
        
        if len(finished_players) > 0:
            print(f"🏁 {len(finished_players)} players have finished!")
            return True
        
        return False
    
    async def close_connection(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 Connection closed")

async def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("Usage: python test_player_actions_improved.py <player_id>")
        print("Example: python test_player_actions_improved.py 1")
        return
    
    try:
        player_id = int(sys.argv[1])
        if player_id < 1 or player_id > 4:
            print("Player ID must be between 1 and 4")
            return
    except ValueError:
        print("Player ID must be a number")
        return
    
    print("=" * 60)
    print(f"🎮 Guandan Player {player_id} Test Script")
    print("=" * 60)
    
    # 创建玩家实例
    player = GuandanPlayer(player_id)
    
    try:
        # 连接到游戏
        if not await player.connect_to_game():
            print("❌ Failed to connect to game")
            return
        
        # 开始游戏
        await player.play_game()
        
    except KeyboardInterrupt:
        print("\n⏹️ Game interrupted by user")
    except Exception as e:
        print(f"❌ Game error: {e}")
    finally:
        await player.close_connection()
        print("👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
