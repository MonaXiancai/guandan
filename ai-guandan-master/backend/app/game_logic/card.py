"""
掼蛋游戏卡牌定义模块

此模块定义了掼蛋游戏中的卡牌相关类和枚举。
"""

from enum import Enum
from typing import Union


class Suit(Enum):
    """花色枚举"""
    SPADE = "S"      # 黑桃
    HEART = "H"      # 红桃
    DIAMOND = "D"    # 方块
    CLUB = "C"       # 梅花

    def __str__(self):
        return self.value


class Rank(Enum):
    """牌面值枚举"""
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"
    SMALL_JOKER = "SMALL_JOKER"    # 小王
    BIG_JOKER = "BIG_JOKER"        # 大王

    def __str__(self):
        return self.value

    @property
    def order(self) -> int:
        """返回牌的排序值，用于比较大小"""
        order_map = {
            Rank.TWO: 2,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
            Rank.ACE: 14,
            Rank.SMALL_JOKER: 16,
            Rank.BIG_JOKER: 17
        }
        return order_map[self]


class Card:
    """
    掼蛋游戏中的单张卡牌
    
    Attributes:
        rank: 牌面值
        suit: 花色（王牌为None）
    """
    
    def __init__(self, rank: Rank, suit: Union[Suit, None] = None):
        """
        初始化卡牌
        
        Args:
            rank: 牌面值
            suit: 花色，王牌为None
        """
        self.rank = rank
        self.suit = suit
        
        # 验证王牌不应该有花色
        if rank in [Rank.SMALL_JOKER, Rank.BIG_JOKER] and suit is not None:
            raise ValueError("王牌不应该有花色")
        
        # 验证普通牌必须有花色
        if rank not in [Rank.SMALL_JOKER, Rank.BIG_JOKER] and suit is None:
            raise ValueError("普通牌必须有花色")
    
    def __str__(self) -> str:
        """返回卡牌的字符串表示"""
        if self.rank in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
            return str(self.rank)
        return f"{self.suit}{self.rank}"
    
    def __repr__(self) -> str:
        """返回卡牌的详细表示"""
        if self.rank in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
            return f"Card({self.rank})"
        return f"Card({self.rank}, {self.suit})"
    
    def __eq__(self, other) -> bool:
        """判断两张牌是否相等"""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        """返回卡牌的哈希值，用于set和dict"""
        return hash((self.rank, self.suit))
    
    def __lt__(self, other):
        """禁用小于比较操作，避免排序混淆"""
        raise TypeError("Card对象不支持直接比较，请使用具体的比较逻辑")
    
    def __le__(self, other):
        """禁用小于等于比较操作"""
        raise TypeError("Card对象不支持直接比较，请使用具体的比较逻辑")
    
    def __gt__(self, other):
        """禁用大于比较操作"""
        raise TypeError("Card对象不支持直接比较，请使用具体的比较逻辑")
    
    def __ge__(self, other):
        """禁用大于等于比较操作"""
        raise TypeError("Card对象不支持直接比较，请使用具体的比较逻辑")
    

    
    @classmethod
    def from_string(cls, card_str: str) -> 'Card':
        """
        从字符串创建卡牌对象
        
        Args:
            card_str: 卡牌字符串，如 "S5", "HA", "SMALL_JOKER"
            
        Returns:
            Card对象
            
        Examples:
            >>> Card.from_string("S5")
            Card(Rank.FIVE, Suit.SPADE)
            >>> Card.from_string("SMALL_JOKER")
            Card(Rank.SMALL_JOKER)
        """
        # 处理王牌
        if card_str == "SMALL_JOKER":
            return cls(Rank.SMALL_JOKER)
        elif card_str == "BIG_JOKER":
            return cls(Rank.BIG_JOKER)
        
        # 处理普通牌
        if len(card_str) < 2:
            raise ValueError(f"无效的卡牌字符串: {card_str}")
        
        suit_char = card_str[0]
        rank_str = card_str[1:]
        
        # 解析花色
        suit_map = {"S": Suit.SPADE, "H": Suit.HEART, "D": Suit.DIAMOND, "C": Suit.CLUB}
        if suit_char not in suit_map:
            raise ValueError(f"无效的花色: {suit_char}")
        suit = suit_map[suit_char]
        
        # 解析牌面值
        rank_map = {
            "2": Rank.TWO, "3": Rank.THREE, "4": Rank.FOUR, "5": Rank.FIVE,
            "6": Rank.SIX, "7": Rank.SEVEN, "8": Rank.EIGHT, "9": Rank.NINE,
            "10": Rank.TEN, "J": Rank.JACK, "Q": Rank.QUEEN, "K": Rank.KING, "A": Rank.ACE
        }
        if rank_str not in rank_map:
            raise ValueError(f"无效的牌面值: {rank_str}")
        rank = rank_map[rank_str]
        
        return cls(rank, suit)
    
    def is_joker(self) -> bool:
        """判断是否为王牌（大王或小王）"""
        return self.rank in [Rank.SMALL_JOKER, Rank.BIG_JOKER]
    
    def is_big_joker(self) -> bool:
        """判断是否为大王"""
        return self.rank == Rank.BIG_JOKER
    
    @property
    def is_red(self) -> bool:
        """判断是否为红色牌（红桃或方块）"""
        if self.is_joker():
            return False
        return self.suit in [Suit.HEART, Suit.DIAMOND]
    
    @property
    def is_black(self) -> bool:
        """判断是否为黑色牌（黑桃或梅花）"""
        if self.is_joker():
            return False
        return self.suit in [Suit.SPADE, Suit.CLUB]
    
    @staticmethod
    def _level_to_rank(level: int) -> Rank:
        """
        将级别数字转换为对应的Rank枚举
        
        Args:
            level: 级别数字（2-14，其中11=J, 12=Q, 13=K, 14=A）
            
        Returns:
            对应的Rank枚举
        """
        level_map = {
            2: Rank.TWO, 3: Rank.THREE, 4: Rank.FOUR, 5: Rank.FIVE,
            6: Rank.SIX, 7: Rank.SEVEN, 8: Rank.EIGHT, 9: Rank.NINE,
            10: Rank.TEN, 11: Rank.JACK, 12: Rank.QUEEN, 13: Rank.KING, 14: Rank.ACE
        }
        if level not in level_map:
            raise ValueError(f"无效的级别: {level}")
        return level_map[level]
    
    def is_trump(self, level: int) -> bool:
        """
        判断该牌是否是级牌（当前打的级别）
        
        在掼蛋中，级牌是当前级别的所有牌（如打7时，所有的7都是级牌）
        注意：王牌（大王、小王）不是级牌，王牌 > 级牌 > 普通牌
        
        Args:
            level: 当前打的级别（2-14）
            
        Returns:
            True如果是级牌，False否则
        """
        # 王牌不是级牌
        if self.is_joker():
            return False
        
        # 检查是否为当前级别的牌
        try:
            trump_rank = self._level_to_rank(level)
            return self.rank == trump_rank
        except ValueError:
            return False
    
    def is_wildcard(self, level: int) -> bool:
        """
        判断该牌是否是红桃级牌（"逢人配"万能牌）
        
        在掼蛋中，红桃级牌被称为"逢人配"，具有特殊规则：
        1. 单打时：就是自己本身（红桃级牌）
        2. 与其他牌一起出时：可以代替任何牌来组成牌型
        3. 限制：无法变成王牌
        
        例如：打7时，红桃7是逢人配
        
        Args:
            level: 当前打的级别（2-14）
            
        Returns:
            True如果是红桃级牌，False否则
        """
        # 王牌不是逢人配
        if self.is_joker():
            return False
        
        # 必须是红桃花色且是当前级别
        try:
            trump_rank = self._level_to_rank(level)
            return self.suit == Suit.HEART and self.rank == trump_rank
        except ValueError:
            return False
    
    def get_card_power(self, level: int) -> int:
        """
        获取牌的力量值，用于比较大小
        
        返回值越大表示牌力越强：
        - 王牌：1000+ (大王 > 小王)
        - 级牌：500+ (按rank.order排序)
        - 普通牌：按rank.order排序
        
        Args:
            level: 当前打的级别
            
        Returns:
            牌的力量值
        """
        if self.is_joker():
            # 王牌最大
            if self.rank == Rank.BIG_JOKER:
                return 1001
            else:  # SMALL_JOKER
                return 1000
        elif self.is_trump(level):
            # 级牌次之
            return 500 + self.rank.order
        else:
            # 普通牌最小
            return self.rank.order
    
    def can_substitute_as(self, target_card: 'Card', level: int) -> bool:
        """
        判断这张牌是否可以代替目标牌（逢人配功能）
        
        Args:
            target_card: 目标牌
            level: 当前级别
            
        Returns:
            True如果可以代替，False否则
        """
        # 只有逢人配可以代替其他牌
        if not self.is_wildcard(level):
            return False
        
        # 逢人配无法变成王牌
        if target_card.is_joker():
            return False
        
        # 可以代替任何非王牌
        return True
