#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试重构后的牌型解析器，支持"逢人配"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.game_logic.card import Card, Suit, Rank
from app.game_logic.hand_validator import parse_hand

def test_specific_hands():
    """测试具体的牌组例子"""
    level = 7  # 当前级别7，逢人配是H7和D7
    print(f"开始具体牌组测试...")
    print(f"当前级别: {level} (逢人配: H7, D7)")
    print()
    
    print("=== 具体牌组测试 ===")
    
    # 4张牌组 (10组)
    print("--- 4张牌组 (10组) ---")
    
    # 4张1: 炸弹 - 2张逢人配 + 2张10
    cards1 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART), 
               Card(Rank.TEN, Suit.HEART), Card(Rank.TEN, Suit.SPADE)]
    print(f"4张1: {[str(card) for card in cards1]}")
    result1 = parse_hand(cards1, level)
    for hand in result1:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张2: 炸弹 - 2张逢人配 + 2张K
    cards2 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
               Card(Rank.KING, Suit.HEART), Card(Rank.KING, Suit.CLUB)]
    print(f"4张2: {[str(card) for card in cards2]}")
    result2 = parse_hand(cards2, level)
    for hand in result2:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张3: 炸弹 - 2张逢人配 + 2张6
    cards3 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
               Card(Rank.SIX, Suit.SPADE), Card(Rank.SIX, Suit.CLUB)]
    print(f"4张3: {[str(card) for card in cards3]}")
    result3 = parse_hand(cards3, level)
    for hand in result3:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张4: 炸弹 - 2张逢人配 + 2张A
    cards4 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.DIAMOND),
               Card(Rank.ACE, Suit.HEART), Card(Rank.ACE, Suit.SPADE)]
    print(f"4张4: {[str(card) for card in cards4]}")
    result4 = parse_hand(cards4, level)
    for hand in result4:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张5: 炸弹 - 2张逢人配 + 2张2
    cards5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.DIAMOND),
               Card(Rank.TWO, Suit.HEART), Card(Rank.TWO, Suit.CLUB)]
    print(f"4张5: {[str(card) for card in cards5]}")
    result5 = parse_hand(cards5, level)
    for hand in result5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张6: 炸弹 - 2张逢人配 + 2张J
    cards6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.DIAMOND),
               Card(Rank.JACK, Suit.HEART), Card(Rank.JACK, Suit.DIAMOND)]
    print(f"4张6: {[str(card) for card in cards6]}")
    result6 = parse_hand(cards6, level)
    for hand in result6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张7: 炸弹 - 2张逢人配 + 2张Q
    cards7 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.DIAMOND),
               Card(Rank.QUEEN, Suit.HEART), Card(Rank.QUEEN, Suit.SPADE)]
    print(f"4张7: {[str(card) for card in cards7]}")
    result7 = parse_hand(cards7, level)
    for hand in result7:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张8: 炸弹 - 2张逢人配 + 2张8
    cards8 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.DIAMOND),
               Card(Rank.EIGHT, Suit.HEART), Card(Rank.EIGHT, Suit.CLUB)]
    print(f"4张8: {[str(card) for card in cards8]}")
    result8 = parse_hand(cards8, level)
    for hand in result8:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张9: 炸弹 - 2张逢人配 + 2张9
    cards9 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
               Card(Rank.NINE, Suit.HEART), Card(Rank.NINE, Suit.DIAMOND)]
    print(f"4张9: {[str(card) for card in cards9]}")
    result9 = parse_hand(cards9, level)
    for hand in result9:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 4张10: 炸弹 - 2张逢人配 + 2张3
    cards10 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                Card(Rank.SMALL_JOKER), Card(Rank.SMALL_JOKER)]
    print(f"4张10: {[str(card) for card in cards10]}")
    result10 = parse_hand(cards10, level)
    for hand in result10:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    print()
    
    # 5张牌组 (10组)
    print("--- 5张牌组 (10组) ---")
    
    # 5张1: 三带二 - 2张逢人配 + 2张9 + 1张Q
    cards1_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.NINE, Suit.HEART), Card(Rank.NINE, Suit.DIAMOND),
                 Card(Rank.QUEEN, Suit.SPADE)]
    print(f"5张1: {[str(card) for card in cards1_5]}")
    result1_5 = parse_hand(cards1_5, level)
    for hand in result1_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张2: 三带二 - 2张逢人配 + 2张K + 1张A
    cards2_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.KING, Suit.HEART), Card(Rank.KING, Suit.CLUB),
                 Card(Rank.ACE, Suit.HEART)]
    print(f"5张2: {[str(card) for card in cards2_5]}")
    result2_5 = parse_hand(cards2_5, level)
    for hand in result2_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张3: 三带二 - 2张逢人配 + 2张6 + 1张J
    cards3_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.SIX, Suit.SPADE), Card(Rank.SIX, Suit.CLUB),
                 Card(Rank.JACK, Suit.HEART)]
    print(f"5张3: {[str(card) for card in cards3_5]}")
    result3_5 = parse_hand(cards3_5, level)
    for hand in result3_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张4: 三带二 - 2张逢人配 + 2张10 + 1张8
    cards4_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.TEN, Suit.HEART), Card(Rank.TEN, Suit.SPADE),
                 Card(Rank.EIGHT, Suit.CLUB)]
    print(f"5张4: {[str(card) for card in cards4_5]}")
    result4_5 = parse_hand(cards4_5, level)
    for hand in result4_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张5: 三带二 - 2张逢人配 + 2张2 + 1张5
    cards5_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.TWO, Suit.HEART), Card(Rank.TWO, Suit.CLUB),
                 Card(Rank.FIVE, Suit.DIAMOND)]
    print(f"5张5: {[str(card) for card in cards5_5]}")
    result5_5 = parse_hand(cards5_5, level)
    for hand in result5_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张6: 同花顺 - 2张逢人配 + S8 + S9 + S10
    cards6_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.EIGHT, Suit.SPADE), Card(Rank.NINE, Suit.SPADE),
                 Card(Rank.TEN, Suit.SPADE)]
    print(f"5张6: {[str(card) for card in cards6_5]}")
    result6_5 = parse_hand(cards6_5, level)
    for hand in result6_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张7: 同花顺 - 2张逢人配 + H8 + H9 + H10
    cards7_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.EIGHT, Suit.HEART), Card(Rank.NINE, Suit.HEART),
                 Card(Rank.TEN, Suit.HEART)]
    print(f"5张7: {[str(card) for card in cards7_5]}")
    result7_5 = parse_hand(cards7_5, level)
    for hand in result7_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张8: 顺子 - 2张逢人配 + C8 + C9 + C10
    cards8_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.EIGHT, Suit.CLUB), Card(Rank.NINE, Suit.CLUB),
                 Card(Rank.TEN, Suit.CLUB)]
    print(f"5张8: {[str(card) for card in cards8_5]}")
    result8_5 = parse_hand(cards8_5, level)
    for hand in result8_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张9: 顺子 - 2张逢人配 + D8 + D9 + D10
    cards9_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.EIGHT, Suit.DIAMOND), Card(Rank.NINE, Suit.DIAMOND),
                 Card(Rank.TEN, Suit.DIAMOND)]
    print(f"5张9: {[str(card) for card in cards9_5]}")
    result9_5 = parse_hand(cards9_5, level)
    for hand in result9_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 5张10: 顺子 - 2张逢人配 + S6 + S8 + S9
    cards10_5 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                  Card(Rank.SIX, Suit.SPADE), Card(Rank.EIGHT, Suit.SPADE),
                  Card(Rank.NINE, Suit.SPADE)]
    print(f"5张10: {[str(card) for card in cards10_5]}")
    result10_5 = parse_hand(cards10_5, level)
    for hand in result10_5:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    print()
    
    # 6张牌组 (10组)
    print("--- 6张牌组 (10组) ---")
    
    # 6张1: 连对 - 2张逢人配 + 2张6 + 2张8
    cards1_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.SIX, Suit.SPADE), Card(Rank.SIX, Suit.CLUB),
                 Card(Rank.EIGHT, Suit.HEART), Card(Rank.EIGHT, Suit.DIAMOND)]
    print(f"6张1: {[str(card) for card in cards1_6]}")
    result1_6 = parse_hand(cards1_6, level)
    for hand in result1_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张2: 连对 - 2张逢人配 + 2张9 + 2张10
    cards2_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.NINE, Suit.SPADE), Card(Rank.NINE, Suit.CLUB),
                 Card(Rank.TEN, Suit.HEART), Card(Rank.TEN, Suit.DIAMOND)]
    print(f"6张2: {[str(card) for card in cards2_6]}")
    result2_6 = parse_hand(cards2_6, level)
    for hand in result2_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张3: 连对 - 2张逢人配 + 2张J + 2张Q
    cards3_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.JACK, Suit.SPADE), Card(Rank.JACK, Suit.CLUB),
                 Card(Rank.QUEEN, Suit.HEART), Card(Rank.QUEEN, Suit.DIAMOND)]
    print(f"6张3: {[str(card) for card in cards3_6]}")
    result3_6 = parse_hand(cards3_6, level)
    for hand in result3_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张4: 连对 - 2张逢人配 + 2张K + 2张A
    cards4_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.KING, Suit.SPADE), Card(Rank.KING, Suit.CLUB),
                 Card(Rank.ACE, Suit.HEART), Card(Rank.ACE, Suit.DIAMOND)]
    print(f"6张4: {[str(card) for card in cards4_6]}")
    result4_6 = parse_hand(cards4_6, level)
    for hand in result4_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张5: 连对 - 2张逢人配 + 2张2 + 2张3
    cards5_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.TWO, Suit.SPADE), Card(Rank.TWO, Suit.CLUB),
                 Card(Rank.THREE, Suit.HEART), Card(Rank.THREE, Suit.DIAMOND)]
    print(f"6张5: {[str(card) for card in cards5_6]}")
    result5_6 = parse_hand(cards5_6, level)
    for hand in result5_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张6: 飞机 - 2张逢人配 + 2张8 + 2张9
    cards6_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.EIGHT, Suit.SPADE), Card(Rank.EIGHT, Suit.CLUB),
                 Card(Rank.NINE, Suit.HEART), Card(Rank.NINE, Suit.DIAMOND)]
    print(f"6张6: {[str(card) for card in cards6_6]}")
    result6_6 = parse_hand(cards6_6, level)
    for hand in result6_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张7: 飞机 - 2张逢人配 + 2张10 + 2张J
    cards7_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                 Card(Rank.TEN, Suit.SPADE), Card(Rank.TEN, Suit.CLUB),
                 Card(Rank.JACK, Suit.HEART), Card(Rank.JACK, Suit.DIAMOND)]
    print(f"6张7: {[str(card) for card in cards7_6]}")
    result7_6 = parse_hand(cards7_6, level)
    for hand in result7_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张8: 飞机 - 2张逢人配 + 2张Q + 2张K
    cards8_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.DIAMOND),
                 Card(Rank.QUEEN, Suit.SPADE), Card(Rank.QUEEN, Suit.CLUB),
                 Card(Rank.KING, Suit.HEART), Card(Rank.KING, Suit.DIAMOND)]
    print(f"6张8: {[str(card) for card in cards8_6]}")
    result8_6 = parse_hand(cards8_6, level)
    for hand in result8_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张9: 飞机 - 2张逢人配 + 2张A + 2张2
    cards9_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.DIAMOND),
                 Card(Rank.ACE, Suit.SPADE), Card(Rank.ACE, Suit.CLUB),
                 Card(Rank.TWO, Suit.HEART), Card(Rank.TWO, Suit.DIAMOND)]
    print(f"6张9: {[str(card) for card in cards9_6]}")
    result9_6 = parse_hand(cards9_6, level)
    for hand in result9_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    # 6张10: 飞机 - 2张逢人配 + 2张3 + 2张4
    cards10_6 = [Card(Rank.SEVEN, Suit.HEART), Card(Rank.SEVEN, Suit.HEART),
                  Card(Rank.THREE, Suit.SPADE), Card(Rank.THREE, Suit.CLUB),
                  Card(Rank.FOUR, Suit.HEART), Card(Rank.FOUR, Suit.DIAMOND)]
    print(f"6张10: {[str(card) for card in cards10_6]}")
    result10_6 = parse_hand(cards10_6, level)
    for hand in result10_6:
        print(f"  牌型: {hand.hand_type}, 主牌: {hand.primary_rank}")
    
    print()
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_specific_hands()
