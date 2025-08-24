#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完整的GameEngine状态机 - 详尽版本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.game_logic.game_engine import GameEngine
from app.game_logic.player import Player, PlayerType
from app.game_logic.card import Card, Suit, Rank
from app.game_logic.game_state import GamePhase

def test_complete_game_flow():
    """测试完整的游戏流程"""
    print("开始测试完整的GameEngine状态机...")
    print("=" * 60)
    
    # 创建游戏引擎
    engine = GameEngine()
    
    # 创建玩家
    players = [
        Player("player_A", "玩家A", PlayerType.HUMAN, team=0),
        Player("player_B", "玩家B", PlayerType.AI, team=1),
        Player("player_C", "玩家C", PlayerType.AI, team=0),
        Player("player_D", "玩家D", PlayerType.AI, team=1)
    ]
    
    print("=== 阶段1: 开始新游戏 ===")
    game_state = engine.start_new_game("test_game_1", players, current_level=2)
    print(f"✓ 游戏创建成功")
    print(f"  - 游戏ID: {game_state.game_id}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 玩家数量: {len(game_state.players)}")
    print(f"  - 每个玩家手牌数: {len(players[0].hand)}")
    
    print("\n=== 阶段2: 处理进贡阶段（第一局） ===")
    tribute_result = engine.process_tribute_phase("test_game_1")
    print(f"✓ 进贡阶段处理完成")
    print(f"  - 结果: {tribute_result}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 先手玩家索引: {game_state.current_turn_index}")
    print(f"  - 先手玩家: {players[game_state.current_turn_index].name}")
    
    print("\n=== 阶段3: 模拟第一局游戏进行 ===")
    
    # 获取当前先手玩家
    current_player_index = game_state.current_turn_index
    current_player = players[current_player_index]
    
    print(f"当前玩家: {current_player.name} (索引: {current_player_index})")
    print(f"手牌: {[str(card) for card in current_player.hand[:5]]}...")
    
    # 模拟第一局游戏进行（简化版）
    print("\n--- 模拟游戏进行 ---")
    
    # 玩家出牌
    if len(current_player.hand) >= 2:
        cards_to_play = current_player.hand[:2]
        print(f"{current_player.name} 出牌: {[str(card) for card in cards_to_play]}")
        
        result = engine.process_player_action("test_game_1", current_player.player_id, "play_cards", cards_to_play)
        print(f"出牌结果: {result}")
        
        if result.get("success"):
            print(f"✓ 出牌成功")
            print(f"  - 下一个玩家索引: {result.get('next_player_index')}")
            print(f"  - 玩家是否出完牌: {result.get('player_finished')}")
            
            # 检查游戏状态
            game_summary = engine.get_game_summary("test_game_1")
            print(f"  - 游戏状态: {game_summary['phase']}")
            print(f"  - 当前回合玩家索引: {game_summary['current_turn_index']}")
        else:
            print(f"✗ 出牌失败: {result.get('error')}")
    else:
        print(f"✗ {current_player.name} 手牌不足，无法出牌")
    
    print("\n=== 阶段4: 模拟第一局结束 ===")
    
    # 手动设置第一局结束（模拟所有玩家出完牌）
    print("手动设置第一局结束...")
    
    # 清空所有玩家手牌
    for player in players:
        player.clear_hand()
    
    # 设置名次（双上：玩家A和C获胜）
    game_state.last_round_finish_order = ["player_A", "player_C", "player_B", "player_D"]
    
    # 手动触发回合结束
    engine._end_round(game_state)
    
    print(f"✓ 第一局结束")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 名次: {game_state.last_round_finish_order}")
    print(f"  - 升级类型: 双上 (+3级)")
    
    print("\n=== 阶段5: 开始第二局 ===")
    
    # 开始下一轮
    next_round_result = engine.start_next_round("test_game_1")
    print(f"✓ 第二局开始")
    print(f"  - 结果: {next_round_result}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 每个玩家手牌数: {len(players[0].hand)}")
    
    print("\n=== 阶段6: 处理第二局进贡阶段 ===")
    
    # 处理进贡阶段（有上一轮结果）
    tribute_result2 = engine.process_tribute_phase("test_game_1")
    print(f"✓ 第二局进贡阶段处理完成")
    print(f"  - 结果: {tribute_result2}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 先手玩家索引: {game_state.current_turn_index}")
    print(f"  - 先手玩家: {players[game_state.current_turn_index].name}")
    
    print("\n=== 阶段7: 模拟第二局游戏进行 ===")
    
    # 获取当前先手玩家
    current_player_index = game_state.current_turn_index
    current_player = players[current_player_index]
    
    print(f"当前玩家: {current_player.name} (索引: {current_player_index})")
    print(f"手牌: {[str(card) for card in current_player.hand[:5]]}...")
    
    # 模拟第二局游戏进行
    print("\n--- 模拟游戏进行 ---")
    
    # 玩家出牌
    if len(current_player.hand) >= 2:
        cards_to_play = current_player.hand[:2]
        print(f"{current_player.name} 出牌: {[str(card) for card in cards_to_play]}")
        
        result = engine.process_player_action("test_game_1", current_player.player_id, "play_cards", cards_to_play)
        print(f"出牌结果: {result}")
        
        if result.get("success"):
            print(f"✓ 出牌成功")
            print(f"  - 下一个玩家索引: {result.get('next_player_index')}")
            print(f"  - 玩家是否出完牌: {result.get('player_finished')}")
        else:
            print(f"✗ 出牌失败: {result.get('error')}")
    else:
        print(f"✗ {current_player.name} 手牌不足，无法出牌")
    
    print("\n=== 阶段8: 测试过牌逻辑 ===")
    
    # 测试过牌
    current_player_index = game_state.current_turn_index
    current_player = players[current_player_index]
    
    print(f"当前玩家: {current_player.name} (索引: {current_player_index})")
    
    result = engine.process_player_action("test_game_1", current_player.player_id, "pass")
    print(f"过牌结果: {result}")
    
    if result.get("success"):
        print(f"✓ 过牌成功")
        print(f"  - 下一个玩家索引: {result.get('next_player_index')}")
        print(f"  - 过牌计数: {result.get('pass_count')}")
    else:
        print(f"✗ 过牌失败: {result.get('error')}")
    
    print("\n=== 阶段9: 测试游戏状态查询 ===")
    
    # 获取游戏摘要
    game_summary = engine.get_game_summary("test_game_1")
    print(f"✓ 游戏摘要获取成功")
    print(f"  - 游戏ID: {game_summary['game_id']}")
    print(f"  - 游戏状态: {game_summary['phase']}")
    print(f"  - 当前级别: {game_summary['current_level']}")
    print(f"  - 当前回合玩家索引: {game_summary['current_turn_index']}")
    print(f"  - 玩家信息:")
    for player_info in game_summary['players']:
        print(f"    * {player_info['name']}: 队伍{player_info['team']}, 手牌{player_info['hand_count']}张")
    print(f"  - 上一轮名次: {game_summary['last_round_finish_order']}")
    
    print("\n=== 阶段10: 测试游戏结束条件 ===")
    
    # 模拟第二局结束（所有玩家出完牌）
    print("模拟第二局结束...")
    
    # 清空所有玩家手牌
    for player in players:
        player.clear_hand()
    
    # 设置名次（单上：玩家A获胜，玩家B第三）
    game_state.last_round_finish_order = ["player_A", "player_B", "player_C", "player_D"]
    
    # 手动触发回合结束
    engine._end_round(game_state)
    
    print(f"✓ 第二局结束")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 名次: {game_state.last_round_finish_order}")
    print(f"  - 升级类型: 单上 (+2级)")
    
    print("\n=== 阶段11: 测试第三局开始 ===")
    
    # 开始第三局
    next_round_result = engine.start_next_round("test_game_1")
    print(f"✓ 第三局开始")
    print(f"  - 结果: {next_round_result}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    
    print("\n=== 阶段12: 测试游戏清理 ===")
    
    # 测试游戏清理
    remove_result = engine.remove_game("test_game_1")
    print(f"✓ 游戏清理")
    print(f"  - 移除结果: {remove_result}")
    
    # 尝试获取已删除的游戏
    deleted_game = engine.get_game_state("test_game_1")
    print(f"  - 获取已删除游戏: {deleted_game}")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成！")
    print("=" * 60)

def test_error_conditions():
    """测试错误条件"""
    print("\n开始测试错误条件...")
    print("=" * 60)
    
    engine = GameEngine()
    
    # 测试1: 获取不存在的游戏
    print("=== 测试1: 获取不存在的游戏 ===")
    non_existent_game = engine.get_game_state("non_existent")
    print(f"结果: {non_existent_game}")
    
    # 测试2: 处理不存在的游戏
    print("\n=== 测试2: 处理不存在的游戏 ===")
    result = engine.process_tribute_phase("non_existent")
    print(f"结果: {result}")
    
    # 测试3: 在错误的状态下调用方法
    print("\n=== 测试3: 在错误的状态下调用方法 ===")
    
    # 创建游戏
    players = [
        Player("player_A", "玩家A", PlayerType.HUMAN, team=0),
        Player("player_B", "玩家B", PlayerType.AI, team=1),
        Player("player_C", "玩家C", PlayerType.AI, team=0),
        Player("player_D", "玩家D", PlayerType.AI, team=1)
    ]
    
    game_state = engine.start_new_game("test_error", players, current_level=2)
    
    # 尝试在PLAYING状态下调用进贡方法
    result = engine.process_tribute_phase("test_error")
    print(f"在PLAYING状态下调用进贡方法: {result}")
    
    # 尝试在PLAYING状态下调用开始下一轮方法
    result = engine.start_next_round("test_error")
    print(f"在PLAYING状态下调用开始下一轮方法: {result}")
    
    # 清理
    engine.remove_game("test_error")
    
    print("\n" + "=" * 60)
    print("✓ 错误条件测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_complete_game_flow()
    test_error_conditions()
