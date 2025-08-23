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
            Rank.SMALL_JOKER: 15,
            Rank.BIG_JOKER: 16
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
    
    def __lt__(self, other) -> bool:
        """
        比较两张牌的大小，用于排序
        
        排序规则：
        1. 首先按牌面值排序
        2. 牌面值相同时按花色排序（黑桃 < 红桃 < 方块 < 梅花）
        """
        if not isinstance(other, Card):
            return NotImplemented
        
        # 首先按牌面值排序
        if self.rank.order != other.rank.order:
            return self.rank.order < other.rank.order
        
        # 王牌之间的比较
        if self.rank in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
            return False  # 王牌之间不需要进一步排序
        
        # 牌面值相同时按花色排序
        suit_order = {Suit.SPADE: 1, Suit.HEART: 2, Suit.DIAMOND: 3, Suit.CLUB: 4}
        return suit_order[self.suit] < suit_order[other.suit]
    
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
    
    @property
    def is_joker(self) -> bool:
        """判断是否为王牌"""
        return self.rank in [Rank.SMALL_JOKER, Rank.BIG_JOKER]
    
    @property
    def is_red(self) -> bool:
        """判断是否为红色牌（红桃或方块）"""
        if self.is_joker:
            return False
        return self.suit in [Suit.HEART, Suit.DIAMOND]
    
    @property
    def is_black(self) -> bool:
        """判断是否为黑色牌（黑桃或梅花）"""
        if self.is_joker:
            return False
        return self.suit in [Suit.SPADE, Suit.CLUB]
