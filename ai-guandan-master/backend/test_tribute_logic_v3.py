#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修正后的进贡/抗贡逻辑 - 回贡不能是级牌
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.game_logic.game_engine import GameEngine, TributeInfo
from app.game_logic.player import Player, PlayerType
from app.game_logic.card import Card, Suit, Rank

def test_tribute_logic_v3():
    """测试修正后的进贡/抗贡逻辑 - 回贡不能是级牌"""
    print("开始修正后的进贡/抗贡逻辑测试 - 回贡不能是级牌...")
    print()
    
    # 创建游戏引擎
    engine = GameEngine()
    
    print("=== 测试1: 双上情况下的进贡 - 回贡不能是级牌 ===")
    
    # 模拟双上情况：头游和二游同一队
    # 玩家A（队伍0）第一名，玩家B（队伍0）第二名
    # 玩家C（队伍1）第三名，玩家D（队伍1）第四名
    last_round_finish_order = ["player_A", "player_B", "player_C", "player_D"]
    
    # 创建玩家
    player_A = Player("player_A", "玩家A", PlayerType.HUMAN, team=0)
    player_B = Player("player_B", "玩家B", PlayerType.AI, team=0)
    player_C = Player("player_C", "玩家C", PlayerType.AI, team=1)
    player_D = Player("player_D", "玩家D", PlayerType.AI, team=1)
    
    # 给三四游一些牌
    player_C.add_cards([
        Card(Rank.ACE, Suit.HEART),      # 红桃A
        Card(Rank.KING, Suit.SPADE),     # 黑桃K
        Card(Rank.TEN, Suit.DIAMOND),    # 方块10
    ], level=7)
    
    player_D.add_cards([
        Card(Rank.QUEEN, Suit.HEART),    # 红桃Q
        Card(Rank.JACK, Suit.SPADE),     # 黑桃J
        Card(Rank.NINE, Suit.DIAMOND),   # 方块9
    ], level=7)
    
    # 给头游和二游一些牌，包括级牌7
    player_A.add_cards([
        Card(Rank.SEVEN, Suit.HEART),    # 红桃7（级牌，不能回贡）
        Card(Rank.EIGHT, Suit.SPADE),    # 黑桃8
        Card(Rank.SIX, Suit.DIAMOND),    # 方块6
    ], level=7)
    
    player_B.add_cards([
        Card(Rank.SEVEN, Suit.SPADE),    # 黑桃7（级牌，不能回贡）
        Card(Rank.FIVE, Suit.HEART),     # 红桃5
        Card(Rank.FOUR, Suit.CLUB),      # 梅花4
    ], level=7)
    
    print(f"头游手牌: {[str(card) for card in player_A.hand]}")
    print(f"二游手牌: {[str(card) for card in player_B.hand]}")
    print(f"三游手牌: {[str(card) for card in player_C.hand]}")
    print(f"末游手牌: {[str(card) for card in player_D.hand]}")
    
    # 计算进贡信息
    tribute_list = engine.calculate_tribute(last_round_finish_order, [player_A, player_B, player_C, player_D])
    print(f"进贡信息数量: {len(tribute_list)}")
    for i, info in enumerate(tribute_list):
        print(f"进贡{i+1}: {info.tribute_player_id} -> {info.receive_player_id}, 是否头游进贡: {info.is_first_tribute}")
    
    # 执行进贡
    results = engine.handle_all_tributes(tribute_list, [player_A, player_B, player_C, player_D], level=7)
    
    print(f"进贡结果: {results}")
    print(f"进贡后头游手牌: {[str(card) for card in player_A.hand]}")
    print(f"进贡后二游手牌: {[str(card) for card in player_B.hand]}")
    print(f"进贡后三游手牌: {[str(card) for card in player_C.hand]}")
    print(f"进贡后末游手牌: {[str(card) for card in player_D.hand]}")
    
    print()
    
    print("=== 测试2: 单上情况下的进贡 - 回贡不能是级牌 ===")
    
    # 模拟单上情况：头游和三游同一队，二游和末游同一队
    # 玩家A（队伍0）第一名，玩家C（队伍1）第二名
    # 玩家B（队伍0）第三名，玩家D（队伍1）第四名
    last_round_finish_order_single = ["player_A", "player_C", "player_B", "player_D"]
    
    # 重新创建玩家
    player_A_single = Player("player_A", "玩家A", PlayerType.HUMAN, team=0)
    player_B_single = Player("player_B", "玩家B", PlayerType.AI, team=0)
    player_C_single = Player("player_C", "玩家C", PlayerType.AI, team=1)
    player_D_single = Player("player_D", "玩家D", PlayerType.AI, team=1)
    
    # 给末游一些牌
    player_D_single.add_cards([
        Card(Rank.ACE, Suit.HEART),      # 红桃A
        Card(Rank.KING, Suit.SPADE),     # 黑桃K
    ], level=7)
    
    # 给头游一些牌，包括级牌7
    player_A_single.add_cards([
        Card(Rank.SEVEN, Suit.HEART),    # 红桃7（级牌，不能回贡）
        Card(Rank.EIGHT, Suit.SPADE),    # 黑桃8
        Card(Rank.SIX, Suit.DIAMOND),    # 方块6
    ], level=7)
    
    print(f"单上情况 - 头游手牌: {[str(card) for card in player_A_single.hand]}")
    print(f"单上情况 - 末游手牌: {[str(card) for card in player_D_single.hand]}")
    
    # 计算进贡信息
    tribute_list_single = engine.calculate_tribute(last_round_finish_order_single, [player_A_single, player_B_single, player_C_single, player_D_single])
    print(f"单上进贡信息数量: {len(tribute_list_single)}")
    
    # 执行进贡
    results_single = engine.handle_all_tributes(tribute_list_single, [player_A_single, player_B_single, player_C_single, player_D_single], level=7)
    
    print(f"单上进贡结果: {results_single}")
    
    print()
    print("=== 测试完成 ===")

if __name__ == "__main__":
    test_tribute_logic_v3()
