#!/usr/bin/env python3
"""
测试任务1.8：重构牌型解析器以支持"逢人配"
"""

from app.game_logic.card import Card, Rank, Suit
from app.game_logic.hand_validator import parse_hand, HandType


def test_acceptance_criteria():
    """验收标准：parse_hand([H7, S8, S9, S10, SJ], 7) 应能被正确解析为顺子"""
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
    
    # 解析牌型
    hand_info = parse_hand(cards, level)
    
    print(f"解析结果: {hand_info}")
    print(f"牌型: {hand_info.hand_type}")
    
    # 验收标准：应该被解析为顺子
    if hand_info.hand_type == HandType.STRAIGHT:
        print("✅ 验收标准通过：包含逢人配的牌组被正确解析为顺子")
        return True
    else:
        print(f"❌ 验收标准失败：期望STRAIGHT，实际得到{hand_info.hand_type}")
        return False


def test_wildcard_single():
    """测试逢人配单打"""
    print("\\n=== 测试逢人配单打 ===")
    
    heart_7 = Card(Rank.SEVEN, Suit.HEART)  # 红桃7在打7时是逢人配
    
    # 逢人配单打时就是自己本身
    hand_info = parse_hand([heart_7], 7)
    
    print(f"红桃7单打: {hand_info}")
    print(f"牌型: {hand_info.hand_type}")
    print(f"主要牌面值: {hand_info.primary_rank}")
    
    assert hand_info.hand_type == HandType.SINGLE, "逢人配单打应该是单牌"
    assert hand_info.primary_rank == Rank.SEVEN, "逢人配单打的牌面值应该是自己本身"
    
    print("✅ 逢人配单打测试通过\\n")


def test_wildcard_pair():
    """测试逢人配组成对子"""
    print("=== 测试逢人配组成对子 ===")
    
    # 一张逢人配 + 一张普通牌 = 对子
    cards1 = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配
        Card(Rank.EIGHT, Suit.SPADE)     # S8 - 普通牌
    ]
    
    hand_info1 = parse_hand(cards1, 7)
    print(f"逢人配+普通牌: {hand_info1}")
    
    assert hand_info1.hand_type == HandType.PAIR, "逢人配+普通牌应该组成对子"
    assert hand_info1.primary_rank == Rank.EIGHT, "对子的牌面值应该是普通牌的牌面值"
    
    # 两张逢人配 = 对逢人配
    cards2 = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配
        Card(Rank.SEVEN, Suit.DIAMOND)   # D7 - 也是级牌但不是逢人配
    ]
    
    # 注意：这里D7不是逢人配，所以这应该是普通的对7
    hand_info2 = parse_hand(cards2, 7)
    print(f"两张7: {hand_info2}")
    
    assert hand_info2.hand_type == HandType.PAIR, "两张7应该组成对子"
    
    print("✅ 逢人配对子测试通过\\n")


def test_wildcard_trio():
    """测试逢人配组成三张"""
    print("=== 测试逢人配组成三张 ===")
    
    # 逢人配 + 两张相同牌 = 三张
    cards = [
        Card(Rank.SEVEN, Suit.HEART),    # H7 - 逢人配
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.CLUB)      # C8
    ]
    
    hand_info = parse_hand(cards, 7)
    print(f"逢人配+两张8: {hand_info}")
    
    assert hand_info.hand_type == HandType.TRIO, "逢人配+两张相同牌应该组成三张"
    assert hand_info.primary_rank == Rank.EIGHT, "三张的牌面值应该是8"
    
    print("✅ 逢人配三张测试通过\\n")


def test_different_levels():
    """测试不同级别下的逢人配"""
    print("=== 测试不同级别下的逢人配 ===")
    
    # 相同的牌在不同级别下有不同的解析结果
    cards = [
        Card(Rank.SEVEN, Suit.HEART),    # H7
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.SPADE),     # S9  
        Card(Rank.TEN, Suit.SPADE),      # S10
        Card(Rank.JACK, Suit.SPADE)      # SJ
    ]
    
    # 打7级时，H7是逢人配，可以组成顺子
    hand_info_7 = parse_hand(cards, 7)
    print(f"打7级时: {hand_info_7}")
    
    # 打5级时，H7不是逢人配，无法组成顺子
    hand_info_5 = parse_hand(cards, 5)
    print(f"打5级时: {hand_info_5}")
    
    assert hand_info_7.hand_type == HandType.STRAIGHT, "打7级时应该是顺子"
    assert hand_info_5.hand_type == HandType.INVALID, "打5级时应该是无效牌型"
    
    print("✅ 不同级别测试通过\\n")


def test_no_wildcard_cases():
    """测试没有逢人配的情况（确保原逻辑仍然正常）"""
    print("=== 测试没有逢人配的情况 ===")
    
    # 普通顺子
    cards = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.NINE, Suit.HEART),     # H9  
        Card(Rank.TEN, Suit.DIAMOND),    # D10
        Card(Rank.JACK, Suit.CLUB),      # CJ
        Card(Rank.QUEEN, Suit.SPADE)     # SQ
    ]
    
    hand_info = parse_hand(cards, 7)
    print(f"普通顺子: {hand_info}")
    
    assert hand_info.hand_type == HandType.STRAIGHT, "普通顺子应该正确解析"
    
    # 普通对子
    pair_cards = [
        Card(Rank.EIGHT, Suit.SPADE),    # S8
        Card(Rank.EIGHT, Suit.HEART)     # H8
    ]
    
    pair_info = parse_hand(pair_cards, 7)
    print(f"普通对子: {pair_info}")
    
    assert pair_info.hand_type == HandType.PAIR, "普通对子应该正确解析"
    
    print("✅ 非逢人配情况测试通过\\n")


def test_edge_cases():
    """测试边界情况"""
    print("=== 测试边界情况 ===")
    
    # 逢人配不能变成王牌的测试
    # 这个测试在牌型解析层面不太容易体现，主要在Card.can_substitute_as方法中
    
    # 测试空牌组
    empty_info = parse_hand([], 7)
    print(f"空牌组: {empty_info}")
    assert empty_info.hand_type == HandType.INVALID, "空牌组应该是无效牌型"
    
    # 测试单张王牌
    joker_info = parse_hand([Card(Rank.BIG_JOKER)], 7)
    print(f"大王单张: {joker_info}")
    assert joker_info.hand_type == HandType.SINGLE, "大王应该是单牌"
    
    print("✅ 边界情况测试通过\\n")


if __name__ == "__main__":
    print("开始测试任务1.8：重构牌型解析器以支持逢人配...")
    print()
    
    tests = [
        test_acceptance_criteria,
        test_wildcard_single,
        test_wildcard_pair,
        test_wildcard_trio,
        test_different_levels,
        test_no_wildcard_cases,
        test_edge_cases
    ]
    
    all_passed = True
    for test_func in tests:
        try:
            result = test_func()
            if result is False:
                all_passed = False
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 失败: {e}")
            all_passed = False
    
    if all_passed:
        print("🎉 任务1.8验收标准全部通过！")
        print("✅ 修改了parse_hand函数签名，增加level参数")
        print("✅ 重写了牌型解析逻辑，支持逢人配万能牌功能")
        print("✅ 验收标准：parse_hand([H7, S8, S9, S10, SJ], 7) 正确解析为顺子")
        print("✅ 逢人配单打时是自己本身，组合时可代替任意牌")
    else:
        print("❌ 部分测试失败，请检查实现")
