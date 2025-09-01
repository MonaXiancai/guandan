#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import websockets
import json
import sys
from typing import List, Dict, Any

# 需要安装aioconsole包来处理异步输入
# pip install aioconsole
import aioconsole

class ManualPlayer:
    def __init__(self, player_id: str, client_id: str):
        self.player_id = player_id
        self.client_id = client_id
        self.websocket = None
        self.game_started = False
        self.game_state: Dict[str, Any] = {}  # 存储游戏状态
        self.my_hand: List[str] = []  # 存储自己的手牌
        
    async def connect_to_game(self):
        try:
            uri = "ws://127.0.0.1:8000/api/v1/ws/" + self.client_id
            self.websocket = await websockets.connect(uri)
            print(f"Player {self.player_id} connected to server")
            
            await self.register_player()
            await self.wait_for_game_start()
            await self.play_game()
            
        except Exception as e:
            print(f"Error connecting to game: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
    
    async def register_player(self):
        message = {
            "type": "REGISTER_PLAYER",
            "player_id": self.player_id,
            "client_id": self.client_id
        }
        await self.websocket.send(json.dumps(message))
        print(f"Player {self.player_id} registered")
        
        response = await self.websocket.recv()
        data = json.loads(response)
        if data.get("type") == "PLAYER_REGISTERED":
            print(f"Player {self.player_id} registration confirmed")
        else:
            print(f"Unexpected response: {data}")
    
    async def wait_for_game_start(self):
        print(f"Player {self.player_id} waiting for game to start...")
        
        while not self.game_started:
            try:
                response = await asyncio.wait_for(self.websocket.recv(), timeout=1800.0)
                data = json.loads(response)
                
                print(f"Player {self.player_id} received: {data.get('type')} - {data}")
                
                if data.get("type") == "GAME_STATE_UPDATE":
                    self.update_game_state(data.get("game_state", {}))
                    if self.game_state.get("phase") == "playing":
                        self.game_started = True
                        print(f"Player {self.player_id}: Game started!")
                        self.display_game_status()
                        break
                elif data.get("type") == "PLAYER_JOINED":
                    print(f"Player {data.get('player_id')} joined the game")
                elif data.get("type") == "PLAYER_JOINED_CONFIRMATION":
                    print(f"Player {self.player_id} registration confirmed")
                elif data.get("type") == "CONNECTION_ESTABLISHED":
                    print(f"Player {self.player_id} connection established")
                else:
                    print(f"Player {self.player_id} received: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print(f"Player {self.player_id}: Timeout waiting for game start")
                break
            except Exception as e:
                print(f"Player {self.player_id} error: {e}")
                break
    
    def update_game_state(self, game_state: Dict[str, Any]):
        """更新游戏状态"""
        self.game_state = game_state
        self.my_hand = game_state.get("my_hand", [])
        
    def display_game_status(self):
        """显示游戏状态"""
        if not self.game_state:
            return
            
        print(f"\n=== Player {self.player_id} Game Status ===")
        print(f"Current turn: Player {self.game_state.get('current_turn_index', 0) + 1}")
        print(f"My turn: {'Yes' if self.game_state.get('my_index') == self.game_state.get('current_turn_index') else 'No'}")
        print(f"My hand ({len(self.my_hand)} cards): {self.my_hand}")
        
        # 显示其他玩家的手牌数量
        players = self.game_state.get("players", [])
        for i, player in enumerate(players):
            if player.get('player_id') != self.player_id:
                hand_count = player.get("hand_count", 0)
                print(f"Player {player.get('player_id')} hand count: {hand_count}")
        
        # 显示最后出的牌
        last_hand = self.game_state.get("last_played_hand", [])
        if last_hand:
            print(f"Last played hand: {last_hand}")
        
        print("=" * 40)
    
    async def play_game(self):
        print(f"Player {self.player_id} entering game loop")
        
        while self.game_started:
            try:
                # 检查WebSocket连接状态
                if not self.websocket or self.websocket.closed:
                    print(f"Player {self.player_id}: WebSocket connection lost, exiting game loop")
                    break
                
                # 检查是否轮到自己的回合
                if self.game_state.get('my_index') == self.game_state.get('current_turn_index'):
                    await self.take_my_turn()
                else:
                    print(f"Player {self.player_id}: Waiting for my turn...")
                    await self.wait_for_turn()
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except websockets.exceptions.ConnectionClosed:
                print(f"Player {self.player_id}: WebSocket connection closed, exiting game loop")
                break
            except Exception as e:
                print(f"Player {self.player_id} error in game loop: {e}")
                if "no close frame received or sent" in str(e):
                    print("WebSocket connection issue detected, trying to continue...")
                    await asyncio.sleep(1)  # 短暂等待后继续
                else:
                    print(f"Unexpected error, exiting: {e}")
                    break
    
    async def take_my_turn(self):
        """处理自己的回合"""
        print(f"\nPlayer {self.player_id}: It's my turn!")
        self.display_game_status()
        
        while True:
            try:
                choice = await aioconsole.ainput(f"Player {self.player_id}, choose action:\n"
                             f"1. Play cards (enter card indices separated by space, e.g., '0 1 2')\n"
                             f"2. Pass turn\n"
                             f"Enter choice (1 or 2): ")
                choice = choice.strip()
                
                if choice == "1":
                    await self.play_cards()
                    break
                elif choice == "2":
                    await self.pass_turn()
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                return
            except Exception as e:
                print(f"Error: {e}")
    
    async def play_cards(self):
        """出牌"""
        if not self.my_hand:
            print("No cards in hand!")
            return
            
        print(f"Player {self.player_id} playing cards")
        print(f"Your hand: {self.my_hand}")
        
        # 让用户选择要出的牌
        card_input = await aioconsole.ainput("Enter card indices (0-based, space separated, e.g., '0 1 2'): ")
        card_input = card_input.strip()
        if not card_input:
            print("No cards selected")
            return
            
        try:
            indices = [int(x) for x in card_input.split()]
            if all(0 <= i < len(self.my_hand) for i in indices):
                selected_cards = [self.my_hand[i] for i in indices]
                print(f"Playing cards: {selected_cards}")
                
                message = {
                    "type": "PLAY_CARDS",
                    "cards": selected_cards
                }
                await self.websocket.send(json.dumps(message))
                print(f"Player {self.player_id}: Sent PLAY_CARDS message")
                
                # 等待响应
                await self.wait_for_response()
                
            else:
                print("Invalid card indices. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter numbers separated by spaces.")
    
    async def pass_turn(self):
        """过牌"""
        print(f"Player {self.player_id} passing turn")
        
        message = {
            "type": "PASS_TURN"
        }
        await self.websocket.send(json.dumps(message))
        print(f"Player {self.player_id}: Sent PASS_TURN message")
        
        # 等待响应
        await self.wait_for_response()
    
    async def wait_for_turn(self):
        """等待轮到自己的回合"""
        print(f"Player {self.player_id}: Waiting for turn...")
        
        try:
            response = await asyncio.wait_for(self.websocket.recv(), timeout=1800.0)
            data = json.loads(response)
            print(f"Player {self.player_id} received: {data.get('type')}")
            
            if data.get("type") == "GAME_STATE_UPDATE":
                self.update_game_state(data.get("game_state", {}))
                print("Game state updated")
            elif data.get("type") == "GAME_ENDED":
                print(f"Player {self.player_id}: Game ended - {data.get('message')}")
                self.game_started = False
                return
            elif data.get("type") in ["PLAY_CARDS_SUCCESS", "PASS_TURN_SUCCESS"]:
                print(f"Player {self.player_id}: Action successful - {data.get('message')}")
                
            # 继续等待可能的后续消息
            try:
                while True:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    print(f"Player {self.player_id} received additional message: {data.get('type')}")
                    
                    if data.get("type") == "GAME_STATE_UPDATE":
                        self.update_game_state(data.get("game_state", {}))
                        print("Additional game state update received")
                    elif data.get("type") == "GAME_ENDED":
                        print(f"Player {self.player_id}: Game ended - {data.get('message')}")
                        self.game_started = False
                        return
                        
            except asyncio.TimeoutError:
                # 没有更多消息，正常退出
                pass
                
        except asyncio.TimeoutError:
            print(f"Player {self.player_id}: Timeout waiting for turn")
        except websockets.exceptions.ConnectionClosed:
            print(f"Player {self.player_id}: WebSocket connection closed when waiting for turn")
            self.game_started = False
        except Exception as e:
            print(f"Player {self.player_id} error waiting for turn: {e}")
            if "no close frame received or sent" in str(e):
                print("WebSocket connection issue detected, continuing...")
            else:
                print(f"Unexpected error: {e}")
    
    async def wait_for_response(self):
        """等待服务器响应"""
        try:
            # 等待第一个响应消息
            response = await asyncio.wait_for(self.websocket.recv(), timeout=1800.0)
            data = json.loads(response)
            print(f"Player {self.player_id} received response: {data}")
            
            # 处理第一个消息
            if data.get("type") == "GAME_STATE_UPDATE":
                self.update_game_state(data.get("game_state", {}))
                print("Game state updated after action")
            elif data.get("type") == "GAME_ENDED":
                print(f"Player {self.player_id}: Game ended - {data.get('message')}")
                self.game_started = False
                return
            elif data.get("type") in ["PLAY_CARDS_SUCCESS", "PASS_TURN_SUCCESS"]:
                print(f"Player {self.player_id}: Action successful - {data.get('message')}")
            
            # 继续等待可能的后续消息（比如GAME_STATE_UPDATE）
            try:
                while True:
                    # 使用较短的超时时间检查是否有更多消息
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    data = json.loads(response)
                    print(f"Player {self.player_id} received additional response: {data}")
                    
                    if data.get("type") == "GAME_STATE_UPDATE":
                        self.update_game_state(data.get("game_state", {}))
                        print("Additional game state update received")
                    elif data.get("type") == "GAME_ENDED":
                        print(f"Player {self.player_id}: Game ended - {data.get('message')}")
                        self.game_started = False
                        return
                        
            except asyncio.TimeoutError:
                # 没有更多消息，正常退出
                pass
                
        except asyncio.TimeoutError:
            print(f"Player {self.player_id}: Timeout waiting for response")
        except websockets.exceptions.ConnectionClosed:
            print(f"Player {self.player_id}: WebSocket connection closed waiting for response")
            self.game_started = False
        except Exception as e:
            print(f"Player {self.player_id} error waiting for response: {e}")
            if "no close frame received or sent" in str(e):
                print("WebSocket connection issue detected, continuing...")
            else:
                print(f"Unexpected error: {e}")

async def main():
    if len(sys.argv) != 2:
        print("Usage: python test_manual_play.py <player_number>")
        print("Example: python test_manual_play.py 1")
        return
    
    try:
        player_num = int(sys.argv[1])
        if player_num < 1 or player_num > 4:
            print("Player number must be between 1 and 4")
            return
    except ValueError:
        print("Player number must be a number")
        return
    
    player_id = f"player_{player_num}"
    client_id = f"test_client_{player_num}"
    
    print(f"Starting manual player {player_num}")
    print(f"Player ID: {player_id}")
    print(f"Client ID: {client_id}")
    print("Make sure the server is running on http://127.0.0.1:8000")
    print("Press Ctrl+C to exit")
    
    player = ManualPlayer(player_id, client_id)
    await player.connect_to_game()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
