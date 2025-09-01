from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Optional
import json
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket连接管理器
    负责管理所有活跃的WebSocket连接，包括添加、移除和广播消息
    """
    
    def __init__(self):
        # 存储所有活跃连接，key为client_id，value为WebSocket实例
        self.active_connections: Dict[str, WebSocket] = {}
        # 存储客户端ID到玩家ID的映射
        self.client_to_player: Dict[str, str] = {}
        # 存储玩家ID到客户端ID的映射
        self.player_to_client: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        接受新的WebSocket连接
        
        Args:
            websocket: WebSocket连接实例
            client_id: 客户端唯一标识
        """
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            logger.info(f"Client {client_id} connected")
        except Exception as e:
            logger.error(f"Failed to accept connection: {e}")
            raise
    
    def disconnect(self, client_id: str):
        """
        断开WebSocket连接
        
        Args:
            client_id: 客户端唯一标识
        """
        if client_id in self.active_connections:
            # 获取玩家ID（如果已注册）
            player_id = None
            if client_id in self.client_to_player:
                player_id = self.client_to_player[client_id]
            
            # 清理连接
            del self.active_connections[client_id]
            
            # 清理映射关系
            if player_id:
                del self.client_to_player[client_id]
                if player_id in self.player_to_client:
                    del self.player_to_client[player_id]
            
            logger.info(f"Client {client_id} disconnected")
            
            # 检查是否需要结束游戏
            if player_id and self._should_end_game():
                self._end_game_due_to_disconnection(player_id)
    
    def register_player(self, client_id: str, player_id: str):
        """
        注册客户端与玩家的映射关系
        
        Args:
            client_id: 客户端唯一标识
            player_id: 玩家唯一标识
        """
        self.client_to_player[client_id] = player_id
        self.player_to_client[player_id] = client_id
        logger.info(f"Client {client_id} registered as player {player_id}")
    
    def get_player_id(self, client_id: str) -> str:
        """
        根据客户端ID获取玩家ID
        
        Args:
            client_id: 客户端唯一标识
            
        Returns:
            玩家ID，如果未找到则返回None
        """
        return self.client_to_player.get(client_id)
    
    def get_client_id(self, player_id: str) -> str:
        """
        根据玩家ID获取客户端ID
        
        Args:
            player_id: 玩家唯一标识
            
        Returns:
            客户端ID，如果未找到则返回None
        """
        return self.player_to_client.get(player_id)
    
    async def send_personal_message(self, message: dict, client_id: str):
        """
        向特定客户端发送个人消息
        
        Args:
            message: 要发送的消息字典
            client_id: 目标客户端ID
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"Failed to send message to client {client_id}: {e}")
                # Disconnect on send failure
                self.disconnect(client_id)
    
    async def send_personal_message_to_player(self, message: dict, player_id: str):
        """
        向特定玩家发送个人消息
        
        Args:
            message: 要发送的消息字典
            player_id: 目标玩家ID
        """
        client_id = self.get_client_id(player_id)
        if client_id:
            await self.send_personal_message(message, client_id)
    
    async def broadcast(self, message: dict, exclude_client_id: str = None):
        """
        向所有连接的客户端广播消息
        
        Args:
            message: 要广播的消息字典
            exclude_client_id: 要排除的客户端ID（可选）
        """
        disconnected_clients = []
        
        for client_id, connection in self.active_connections.items():
            if client_id != exclude_client_id:
                try:
                    await connection.send_text(json.dumps(message, ensure_ascii=False))
                except Exception as e:
                    logger.error(f"Failed to broadcast message to client {client_id}: {e}")
                    disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_to_players(self, message: dict, player_ids: List[str], exclude_player_id: str = None):
        """
        向指定的玩家列表广播消息
        
        Args:
            message: 要广播的消息字典
            player_ids: 目标玩家ID列表
            exclude_player_id: 要排除的玩家ID（可选）
        """
        for player_id in player_ids:
            if player_id != exclude_player_id:
                await self.send_personal_message_to_player(message, player_id)
    
    def get_connected_players(self) -> List[str]:
        """
        获取所有已连接的玩家ID列表
        
        Returns:
            玩家ID列表
        """
        return list(self.player_to_client.keys())
    
    def get_connection_count(self) -> int:
        """
        获取当前连接数
        
        Returns:
            活跃连接数量
        """
        return len(self.active_connections)
    
    def is_connected(self, client_id: str) -> bool:
        """
        检查指定客户端是否已连接
        
        Args:
            client_id: 客户端ID
            
        Returns:
            如果已连接返回True，否则返回False
        """
        return client_id in self.active_connections
    
    def is_player_connected(self, player_id: str) -> bool:
        """
        检查指定玩家是否已连接
        
        Args:
            player_id: 玩家ID
            
        Returns:
            如果已连接返回True，否则返回False
        """
        return player_id in self.player_to_client
    
    # 游戏管理相关方法
    def get_game_id(self) -> str:
        """获取当前游戏ID"""
        return getattr(self, '_game_id', None)
    
    def set_game_id(self, game_id: str):
        """设置当前游戏ID"""
        self._game_id = game_id
    
    def get_game_state(self):
        """获取当前游戏状态"""
        from app.main import game_engine
        game_id = self.get_game_id()
        if game_id and game_engine:
            return game_engine.get_game_state(game_id)
        return None
    
    def should_start_game(self) -> bool:
        """检查是否应该开始游戏（4个玩家连接且注册）"""
        connections = len(self.active_connections)
        players = len(self.client_to_player)
        logger.info(f"Should start game check: connections={connections}, players={players}")
        return connections == 4 and players == 4
    
    def get_connected_players_info(self) -> List[Dict[str, str]]:
        """获取已连接玩家的信息列表"""
        players_info = []
        for client_id, player_id in self.client_to_player.items():
            players_info.append({
                "client_id": client_id,
                "player_id": player_id
            })
        return players_info
    
    def get_last_played_hand(self):
        """获取上家最后出的牌"""
        game_state = self.get_game_state()
        if game_state and hasattr(game_state, 'last_played_hand'):
            # 转换为字符串列表，避免JSON序列化问题
            return [str(card) for card in game_state.last_played_hand] if game_state.last_played_hand else []
        return []

    def _should_end_game(self) -> bool:
        """
        检查是否应该结束游戏
        
        Returns:
            True如果应该结束游戏，否则False
        """
        # 如果有游戏ID且连接数少于4个，说明有玩家断线
        return (self.get_game_id() is not None and 
                len(self.active_connections) < 4)
    
    def _end_game_due_to_disconnection(self, disconnected_player_id: str):
        """
        由于玩家断线而结束游戏
        
        Args:
            disconnected_player_id: 断线的玩家ID
        """
        try:
            # 获取游戏状态
            game_state = self.get_game_state()
            if not game_state:
                logger.warning("No game state available for ending game")
                return
            
            # 广播游戏结束消息
            import asyncio
            asyncio.create_task(self._broadcast_game_end(disconnected_player_id))
            
            # 清理游戏状态
            self._cleanup_game_state()
            
            logger.info(f"Game ended due to player {disconnected_player_id} disconnection")
            
        except Exception as e:
            logger.error(f"Error ending game due to disconnection: {e}")
    
    async def _broadcast_game_end(self, disconnected_player_id: str):
        """
        广播游戏结束消息
        
        Args:
            disconnected_player_id: 断线的玩家ID
        """
        try:
            # 向所有剩余连接的客户端广播游戏结束消息
            await self.broadcast({
                "type": "GAME_ENDED",
                "reason": "player_disconnected",
                "disconnected_player_id": disconnected_player_id,
                "message": f"Game ended because player {disconnected_player_id} disconnected"
            })
            
            logger.info(f"Game end message broadcasted due to player {disconnected_player_id} disconnection")
            
        except Exception as e:
            logger.error(f"Error broadcasting game end message: {e}")
    
    def _cleanup_game_state(self):
        """
        清理游戏状态
        """
        try:
            # 获取当前游戏ID
            game_id = self.get_game_id()
            if game_id:
                # 从游戏引擎中移除游戏
                from app.main import game_engine
                if game_engine.remove_game(game_id):
                    logger.info(f"Successfully removed game {game_id} from game engine")
                else:
                    logger.warning(f"Failed to remove game {game_id} from game engine")
                
                # 清除连接管理器中的游戏ID
                self._game_id = None
                logger.info(f"Cleaned up game state for game {game_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up game state: {e}")

# 全局连接管理器实例
connection_manager = ConnectionManager()

async def start_new_game() -> Optional[str]:
    """
    开始新游戏
    
    Returns:
        游戏ID，如果失败则返回None
    """
    try:
        from app.main import game_engine
        
        # 获取已连接的玩家信息
        players_info = connection_manager.get_connected_players_info()
        
        # 添加调试日志
        logger.info(f"Active connections: {len(connection_manager.active_connections)}")
        logger.info(f"Registered players: {len(connection_manager.client_to_player)}")
        logger.info(f"Players info: {players_info}")
        
        # 检查是否有足够的玩家
        if len(players_info) != 4:
            logger.error(f"Expected 4 players, but got {len(players_info)}")
            return None
        
        # 生成游戏ID
        game_id = str(uuid.uuid4())
        
        # 创建Player对象
        from app.game_logic.player import Player, PlayerType
        players = []
        for i, info in enumerate(players_info):
            player = Player(
                player_id=info["player_id"],
                name=f"Player_{info['player_id']}",
                player_type=PlayerType.HUMAN if i == 0 else PlayerType.AI,  # 第一个玩家是人类，其他是AI
                team=i % 2
            )
            players.append(player)
        
        # 开始新游戏
        game_state = game_engine.start_new_game(game_id, players, current_level=2)
        
        # 设置连接管理器的游戏ID
        connection_manager.set_game_id(game_id)
        
        # 处理进贡阶段（首局无进贡，直接进入游戏阶段）
        try:
            tribute_result = game_engine.process_tribute_phase(game_id)
            if tribute_result.get("success"):
                logger.info(f"Tribute phase processed: {tribute_result.get('message')}")
            else:
                logger.warning(f"Tribute phase processing failed: {tribute_result.get('error')}")
        except Exception as e:
            logger.error(f"Error processing tribute phase: {e}")
        
        logger.info(f"New game started with ID: {game_id}")
        return game_id
        
    except Exception as e:
        logger.error(f"Failed to start new game: {e}")
        return None

async def broadcast_game_state():
    """
    广播游戏状态给所有客户端
    为每个玩家生成定制化的状态（隐藏他人手牌）
    """
    try:
        game_state = connection_manager.get_game_state()
        if not game_state:
            logger.warning("No game state available for broadcasting")
            return
        
        # 为每个玩家生成定制化的状态
        for i, player in enumerate(game_state.players):
            client_id = connection_manager.get_client_id(player.player_id)
            if not client_id:
                continue
            
            # 创建定制化的游戏状态
            personalized_state = create_personalized_game_state(game_state, i)
            
            # 发送给玩家
            await connection_manager.send_personal_message({
                "type": "GAME_STATE_UPDATE",
                "game_state": personalized_state
            }, client_id)
        
        logger.info("Game state broadcasted to all players")
        
    except Exception as e:
        logger.error(f"Failed to broadcast game state: {e}")

def create_personalized_game_state(game_state, player_index: int) -> dict:
    """
    为指定玩家创建定制化的游戏状态
    
    Args:
        game_state: 游戏状态对象
        player_index: 玩家索引
        
    Returns:
        定制化的游戏状态字典
    """
    try:
        # 基础游戏信息
        personalized_state = {
            "game_id": game_state.game_id,
            "current_level": game_state.current_level,
            "phase": game_state.phase.value if hasattr(game_state.phase, 'value') else str(game_state.phase),
            "current_turn_index": game_state.current_turn_index,
            "round_number": game_state.round_number,
            "turn_number": game_state.turn_number,
            "my_index": player_index,
            "my_team": game_state.players[player_index].team,
            "my_hand": [str(card) for card in game_state.players[player_index].hand],
            "players": []
        }
        
        # 其他玩家信息（隐藏手牌）
        for i, player in enumerate(game_state.players):
            player_info = {
                "player_id": player.player_id,
                "name": player.name,
                "team": player.team,
                "is_finished": player.is_finished,
                "hand_count": len(player.hand) if i == player_index else 0,  # 只显示自己的手牌数量
                "is_current_turn": i == game_state.current_turn_index
            }
            personalized_state["players"].append(player_info)
        
        # 当前回合信息
        if game_state.last_played_hand:
            personalized_state["last_played_hand"] = [str(card) for card in game_state.last_played_hand]
        if game_state.last_player_id:
            personalized_state["last_player_id"] = game_state.last_player_id
        
        return personalized_state
        
    except Exception as e:
        logger.error(f"Failed to create personalized game state: {e}")
        return {"error": "Failed to create game state"}

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket端点，处理客户端连接和消息
    
    Args:
        websocket: WebSocket连接实例
        client_id: 客户端唯一标识
    """
    try:
        # 接受连接
        await connection_manager.connect(websocket, client_id)
        
        # 发送连接成功消息
        await connection_manager.send_personal_message({
            "type": "CONNECTION_ESTABLISHED",
            "client_id": client_id,
            "message": "Connection established successfully"
        }, client_id)
        
        logger.info(f"Client {client_id} connected successfully, current connections: {connection_manager.get_connection_count()}")
        
        # 游戏启动检查移到玩家注册后，这里不需要检查
        
        # 消息处理循环
        try:
            while True:
                # 接收客户端消息
                data = await websocket.receive_text()
                message = json.loads(data)
                
                logger.info(f"Received message from client {client_id}: {message}")
                
                # 处理不同类型的消息
                await handle_client_message(client_id, message)
                
        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error processing message from client {client_id}: {e}")
            
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection: {e}")
    finally:
        # Clean up connection
        connection_manager.disconnect(client_id)
        logger.info(f"Client {client_id} connection cleaned up, current connections: {connection_manager.get_connection_count()}")

