"""
掼蛋游戏状态定义模块

此模块定义了掼蛋游戏中的游戏状态类。
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from .player import Player
from .card import Card


class GamePhase(Enum):
    """游戏阶段枚举"""
    WAITING = "waiting"          # 等待玩家
    DEALING = "dealing"          # 发牌阶段
    TRIBUTING = "tributing"      # 进贡阶段
    PLAYING = "playing"          # 游戏进行中
    ROUND_OVER = "round_over"    # 一轮结束
    GAME_END = "game_end"        # 游戏结束


class TurnAction(Enum):
    """回合动作枚举"""
    PLAY_CARDS = "play_cards"    # 出牌
    PASS = "pass"                # 过牌
    WAITING = "waiting"          # 等待中


class GameState:
    """
    掼蛋游戏状态
    
    管理一局游戏的完整状态信息
    """
    
    def __init__(self, game_id: str, max_players: int = 4):
        """
        初始化游戏状态
        
        Args:
            game_id: 游戏唯一标识符
            max_players: 最大玩家数量，默认4人
        """
        self.game_id = game_id
        self.max_players = max_players
        self.created_at = datetime.now()
        
        # 玩家相关
        self.players: List[Player] = []
        self.current_turn_index = 0
        
        # 游戏进度
        self.phase = GamePhase.WAITING
        self.round_number = 0
        self.turn_number = 0
        
        # 新增：掼蛋2v2组队和升级相关
        self.current_level = 2  # 当前打级，从2开始
        self.declarer_team = 0  # 当前打级的队伍（0或1）
        self.last_round_finish_order: List[str] = []  # 上一轮结束顺序，用于判断名次和进贡
        
        # 当前回合状态
        self.last_played_hand: List[Card] = []
        self.last_player_id: Optional[str] = None
        self.last_action = TurnAction.WAITING
        
        # 过牌计数
        self.pass_count = 0
        self.max_pass_count = 3  # 连续3个玩家过牌后，重置为可以出任意牌
        
        # 游戏历史
        self.move_history: List[Dict[str, Any]] = []
        
        # 游戏设置
        self.auto_play_ai = True  # 是否自动执行AI回合
        
    def add_player(self, player: Player) -> bool:
        """
        添加玩家到游戏
        
        Args:
            player: 要添加的玩家
            
        Returns:
            True如果成功添加，否则False
        """
        if len(self.players) >= self.max_players:
            return False
        
        # 检查玩家ID是否已存在
        if any(p.player_id == player.player_id for p in self.players):
            return False
        
        self.players.append(player)
        
        # 如果达到最大玩家数，准备开始游戏
        if len(self.players) == self.max_players:
            self.phase = GamePhase.DEALING
        
        return True
    
    def remove_player(self, player_id: str) -> bool:
        """
        从游戏中移除玩家
        
        Args:
            player_id: 要移除的玩家ID
            
        Returns:
            True如果成功移除，否则False
        """
        for i, player in enumerate(self.players):
            if player.player_id == player_id:
                self.players.pop(i)
                
                # 调整当前回合索引
                if i <= self.current_turn_index and self.current_turn_index > 0:
                    self.current_turn_index -= 1
                
                # 如果玩家数不足，回到等待状态
                if len(self.players) < self.max_players:
                    self.phase = GamePhase.WAITING
                
                return True
        
        return False
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """
        根据ID获取玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            玩家对象，如果不存在则返回None
        """
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None
    
    def get_current_player(self) -> Optional[Player]:
        """
        获取当前回合的玩家
        
        Returns:
            当前玩家对象，如果没有玩家则返回None
        """
        if not self.players or self.current_turn_index >= len(self.players):
            return None
        return self.players[self.current_turn_index]
    
    def get_next_player_index(self) -> int:
        """
        获取下一个玩家的索引
        
        Returns:
            下一个玩家的索引
        """
        return (self.current_turn_index + 1) % len(self.players)
    
    def advance_turn(self):
        """推进到下一个玩家的回合"""
        self.current_turn_index = self.get_next_player_index()
        self.turn_number += 1
    
    def play_cards(self, player_id: str, cards: List[Card]) -> bool:
        """
        玩家出牌
        
        Args:
            player_id: 出牌玩家ID
            cards: 出的牌
            
        Returns:
            True如果出牌成功，否则False
        """
        # 验证是否为当前玩家
        current_player = self.get_current_player()
        if not current_player or current_player.player_id != player_id:
            return False
        
        # 验证玩家是否拥有这些牌
        if not current_player.has_cards(cards):
            return False
        
        # 移除玩家手牌
        if not current_player.remove_cards(cards):
            return False
        
        # 更新游戏状态
        self.last_played_hand = cards.copy()
        self.last_player_id = player_id
        self.last_action = TurnAction.PLAY_CARDS
        self.pass_count = 0  # 重置过牌计数
        
        # 记录移动历史
        self._add_move_to_history(player_id, TurnAction.PLAY_CARDS, cards)
        
        # 检查玩家是否出完牌
        if current_player.is_finished:
            self._handle_player_finished(current_player)
        
        # 推进回合
        self.advance_turn()
        
        return True
    
    def pass_turn(self, player_id: str) -> bool:
        """
        玩家过牌
        
        Args:
            player_id: 过牌玩家ID
            
        Returns:
            True如果过牌成功，否则False
        """
        # 验证是否为当前玩家
        current_player = self.get_current_player()
        if not current_player or current_player.player_id != player_id:
            return False
        
        # 更新游戏状态
        self.last_action = TurnAction.PASS
        self.pass_count += 1
        
        # 记录移动历史
        self._add_move_to_history(player_id, TurnAction.PASS, [])
        
        # 如果连续过牌数达到上限，重置为可以出任意牌
        if self.pass_count >= self.max_pass_count:
            self.last_played_hand = []
            self.last_player_id = None
            self.pass_count = 0
        
        # 推进回合
        self.advance_turn()
        
        return True
    
    def can_play_any_cards(self) -> bool:
        """
        判断当前是否可以出任意牌（首轮或连续过牌后）
        
        Returns:
            True如果可以出任意牌，否则False
        """
        return len(self.last_played_hand) == 0
    
    def is_game_over(self) -> bool:
        """
        判断游戏是否结束
        
        Returns:
            True如果游戏结束，否则False
        """
        return self.phase == GamePhase.GAME_END
    
    def get_winners(self) -> List[Player]:
        """
        获取获胜玩家列表
        
        Returns:
            获胜玩家列表
        """
        return [player for player in self.players if player.is_finished]
    
    def _add_move_to_history(self, player_id: str, action: TurnAction, cards: List[Card]):
        """
        添加移动到历史记录
        
        Args:
            player_id: 玩家ID
            action: 动作类型
            cards: 涉及的卡牌
        """
        move = {
            "turn_number": self.turn_number,
            "player_id": player_id,
            "action": action.value,
            "cards": [str(card) for card in cards],
            "timestamp": datetime.now().isoformat()
        }
        self.move_history.append(move)
    
    def _handle_player_finished(self, player: Player):
        """
        处理玩家出完牌的情况
        
        Args:
            player: 出完牌的玩家
        """
        # 检查是否所有玩家都出完牌（除了一个）
        finished_players = [p for p in self.players if p.is_finished]
        
        if len(finished_players) >= len(self.players) - 1:
            self.phase = GamePhase.GAME_END
        else:
            self.phase = GamePhase.ROUND_END
    
    def reset_round(self):
        """重置回合状态（用于新一轮游戏）"""
        self.round_number += 1
        self.turn_number = 0
        self.current_turn_index = 0
        self.last_played_hand = []
        self.last_player_id = None
        self.last_action = TurnAction.WAITING
        self.pass_count = 0
        self.move_history = []
        
        # 重置玩家状态
        for player in self.players:
            player.clear_hand()
        
        self.phase = GamePhase.DEALING
    
    def to_dict(self, for_player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        将游戏状态转换为字典格式
        
        Args:
            for_player_id: 为特定玩家生成状态（影响手牌可见性）
            
        Returns:
            游戏状态字典
        """
        current_player = self.get_current_player()
        
        return {
            "game_id": self.game_id,
            "phase": self.phase.value,
            "round_number": self.round_number,
            "turn_number": self.turn_number,
            "current_player_id": current_player.player_id if current_player else None,
            "last_played_hand": [str(card) for card in self.last_played_hand],
            "last_player_id": self.last_player_id,
            "last_action": self.last_action.value,
            "pass_count": self.pass_count,
            "can_play_any": self.can_play_any_cards(),
            "is_game_over": self.is_game_over(),
            "players": [player.to_dict(include_hand=(for_player_id is not None), for_player_id=for_player_id) 
                       for player in self.players],
            "winners": [player.player_id for player in self.get_winners()],
            "created_at": self.created_at.isoformat(),
            "move_history": self.move_history[-10:] if self.move_history else [],  # 只返回最近10步
            # 新增：掼蛋2v2组队和升级相关信息
            "current_level": self.current_level,
            "declarer_team": self.declarer_team,
            "last_round_finish_order": self.last_round_finish_order
        }
    
    def __str__(self):
        """返回游戏状态的字符串表示"""
        current_player = self.get_current_player()
        return f"Game {self.game_id} - {self.phase.value} - {len(self.players)}/{self.max_players} players - Current: {current_player.name if current_player else 'None'}"
    
    def __repr__(self):
        """返回游戏状态的详细表示"""
        return f"GameState(id={self.game_id}, phase={self.phase}, players={len(self.players)}, turn={self.turn_number})"
