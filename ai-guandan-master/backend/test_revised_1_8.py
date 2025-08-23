#!/usr/bin/env python3
"""
修正后的任务1.8测试：重构牌型解析器以支持"逢人配"
随机生成各种牌组测试
"""

import random
from app.game_logic.card import Card, Rank, Suit
from app.game_logic.hand_validator import parse_hand, HandType


def generate_random_cards(count: int, level: int = 7, include_wildcard: bool = True):
    """生成随机牌组，尽量构成有效牌型"""
    cards = []
    ranks = [r for r in Rank if r not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]]
    suits = [Suit.SPADE, Suit.HEART, Suit.CLUB, Suit.DIAMOND]
    
    # 确保包含逢人配
    if include_wildcard and count >= 1:
        wildcard = Card(Rank.SEVEN, Suit.HEART)  # H7 逢人配
        cards.append(wildcard)
        count -= 1
    
    if count == 0:
        return cards
    
    # 根据牌数生成更合理的牌组
    if count == 1:
        # 单张：随机生成
        rank = random.choice(ranks)
        suit = random.choice(suits)
        cards.append(Card(rank, suit))
    
    elif count == 2:
        # 对子：生成相同牌面值
        rank = random.choice(ranks)
        suit1, suit2 = random.sample(suits, 2)
        cards.extend([Card(rank, suit1), Card(rank, suit2)])
    
    elif count == 4:
        # 4张：尝试生成炸弹
        if random.random() < 0.7:  # 70%概率生成炸弹
            rank = random.choice(ranks)
            cards.extend([Card(rank, suit) for suit in suits])
        else:
            # 随机生成
            for _ in range(count):
                rank = random.choice(ranks)
                suit = random.choice(suits)
                cards.append(Card(rank, suit))
    
    elif count == 5:
        # 5张：尝试生成顺子或三带二
        if random.random() < 0.6:  # 60%概率生成顺子
            start_rank = random.choice(ranks[:10])  # 选择较小的牌面值
            for i in range(5):
                rank_order = start_rank.order + i
                if rank_order <= 14:
                    rank = Card._level_to_rank(rank_order)
                    suit = random.choice(suits)
                    cards.append(Card(rank, suit))
        else:
            # 随机生成
            for _ in range(count):
                rank = random.choice(ranks)
                suit = random.choice(suits)
                cards.append(Card(rank, suit))
    
    elif count == 6:
        # 6张：尝试生成连对
        if random.random() < 0.5:  # 50%概率生成连对
            start_rank = random.choice(ranks[:9])  # 选择较小的牌面值
            for i in range(3):
                rank_order = start_rank.order + i
                if rank_order <= 14:
                    rank = Card._level_to_rank(rank_order)
                    suit1, suit2 = random.sample(suits, 2)
                    cards.extend([Card(rank, suit1), Card(rank, suit2)])
        else:
            # 随机生成
            for _ in range(count):
                rank = random.choice(ranks)
                suit = random.choice(suits)
                cards.append(Card(rank, suit))
    
    else:
        # 其他情况：随机生成
        for _ in range(count):
            rank = random.choice(ranks)
            suit = random.choice(suits)
            cards.append(Card(rank, suit))
    
    return cards


def test_random_hands():
    """测试随机牌组"""
    print("=== 随机牌组测试 ===")
    level = 7
    
    # 单张2组
    print("\n--- 单张牌组 (2组) ---")
    for i in range(2):
        cards = generate_random_cards(1, level, include_wildcard=(i == 0))
        print(f"单张{i+1}: {[str(card) for card in cards]}")
        result = parse_hand(cards, level)
        print(f"  结果: {[hand.hand_type for hand in result]}")
    
    # 对子3组
    print("\n--- 对子牌组 (3组) ---")
    for i in range(3):
        cards = generate_random_cards(2, level, include_wildcard=(i < 2))
        print(f"对子{i+1}: {[str(card) for card in cards]}")
        result = parse_hand(cards, level)
        print(f"  结果: {[hand.hand_type for hand in result]}")
    
    # 4张牌5组
    print("\n--- 4张牌组 (5组) ---")
    for i in range(5):
        cards = generate_random_cards(4, level, include_wildcard=(i < 3))
        print(f"4张{i+1}: {[str(card) for card in cards]}")
        result = parse_hand(cards, level)
        print(f"  结果: {[hand.hand_type for hand in result]}")
    
    # 5张牌10组
    print("\n--- 5张牌组 (10组) ---")
    for i in range(10):
        cards = generate_random_cards(5, level, include_wildcard=(i < 7))
        print(f"5张{i+1}: {[str(card) for card in cards]}")
        result = parse_hand(cards, level)
        print(f"  结果: {[hand.hand_type for hand in result]}")
    
    # 6张牌10组
    print("\n--- 6张牌组 (10组) ---")
    for i in range(10):
        cards = generate_random_cards(6, level, include_wildcard=(i < 6))
        print(f"6张{i+1}: {[str(card) for card in cards]}")
        result = parse_hand(cards, level)
        print(f"  结果: {[hand.hand_type for hand in result]}")


if __name__ == "__main__":
    print("开始随机牌组测试...")
    print(f"当前级别: 7 (逢人配: H7)")
    print()
    
    test_random_hands()
    
    print("\n=== 测试完成 ===")
    print("请检查上述结果是否符合预期")
