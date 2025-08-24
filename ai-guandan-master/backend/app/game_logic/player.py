"""
掼蛋游戏玩家定义模块

此模块定义了掼蛋游戏中的玩家类。
"""

from typing import List, Optional
from enum import Enum
from .card import Card, Rank


class PlayerType(Enum):
    """玩家类型枚举"""
    HUMAN = "human"      # 人类玩家
    AI = "ai"           # AI玩家


class Player:
    """
    掼蛋游戏中的玩家
    
    Attributes:
        player_id: 玩家唯一标识符
        name: 玩家名称
        player_type: 玩家类型（人类或AI）
        hand: 玩家手牌列表
        is_finished: 是否已出完牌
        rank: 当前等级（2-A）
    """
    
    def __init__(self, player_id: str, name: str = "", player_type: PlayerType = PlayerType.HUMAN, team: int = 0):
        """
        初始化玩家
        
        Args:
            player_id: 玩家唯一标识符
            name: 玩家名称，默认为空
            player_type: 玩家类型，默认为人类玩家
            team: 所属队伍（0或1），默认为0
        """
        self.player_id = player_id
        self.name = name or f"Player_{player_id}"
        self.player_type = player_type
        self.team = team  # 新增：所属队伍（0或1）
        self.hand: List[Card] = []
        self.is_finished = False
        self.rank = "2"  # 掼蛋等级，从2开始
    
    def add_cards(self, cards: List[Card], level: int = 2):
        """
        向玩家手牌添加卡牌
        
        Args:
            cards: 要添加的卡牌列表
            level: 当前级别，用于排序时判断级牌
        """
        self.hand.extend(cards)
        self._sort_hand(level)
    
    def remove_cards(self, cards: List[Card], level: int = 2) -> bool:
        """
        从玩家手牌中移除卡牌
        
        Args:
            cards: 要移除的卡牌列表
            level: 当前级别，用于排序时判断级牌
            
        Returns:
            True如果成功移除所有卡牌，否则False
        """
        # 检查玩家是否拥有所有要移除的卡牌
        hand_copy = self.hand.copy()
        
        for card in cards:
            if card in hand_copy:
                hand_copy.remove(card)
            else:
                return False  # 玩家没有这张牌
        
        # 如果检查通过，实际移除卡牌
        for card in cards:
            self.hand.remove(card)
        
        # 检查是否出完牌
        if len(self.hand) == 0:
            self.is_finished = True
        
        # 重新排序手牌
        self._sort_hand(level)
        
        return True
    
    def has_cards(self, cards: List[Card]) -> bool:
        """
        检查玩家是否拥有指定的卡牌
        
        Args:
            cards: 要检查的卡牌列表
            
        Returns:
            True如果玩家拥有所有指定卡牌，否则False
        """
        hand_copy = self.hand.copy()
        
        for card in cards:
            if card in hand_copy:
                hand_copy.remove(card)
            else:
                return False
        
        return True
    
    def get_hand_count(self) -> int:
        """
        获取玩家手牌数量
        
        Returns:
            手牌数量
        """
        return len(self.hand)
    
    def get_hand_copy(self) -> List[Card]:
        """
        获取手牌的副本（避免外部修改）
        
        Returns:
            手牌列表的副本
        """
        return self.hand.copy()
    
    def clear_hand(self):
        """清空手牌"""
        self.hand.clear()
        self.is_finished = False
    
    def _sort_hand(self, level: int = 2):
        """对手牌进行排序"""
        # 使用牌力值进行排序，而不是直接比较Card对象
        self.hand.sort(key=lambda card: self._get_card_value_for_sorting(card, level))
    
    def _get_card_value_for_sorting(self, card, level: int = 2) -> int:
        """
        获取牌的价值用于排序
        
        Args:
            card: 卡牌对象
            level: 当前级别，用于判断级牌
            
        Returns:
            牌的价值（越大越重要）
        """
        # 使用Rank枚举中已有的order属性
        base_value = card.rank.order
        
        # 级牌大于普通牌（但小于王牌）
        if card.rank.value == str(level) and card.rank not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
            # 级牌在普通牌中最大，但小于王牌
            # 王牌的order是16和17，级牌应该小于这个值
            return 15  # 级牌值设为15，介于ACE(14)和王牌(16,17)之间
        
        return base_value
    
    def is_human(self) -> bool:
        """判断是否为人类玩家"""
        return self.player_type == PlayerType.HUMAN
    
    def is_ai(self) -> bool:
        """判断是否为AI玩家"""
        return self.player_type == PlayerType.AI
    
    def __str__(self):
        """返回玩家的字符串表示"""
        type_str = "Human" if self.is_human() else "AI"
        return f"{self.name}({type_str}, {len(self.hand)} cards)"
    
    def __repr__(self):
        """返回玩家的详细表示"""
        return f"Player(id={self.player_id}, name={self.name}, type={self.player_type}, cards={len(self.hand)})"
    
    def to_dict(self, include_hand: bool = False, for_player_id: Optional[str] = None) -> dict:
        """
        将玩家信息转换为字典格式
        
        Args:
            include_hand: 是否包含手牌信息
            for_player_id: 为特定玩家生成信息（只有本人能看到完整手牌）
            
        Returns:
            玩家信息字典
        """
        player_dict = {
            "player_id": self.player_id,
            "name": self.name,
            "player_type": self.player_type.value,
            "team": self.team,  # 新增：队伍信息
            "hand_count": len(self.hand),
            "is_finished": self.is_finished,
            "rank": self.rank
        }
        
        # 只有当明确要求包含手牌，且是为玩家本人生成信息时，才包含完整手牌
        if include_hand and (for_player_id is None or for_player_id == self.player_id):
            player_dict["hand"] = [str(card) for card in self.hand]
        
        return player_dict


class HumanPlayer(Player):
    """
    人类玩家类
    
    继承自Player，添加人类玩家特有的功能
    """
    
    def __init__(self, player_id: str, name: str = "", team: int = 0):
        """
        初始化人类玩家
        
        Args:
            player_id: 玩家唯一标识符
            name: 玩家名称
            team: 所属队伍（0或1）
        """
        super().__init__(player_id, name, PlayerType.HUMAN, team)


class AIPlayer(Player):
    """
    AI玩家类
    
    继承自Player，添加AI玩家特有的功能
    """
    
    def __init__(self, player_id: str, name: str = "", team: int = 0, difficulty: str = "normal"):
        """
        初始化AI玩家
        
        Args:
            player_id: 玩家唯一标识符
            name: 玩家名称
            team: 所属队伍（0或1）
            difficulty: AI难度级别
        """
        super().__init__(player_id, name, PlayerType.AI, team)
        self.difficulty = difficulty
    
    def to_dict(self, include_hand: bool = False, for_player_id: Optional[str] = None) -> dict:
        """
        将AI玩家信息转换为字典格式
        
        Args:
            include_hand: 是否包含手牌信息
            for_player_id: 为特定玩家生成信息
            
        Returns:
            AI玩家信息字典
        """
        player_dict = super().to_dict(include_hand, for_player_id)
        player_dict["difficulty"] = self.difficulty
        return player_dict
