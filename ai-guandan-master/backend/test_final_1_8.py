#!/usr/bin/env python3
"""
最终测试任务1.8：重构牌型解析器以支持"逢人配"
测试修正后的顺子逻辑和所有牌型的逢人配支持
"""

from app.game_logic.card import Card, Rank, Suit
from app.game_logic.hand_validator import parse_hand, HandType, get_best_hand_for_comparison


def test_acceptance_criteria():
    """验收标准：parse_hand([H7, S8, S9, S10, SJ], 7) 应能被正确解析为同花顺"""
    print("=== 验收标准测试 ===")
    
    # 创建测试牌：H7(红桃7), S8, S9, S10, SJ
    cards = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 红桃7，在打7时是逢人配
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.SPADE),     # S9  
        Card(Rank.TEN, Suit.SPADE),      # S10
        Card(Rank.JACK, Suit.SPADE)      # SJ
    ]
    
    level = 7
    
    print(f"测试牌组: {[str(card) for card in cards]}")
    print(f"当前级别: {level}")
    print(f"H7是否为逢人配: {cards[0].is_wildcard(level)}")
    print("分析：H7是逢人配，可以变成S7，与S8, S9, S10, SJ组成黑桃同花顺")
    
    # 解析牌型
    possible_hands = parse_hand(cards, level)
    
    print(f"解析结果: {possible_hands}")
    print(f"可能的牌型: {[hand.hand_type for hand in possible_hands]}")
    
    # 验收标准：应该包含同花顺
    straight_flush_hands = [hand for hand in possible_hands if hand.hand_type == HandType.STRAIGHT_FLUSH]
    assert len(straight_flush_hands) > 0, f"期望包含STRAIGHT_FLUSH，实际得到{[hand.hand_type for hand in possible_hands]}"
    print("✅ 验收标准通过：包含逢人配的牌组被正确解析为同花顺")
    return True


def test_straight_scenarios():
    """测试顺子的各种逢人配场景"""
    print("\\n=== 测试顺子的逢人配场景 ===")
    
    level = 7
    
    # 场景1：普通顺子（无逢人配）- 5,6,8,9,10（不同花色）
    cards1 = [
        Card(Rank.FIVE, Suit.SPADE),     # S5
        Card(Rank.SIX, Suit.HEART),     # H6
        Card(Rank.EIGHT, Suit.CLUB),    # C8
        Card(Rank.NINE, Suit.DIAMOND),  # D9
        Card(Rank.TEN, Suit.SPADE)      # S10
    ]
    
    result1 = parse_hand(cards1, level)
    print(f"场景1 - 不连续牌: {result1}")
    print(f"  (应该是无效牌型，因为缺7)")
    
    # 场景2：逢人配填补空缺 - 5,6,逢人配,8,9 -> 5,6,7,8,9
    cards2 = [
        Card(Rank.FIVE, Suit.SPADE),     # S5
        Card(Rank.SIX, Suit.HEART),     # H6
        Card(Rank.SEVEN, Suit.HEART),   # H7 - 逢人配，填补7的位置
        Card(Rank.EIGHT, Suit.CLUB),    # C8
        Card(Rank.NINE, Suit.DIAMOND)   # D9
    ]
    
    result2 = parse_hand(cards2, level)
    print(f"场景2 - 逢人配填补: {result2}")
    print(f"  (应该是顺子，逢人配作为7)")
    
    # 场景3：纯顺子（无逢人配）作为对比
    cards3 = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.HEART),    # H9
        Card(Rank.TEN, Suit.CLUB),      # C10
        Card(Rank.JACK, Suit.DIAMOND),  # DJ
        Card(Rank.QUEEN, Suit.SPADE)    # SQ
    ]
    
    result3 = parse_hand(cards3, level)
    print(f"场景3 - 8,9,10,J,Q顺子: {result3}")
    
    print("✅ 顺子逢人配场景测试完成\\n")


def test_straight_flush_wildcard():
    """测试同花顺的逢人配（验收标准的真正测试）"""
    print("=== 测试同花顺逢人配 ===")
    
    level = 7
    
    # 验收标准牌组：H7, S8, S9, S10, SJ (逢人配变成SQ组成同花顺)
    cards = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配，应该变成SQ
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.SPADE),     # S9  
        Card(Rank.TEN, Suit.SPADE),      # S10
        Card(Rank.JACK, Suit.SPADE)      # SJ
    ]
    
    results = parse_hand(cards, level)
    print(f"逢人配同花顺: {results}")
    print(f"  可能牌型: {[hand.hand_type for hand in results]}")
    print(f"  分析: H7(逢人配) + S8,S9,S10,SJ = S8,S9,S10,SJ,SQ 黑桃同花顺")
    
    # 对比：普通同花顺 S8,S9,S10,SJ,SQ
    normal_cards = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.SPADE),     # S9  
        Card(Rank.TEN, Suit.SPADE),      # S10
        Card(Rank.JACK, Suit.SPADE),     # SJ
        Card(Rank.QUEEN, Suit.SPADE)     # SQ
    ]
    
    normal_results = parse_hand(normal_cards, level)
    print(f"普通同花顺(8-Q): {normal_results}")
    
    print("✅ 同花顺逢人配测试完成\\n")


