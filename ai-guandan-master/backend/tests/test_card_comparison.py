#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试指定牌组的大小比较
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.game_logic.card import Card, Suit, Rank
from app.game_logic.hand_validator import parse_hand, is_valid_play

def test_specific_hands():
    """测试指定的牌组比较"""
    level = 7  # 当前级别7，级牌是7
    print(f"开始指定牌组比较测试...")
    print(f"当前级别: {level} (级牌: 7)")
    print()
    
    print("=== 牌组大小比较测试 ===")
    
    # 测试1: 同花顺 vs 同花顺
    print("--- 测试1: 同花顺 vs 同花顺 ---")
    
    # H3，H4，H5，H6，H7 (同花顺，最高牌7)
    hand1 = [Card(Rank.THREE, Suit.HEART), Card(Rank.FOUR, Suit.HEART),
              Card(Rank.FIVE, Suit.HEART), Card(Rank.SIX, Suit.HEART),
              Card(Rank.SEVEN, Suit.HEART)]
    
    # H4，H5，H6，H7，H7 (同花顺，最高牌7，但包含级牌)
    hand2 = [Card(Rank.FOUR, Suit.HEART), Card(Rank.FIVE, Suit.HEART),
              Card(Rank.SIX, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
              Card(Rank.SEVEN, Suit.HEART)]
    
    print(f"手牌1: {[str(card) for card in hand1]}")
    print(f"手牌2: {[str(card) for card in hand2]}")
    
    # 解析牌型
    result1 = parse_hand(hand1, level)
    result2 = parse_hand(hand2, level)
    
    print(f"手牌1牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result1]}")
    print(f"手牌2牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result2]}")
    
    # 比较大小
    result = is_valid_play(hand2, hand1, level)
    print(f"手牌2 > 手牌1: {result}")
    
    result = is_valid_play(hand1, hand2, level)
    print(f"手牌1 > 手牌2: {result}")
    
    print()
    
    # 测试2: 连对 vs 炸弹
    print("--- 测试2: 连对 vs 炸弹 ---")
    
    # H6，H6，H7，H7，H8，H8 (连对，最高对8)
    hand3 = [Card(Rank.SIX, Suit.HEART), Card(Rank.SIX, Suit.HEART),
              Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
              Card(Rank.EIGHT, Suit.HEART), Card(Rank.EIGHT, Suit.HEART)]
    
    # H8，S8，D8，C8 (炸弹，4张8)
    hand4 = [Card(Rank.EIGHT, Suit.HEART), Card(Rank.EIGHT, Suit.SPADE),
              Card(Rank.EIGHT, Suit.DIAMOND), Card(Rank.EIGHT, Suit.CLUB)]
    
    print(f"手牌3: {[str(card) for card in hand3]}")
    print(f"手牌4: {[str(card) for card in hand4]}")
    
    # 解析牌型
    result3 = parse_hand(hand3, level)
    result4 = parse_hand(hand4, level)
    
    print(f"手牌3牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result3]}")
    print(f"手牌4牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result4]}")
    
    # 比较大小
    result = is_valid_play(hand4, hand3, level)
    print(f"手牌4 > 手牌3: {result}")
    
    result = is_valid_play(hand3, hand4, level)
    print(f"手牌3 > 手牌4: {result}")
    
    print()
    
    # 测试3: 三带二 vs 三带二
    print("--- 测试3: 三带二 vs 三带二 ---")
    
    # H7，SA，DA，C2，C2 (三带二，三张A，对子2)
    hand5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.ACE, Suit.SPADE),
              Card(Rank.ACE, Suit.DIAMOND), Card(Rank.TWO, Suit.CLUB),
              Card(Rank.TWO, Suit.CLUB)]
    
    # H7，S7，D7，C2，C2 (三带二，三张7，对子2)
    hand6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.SPADE),
              Card(Rank.SEVEN, Suit.DIAMOND), Card(Rank.TWO, Suit.CLUB),
              Card(Rank.TWO, Suit.CLUB)]
    
    print(f"手牌5: {[str(card) for card in hand5]}")
    print(f"手牌6: {[str(card) for card in hand6]}")
    
    # 解析牌型
    result5 = parse_hand(hand5, level)
    result6 = parse_hand(hand6, level)
    
    print(f"手牌5牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result5]}")
    print(f"手牌6牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result6]}")
    
    # 比较大小
    result = is_valid_play(hand6, hand5, level)
    print(f"手牌6 > 手牌5: {result}")
    
    result = is_valid_play(hand5, hand6, level)
    print(f"手牌5 > 手牌6: {result}")
    
    print()
    
    # 测试4: 级牌炸弹 vs 王炸
    print("--- 测试4: 级牌炸弹 vs 王炸 ---")
    
    # H7，S7，D7，C7 (级牌炸弹，4张7)
    hand7 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.SPADE),
              Card(Rank.SEVEN, Suit.DIAMOND), Card(Rank.SEVEN, Suit.CLUB)]
    
    # SMALL_JOKER, SMALL_JOKER, LARGE_JOKER, LARGE_JOKER (王炸，4张王牌)
    hand8 = [Card(Rank.SMALL_JOKER), Card(Rank.SMALL_JOKER),
              Card(Rank.BIG_JOKER), Card(Rank.BIG_JOKER)]
    
    print(f"手牌7: {[str(card) for card in hand7]}")
    print(f"手牌8: {[str(card) for card in hand8]}")
    
    # 解析牌型
    result7 = parse_hand(hand7, level)
    result8 = parse_hand(hand8, level)
    
    print(f"手牌7牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result7]}")
    print(f"手牌8牌型: {[f'{hand.hand_type}({hand.primary_rank})' for hand in result8]}")
    
    # 比较大小
    result = is_valid_play(hand8, hand7, level)
    print(f"手牌8 > 手牌7: {result}")
    
    result = is_valid_play(hand7, hand8, level)
    print(f"手牌7 > 手牌8: {result}")
    
    print()
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_specific_hands()
