#!/usr/bin/env python3
"""
简单测试：验证基本牌型识别
"""

from app.game_logic.card import Card, Rank, Suit
from app.game_logic.hand_validator import parse_hand, HandType


def test_basic_hands():
    """测试基本牌型"""
    print("=== 基本牌型测试 ===")
    level = 7
    
    # 测试炸弹
    print("\n--- 炸弹测试 ---")
    bomb_cards = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.HEART),    # H8
        Card(Rank.EIGHT, Suit.CLUB),     # C8
        Card(Rank.EIGHT, Suit.DIAMOND),  # D8
    ]
    print(f"四张8: {[str(card) for card in bomb_cards]}")
    result = parse_hand(bomb_cards, level)
    print(f"  结果: {[hand.hand_type for hand in result]}")
    
    # 测试顺子
    print("\n--- 顺子测试 ---")
    straight_cards = [
        Card(Rank.FIVE, Suit.SPADE),     # S5
        Card(Rank.SIX, Suit.HEART),      # H6
        Card(Rank.SEVEN, Suit.CLUB),     # C7
        Card(Rank.EIGHT, Suit.DIAMOND),  # D8
        Card(Rank.NINE, Suit.SPADE),     # S9
    ]
    print(f"顺子5-9: {[str(card) for card in straight_cards]}")
    result = parse_hand(straight_cards, level)
    print(f"  结果: {[hand.hand_type for hand in result]}")
    
    # 测试三带二
    print("\n--- 三带二测试 ---")
    trio_pair_cards = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.HEART),    # H8
        Card(Rank.EIGHT, Suit.CLUB),     # C8
        Card(Rank.TEN, Suit.DIAMOND),    # D10
        Card(Rank.TEN, Suit.SPADE),      # S10
    ]
    print(f"三张8+对10: {[str(card) for card in trio_pair_cards]}")
    result = parse_hand(trio_pair_cards, level)
    print(f"  结果: {[hand.hand_type for hand in result]}")
    
    # 测试连对
    print("\n--- 连对测试 ---")
    straight_pair_cards = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.HEART),    # H8
        Card(Rank.NINE, Suit.CLUB),      # C9
        Card(Rank.NINE, Suit.DIAMOND),   # D9
        Card(Rank.TEN, Suit.SPADE),      # S10
        Card(Rank.TEN, Suit.HEART),      # H10
    ]
    print(f"连对8,9,10: {[str(card) for card in straight_pair_cards]}")
    result = parse_hand(straight_pair_cards, level)
    print(f"  结果: {[hand.hand_type for hand in result]}")


if __name__ == "__main__":
    print("开始基本牌型测试...")
    print(f"当前级别: 7")
    print()
    
    test_basic_hands()
    
    print("\n=== 测试完成 ===")