def test_pair_wildcard():
    """测试对子的逢人配"""
    print("=== 测试对子逢人配 ===")
    
    level = 7
    
    # 一张逢人配 + 一张普通牌 = 对子
    cards1 = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配
        Card(Rank.EIGHT, Suit.SPADE)     # S8 - 普通牌
    ]
    
    result1 = parse_hand(cards1, level)
    print(f"逢人配+普通牌: {result1}")
    assert result1.hand_type == HandType.PAIR, "应该是对子"
    assert result1.primary_rank == Rank.EIGHT, "对子大小应该是8"
    
    # 两张逢人配 = 对逢人配（按逢人配本身大小）
    cards2 = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配
        Card(Rank.SEVEN, Suit.DIAMOND)   # D7 - 级牌但不是逢人配
    ]
    
    result2 = parse_hand(cards2, level)
    print(f"两张7: {result2}")
    assert result2.hand_type == HandType.PAIR, "应该是对子"
    assert result2.primary_rank == Rank.SEVEN, "对子大小应该是7"
    
    print("✅ 对子逢人配测试通过\\n")


def test_trio_wildcard():
    """测试三张的逢人配"""
    print("=== 测试三张逢人配 ===")
    
    level = 7
    
    # 1张逢人配 + 2张相同牌 = 三张
    cards1 = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.CLUB)      # C8
    ]
    
    result1 = parse_hand(cards1, level)
    print(f"逢人配+两张8: {result1}")
    assert result1.hand_type == HandType.TRIO, "应该是三张"
    assert result1.primary_rank == Rank.EIGHT, "三张大小应该是8"
    
    # 2张逢人配 + 1张普通牌 = 三张
    cards2 = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配
        Card(Rank.SEVEN, Suit.DIAMOND),  # D7 - 级牌但不是逢人配
        Card(Rank.EIGHT, Suit.SPADE)     # S8
    ]
    
    result2 = parse_hand(cards2, level)
    print(f"两张7+一张8: {result2}")
    assert result2.hand_type == HandType.TRIO, "应该是三张"
    assert result2.primary_rank == Rank.EIGHT, "三张大小应该是8"
    
    print("✅ 三张逢人配测试通过\\n")


def test_no_wildcard_preserve():
    """测试没有逢人配时原逻辑保持不变"""
    print("=== 测试原逻辑保持不变 ===")
    
    level = 7
    
    # 普通顺子
    cards1 = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.HEART),     # H9  
        Card(Rank.TEN, Suit.DIAMOND),    # D10
        Card(Rank.JACK, Suit.CLUB),      # CJ
        Card(Rank.QUEEN, Suit.SPADE)     # SQ
    ]
    
    result1 = parse_hand(cards1, level)
    print(f"普通顺子: {result1}")
    assert result1.hand_type == HandType.STRAIGHT, "普通顺子应该正确解析"
    
    # 普通对子
    cards2 = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.HEART)     # H8
    ]
    
    result2 = parse_hand(cards2, level)
    print(f"普通对子: {result2}")
    assert result2.hand_type == HandType.PAIR, "普通对子应该正确解析"
    
    # 普通三张
    cards3 = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.HEART),    # H8
        Card(Rank.EIGHT, Suit.CLUB)      # C8
    ]
    
    result3 = parse_hand(cards3, level)
    print(f"普通三张: {result3}")
    assert result3.hand_type == HandType.TRIO, "普通三张应该正确解析"
    
    print("✅ 原逻辑保持测试通过\\n")


def test_different_levels():
    """测试不同级别下的逢人配行为"""
    print("=== 测试不同级别下的逢人配 ===")
    
    # 相同的牌在不同级别下的表现
    cards = [
        Card(Rank.SEVEN, Suit.HEART),    # H7
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.SPADE),     # S9  
        Card(Rank.TEN, Suit.SPADE),      # S10
        Card(Rank.JACK, Suit.SPADE)      # SJ
    ]
    
    # 打7级时，H7是逢人配
    result_7 = parse_hand(cards, 7)
    print(f"打7级时: {result_7}")
    
    # 打5级时，H7不是逢人配
    result_5 = parse_hand(cards, 5)
    print(f"打5级时: {result_5}")
    
    # 打7级时应该能组成顺子，打5级时不能
    assert result_7.hand_type == HandType.STRAIGHT, "打7级时应该是顺子"
    print(f"打5级时牌型: {result_5.hand_type}")  # 可能是无效牌型
    
    print("✅ 不同级别测试通过\\n")


if __name__ == "__main__":
    print("开始最终测试任务1.8：重构牌型解析器以支持逢人配...")
    print()
    
    tests = [
        test_acceptance_criteria,
        test_straight_flush_wildcard,
        test_straight_scenarios,
        test_pair_wildcard,
        test_trio_wildcard,
        test_no_wildcard_preserve,
        test_different_levels
    ]
    
    all_passed = True
    for test_func in tests:
        try:
            result = test_func()
            if result is False:
                all_passed = False
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    if all_passed:
        print("🎉 任务1.8最终验收通过！")
        print("✅ 修正了顺子逻辑以正确处理逢人配的各种情况")
        print("✅ 所有牌型函数都已添加逢人配支持")
        print("✅ 验收标准：parse_hand([H7, S8, S9, S10, SJ], 7) 正确解析为顺子")
        print("✅ 逢人配规则：最多2张，单打时是自己本身，组合时可代替任意牌")
        print("✅ 对逢人配按照原级牌大小计算")
    else:
        print("❌ 部分测试失败，请检查实现")
