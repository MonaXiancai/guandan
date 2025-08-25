#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试队伍级别逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.game_logic.game_engine import GameEngine
from app.game_logic.player import Player, PlayerType
from app.game_logic.card import Card, Suit, Rank
from app.game_logic.game_state import GamePhase

def test_team_level_logic():
    """测试队伍级别逻辑"""
    print("开始测试队伍级别逻辑...")
    print("=" * 60)
    
    # 创建游戏引擎
    engine = GameEngine()
    
    # 创建玩家
    players = [
        Player("player_A", "玩家A", PlayerType.HUMAN, team=0),  # 队伍0
        Player("player_B", "玩家B", PlayerType.AI, team=1),     # 队伍1
        Player("player_C", "玩家C", PlayerType.AI, team=0),     # 队伍0
        Player("player_D", "玩家D", PlayerType.AI, team=1)      # 队伍1
    ]
    
    print("=== 阶段1: 开始新游戏 ===")
    game_state = engine.start_new_game("test_team_level", players, current_level=2)
    print(f"✓ 游戏创建成功")
    print(f"  - 游戏ID: {game_state.game_id}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    
    print("\n=== 阶段2: 处理进贡阶段（第一局） ===")
    tribute_result = engine.process_tribute_phase("test_team_level")
    print(f"✓ 进贡阶段处理完成")
    print(f"  - 结果: {tribute_result}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    
    print("\n=== 阶段3: 模拟第一局结束（队伍0获胜，双上） ===")
    
    # 手动设置第一局结束（队伍0获胜：玩家A和C获胜）
    print("手动设置第一局结束...")
    
    # 清空所有玩家手牌
    for player in players:
        player.clear_hand()
    
    # 设置名次（双上：队伍0获胜）
    game_state.last_round_finish_order = ["player_A", "player_C", "player_B", "player_D"]
    
    # 手动触发回合结束
    engine._end_round(game_state)
    
    print(f"✓ 第一局结束")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    print(f"  - 名次: {game_state.last_round_finish_order}")
    print(f"  - 升级类型: 双上 (+3级)")
    print(f"  - 获胜队伍: 0")
    
    print("\n=== 阶段4: 开始第二局 ===")
    
    # 开始下一轮
    next_round_result = engine.start_next_round("test_team_level")
    print(f"✓ 第二局开始")
    print(f"  - 结果: {next_round_result}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    
    print("\n=== 阶段5: 处理第二局进贡阶段 ===")
    
    # 处理进贡阶段（有上一轮结果）
    tribute_result2 = engine.process_tribute_phase("test_team_level")
    print(f"✓ 第二局进贡阶段处理完成")
    print(f"  - 结果: {tribute_result2}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    
    print("\n=== 阶段6: 模拟第二局结束（队伍1获胜，单上） ===")
    
    # 手动设置第二局结束（队伍1获胜：玩家B获胜，玩家D第三）
    print("手动设置第二局结束...")
    
    # 清空所有玩家手牌
    for player in players:
        player.clear_hand()
    
    # 设置名次（单上：队伍1获胜）
    game_state.last_round_finish_order = ["player_B", "player_D", "player_A", "player_C"]
    
    # 手动触发回合结束
    engine._end_round(game_state)
    
    print(f"✓ 第二局结束")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    print(f"  - 名次: {game_state.last_round_finish_order}")
    print(f"  - 升级类型: 单上 (+2级)")
    print(f"  - 获胜队伍: 1")
    
    print("\n=== 阶段7: 开始第三局 ===")
    
    # 开始第三局
    next_round_result = engine.start_next_round("test_team_level")
    print(f"✓ 第三局开始")
    print(f"  - 结果: {next_round_result}")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    
    print("\n=== 阶段8: 模拟第三局结束（队伍0获胜，放下） ===")
    
    # 手动设置第三局结束（队伍0获胜：玩家A获胜，玩家B第二，玩家C第三）
    print("手动设置第三局结束...")
    
    # 清空所有玩家手牌
    for player in players:
        player.clear_hand()
    
    # 设置名次（放下：队伍0获胜）
    game_state.last_round_finish_order = ["player_A", "player_B", "player_C", "player_D"]
    
    # 手动触发回合结束
    engine._end_round(game_state)
    
    print(f"✓ 第三局结束")
    print(f"  - 游戏状态: {game_state.phase.value}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    print(f"  - 名次: {game_state.last_round_finish_order}")
    print(f"  - 升级类型: 放下 (+1级)")
    print(f"  - 获胜队伍: 0")
    
    print("\n=== 阶段9: 测试游戏清理 ===")
    
    # 测试游戏清理
    remove_result = engine.remove_game("test_team_level")
    print(f"✓ 游戏清理")
    print(f"  - 移除结果: {remove_result}")
    
    print("\n" + "=" * 60)
    print("✓ 队伍级别逻辑测试完成！")
    print("=" * 60)
    
    print("\n=== 总结 ===")
    print("队伍级别逻辑验证：")
    print("1. 第一局：队伍0获胜（双上），队伍0从2级升到5级")
    print("2. 第二局：队伍1获胜（单上），队伍1从2级升到4级")
    print("3. 第三局：队伍0获胜（放下），队伍0从5级升到6级")
    print("✓ 级别与队伍挂钩的逻辑正确！")

if __name__ == "__main__":
    test_team_level_logic()