async def handle_client_message(client_id: str, message: dict):
    """
    处理客户端消息
    
    Args:
        client_id: 客户端ID
        message: 消息内容
    """
    message_type = message.get("type")
    
    if message_type == "REGISTER_PLAYER":
        # 注册玩家
        player_id = message.get("player_id")
        if player_id:
            connection_manager.register_player(client_id, player_id)
            await connection_manager.send_personal_message({
                "type": "PLAYER_REGISTERED",
                "player_id": player_id,
                "message": "Player registered successfully"
            }, client_id)
            
            # Send confirmation to current client that they joined
            await connection_manager.send_personal_message({
                "type": "PLAYER_JOINED_CONFIRMATION",
                "player_id": player_id,
                "message": f"You have joined the game as {player_id}",
                "total_players": len(connection_manager.client_to_player)
            }, client_id)
            
            # Broadcast player join message to other clients (if any)
            if len(connection_manager.active_connections) > 1:
                await connection_manager.broadcast({
                    "type": "PLAYER_JOINED",
                    "player_id": player_id,
                    "message": f"Player {player_id} has joined the game"
                }, exclude_client_id=client_id)
            
            # 检查是否应该开始游戏
            if connection_manager.should_start_game():
                logger.info("4 players registered, starting new game...")
                game_id = await start_new_game()
                if game_id:
                    # 然后广播游戏状态更新（异步执行，不阻塞当前响应）
                    import asyncio
                    asyncio.create_task(broadcast_game_state())
                else:
                    logger.error("Failed to start new game, cannot broadcast game state")
    
    elif message_type == "PLAY_CARDS":
        # 处理玩家出牌
        player_id = connection_manager.get_player_id(client_id)
        if not player_id:
            await connection_manager.send_personal_message({
                "type": "ERROR",
                "message": "Player not registered"
            }, client_id)
            return
        
        # 获取要出的牌
        cards_data = message.get("cards", [])
        if not cards_data:
            await connection_manager.send_personal_message({
                "type": "ERROR",
                "message": "No cards specified for play"
            }, client_id)
            return
        
        # 解析牌数据
        try:
            from app.game_logic.card import Card, Rank, Suit
            cards = []
            for card_str in cards_data:
                # 解析牌字符串，例如 "S7" -> Card(Rank.SEVEN, Suit.SPADE)
                if card_str == "BIG_JOKER":
                    cards.append(Card(Rank.BIG_JOKER, Suit.JOKER))
                elif card_str == "SMALL_JOKER":
                    cards.append(Card(Rank.SMALL_JOKER, Suit.JOKER))
                else:
                    # 解析普通牌，格式: "S7" (花色+点数)
                    suit_char = card_str[0]
                    rank_char = card_str[1:]
                    
                    # 映射花色
                    suit_map = {"S": Suit.SPADE, "H": Suit.HEART, "D": Suit.DIAMOND, "C": Suit.CLUB}
                    suit = suit_map.get(suit_char)
                    
                    # 映射点数
                    rank_map = {"2": Rank.TWO, "3": Rank.THREE, "4": Rank.FOUR, "5": Rank.FIVE,
                               "6": Rank.SIX, "7": Rank.SEVEN, "8": Rank.EIGHT, "9": Rank.NINE,
                               "10": Rank.TEN, "J": Rank.JACK, "Q": Rank.QUEEN, "K": Rank.KING, "A": Rank.ACE}
                    rank = rank_map.get(rank_char)
                    
                    if suit and rank:
                        cards.append(Card(rank, suit))
                    else:
                        raise ValueError(f"Invalid card format: {card_str}")
            
            # 调用游戏引擎处理出牌
            from app.main import game_engine
            game_id = connection_manager.get_game_id()
            if not game_id:
                await connection_manager.send_personal_message({
                    "type": "ERROR",
                    "message": "No active game"
                }, client_id)
                return
            
            result = game_engine.process_player_action(game_id, player_id, "play_cards", cards)
            
            if result.get("success"):
                # 先发送出牌确认给当前玩家
                await connection_manager.send_personal_message({
                    "type": "PLAY_CARDS_SUCCESS",
                    "message": result.get("message", "Cards played successfully"),
                    "next_player_index": result.get("next_player_index"),
                    "player_finished": result.get("player_finished", False)
                }, client_id)
                
                # 然后异步广播游戏状态更新（不阻塞当前响应）
                import asyncio
                asyncio.create_task(broadcast_game_state())
                
                # 如果玩家出完牌，广播特殊消息
                if result.get("player_finished"):
                    await connection_manager.broadcast({
                        "type": "PLAYER_FINISHED",
                        "player_id": player_id,
                        "message": f"Player {player_id} has finished the round!"
                    })
            else:
                # 出牌失败，需要重新选择
                error_message = result.get("error", "Failed to play cards")
                last_hand = connection_manager.get_last_played_hand()
                
                # 构建更详细的错误信息
                if last_hand:
                    error_details = f"{error_message} 上家出牌：{[str(card) for card in last_hand]}"
                else:
                    error_details = error_message
                
                await connection_manager.send_personal_message({
                    "type": "PLAY_CARDS_ERROR",
                    "message": error_details,
                    "requires_reselection": True,  # 标记需要重新选择
                    "last_played_hand": last_hand  # 提供上家出牌信息
                }, client_id)
                
        except Exception as e:
            logger.error(f"Error processing play cards: {e}")
            await connection_manager.send_personal_message({
                "type": "ERROR",
                "message": f"Error processing cards: {str(e)}"
            }, client_id)
    
    elif message_type == "PASS_TURN":
        # 处理玩家过牌
        player_id = connection_manager.get_player_id(client_id)
        if not player_id:
            await connection_manager.send_personal_message({
                "type": "ERROR",
                "message": "Player not registered"
            }, client_id)
            return
        
        # 调用游戏引擎处理过牌
        from app.main import game_engine
        game_id = connection_manager.get_game_id()
        if not game_id:
            await connection_manager.send_personal_message({
                "type": "ERROR",
                "message": "No active game"
            }, client_id)
            return
        
        result = game_engine.process_player_action(game_id, player_id, "pass")
        
        if result.get("success"):
            # 先发送过牌确认给当前玩家
            await connection_manager.send_personal_message({
                "type": "PASS_TURN_SUCCESS",
                "message": result.get("message", "Turn passed successfully"),
                "next_player_index": result.get("next_player_index"),
                "pass_count": result.get("pass_count", 0)
            }, client_id)
            
            # 然后异步广播游戏状态更新（不阻塞当前响应）
            import asyncio
            asyncio.create_task(broadcast_game_state())
        else:
            # 过牌失败
            await connection_manager.send_personal_message({
                "type": "PASS_TURN_ERROR",
                "message": result.get("error", "Failed to pass turn")
            }, client_id)
    
    elif message_type == "PING":
        # 心跳检测
        await connection_manager.send_personal_message({
            "type": "PONG",
            "timestamp": message.get("timestamp")
        }, client_id)
    
    else:
        # Unknown message type
        await connection_manager.send_personal_message({
            "type": "ERROR",
            "message": f"Unknown message type: {message_type}"
        }, client_id)
