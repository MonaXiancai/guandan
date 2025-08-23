"""
掼蛋游戏牌堆定义模块

此模块定义了掼蛋游戏中的牌堆类，负责生成、洗牌和发牌。
"""

import random
from typing import List
from .card import Card, Suit, Rank


class Deck:
    """
    掼蛋游戏中的牌堆
    
    掼蛋使用两副标准扑克牌，共108张牌：
    - 普通牌：2-A 每种4张 × 2副 = 104张
    - 王牌：小王、大王 每种2张 × 2副 = 4张
    """
    
    def __init__(self):
        """初始化牌堆，生成两副标准扑克牌"""
        self.cards: List[Card] = []
        self._generate_cards()
    
    def _generate_cards(self):
        """生成两副标准扑克牌"""
        self.cards.clear()
        
        # 生成两副牌
        for _ in range(2):
            # 生成普通牌 (2-A，每种花色13张)
            for suit in Suit:
                for rank in [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, 
                           Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, 
                           Rank.QUEEN, Rank.KING, Rank.ACE]:
                    self.cards.append(Card(rank, suit))
            
            # 生成王牌
            self.cards.append(Card(Rank.SMALL_JOKER))
            self.cards.append(Card(Rank.BIG_JOKER))
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def deal(self, num_players: int) -> List[List[Card]]:
        """
        向指定数量的玩家发牌
        
        Args:
            num_players: 玩家数量
            
        Returns:
            包含每个玩家手牌的列表，每个玩家的手牌是一个Card列表
            
        Raises:
            ValueError: 如果玩家数量不合理或牌数不够
        """
        if num_players <= 0:
            raise ValueError("玩家数量必须大于0")
        
        if num_players > 8:
            raise ValueError("玩家数量不能超过8人")
        
        total_cards = len(self.cards)
        cards_per_player = total_cards // num_players
        
        if cards_per_player == 0:
            raise ValueError("牌数不够分配给所有玩家")
        
        # 为每个玩家分配手牌
        hands = []
        card_index = 0
        
        for _ in range(num_players):
            player_hand = []
            for _ in range(cards_per_player):
                if card_index < len(self.cards):
                    player_hand.append(self.cards[card_index])
                    card_index += 1
            hands.append(player_hand)
        
        # 移除已发出的牌
        self.cards = self.cards[card_index:]
        
        return hands
    
    def deal_specific(self, num_cards: int) -> List[Card]:
        """
        发指定数量的牌
        
        Args:
            num_cards: 要发的牌数
            
        Returns:
            发出的牌列表
            
        Raises:
            ValueError: 如果要发的牌数超过剩余牌数
        """
        if num_cards < 0:
            raise ValueError("发牌数量不能为负数")
        
        if num_cards > len(self.cards):
            raise ValueError(f"剩余牌数({len(self.cards)})不足，无法发出{num_cards}张牌")
        
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        
        return dealt_cards
    
    def reset(self):
        """重置牌堆，重新生成两副标准扑克牌"""
        self._generate_cards()
    
    def remaining_cards(self) -> int:
        """返回剩余牌数"""
        return len(self.cards)
    
    def is_empty(self) -> bool:
        """判断牌堆是否为空"""
        return len(self.cards) == 0
    
    def peek_top(self, num_cards: int = 1) -> List[Card]:
        """
        查看牌堆顶部的牌（不移除）
        
        Args:
            num_cards: 要查看的牌数，默认1张
            
        Returns:
            牌堆顶部的牌列表
            
        Raises:
            ValueError: 如果要查看的牌数超过剩余牌数
        """
        if num_cards < 0:
            raise ValueError("查看牌数不能为负数")
        
        if num_cards > len(self.cards):
            raise ValueError(f"剩余牌数({len(self.cards)})不足，无法查看{num_cards}张牌")
        
        return self.cards[:num_cards].copy()
    
    def __len__(self) -> int:
        """返回剩余牌数"""
        return len(self.cards)
    
    def __str__(self) -> str:
        """返回牌堆的字符串表示"""
        return f"Deck(剩余牌数: {len(self.cards)})"
    
    def __repr__(self) -> str:
        """返回牌堆的详细表示"""
        return f"Deck(cards={len(self.cards)})"
    
    @classmethod
    def create_shuffled(cls) -> 'Deck':
        """
        创建一个已洗牌的牌堆
        
        Returns:
            已洗牌的Deck对象
        """
        deck = cls()
        deck.shuffle()
        return deck
    
    def get_all_cards(self) -> List[Card]:
        """
        获取牌堆中所有牌的副本（不移除）
        
        Returns:
            牌堆中所有牌的列表副本
        """
        return self.cards.copy()
    
    @staticmethod
    def validate_full_deck(cards: List[Card]) -> bool:
        """
        验证给定的牌列表是否为完整的两副扑克牌
        
        Args:
            cards: 要验证的牌列表
            
        Returns:
            True如果是完整的两副扑克牌，否则False
        """
        if len(cards) != 108:
            return False
        
        # 统计每种牌的数量
        card_count = {}
        for card in cards:
            card_key = (card.rank, card.suit)
            card_count[card_key] = card_count.get(card_key, 0) + 1
        
        # 验证普通牌：每种应该有2张
        for suit in Suit:
            for rank in [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, 
                       Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, 
                       Rank.QUEEN, Rank.KING, Rank.ACE]:
                if card_count.get((rank, suit), 0) != 2:
                    return False
        
        # 验证王牌：每种应该有2张
        if card_count.get((Rank.SMALL_JOKER, None), 0) != 2:
            return False
        if card_count.get((Rank.BIG_JOKER, None), 0) != 2:
            return False
        
        return True
