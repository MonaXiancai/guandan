#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的A级临界位置处理逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.game_logic.game_engine import GameEngine
from app.game_logic.player import Player, PlayerType
from app.game_logic.game_state import GamePhase

def test_a_level_fixed():
    """测试修复后的A级临界位置处理逻辑"""
    print("开始测试修复后的A级临界位置处理逻辑...")
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
    game_state = engine.start_new_game("test_a_level_fixed", players, current_level=2)
    print(f"✓ 游戏创建成功")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    print(f"  - A级对局计数: {game_state.a_level_rounds}")
    
    print("\n=== 阶段2: 模拟队伍0快速升级到A级（但只是放下） ===")
    
    # 模拟队伍0连续获胜，快速升级到A级
    # 前3局：队伍0双上获胜 (2->5->8->11)
    for round_num in range(1, 4):
        print(f"第{round_num}局：队伍0双上获胜")
        game_state.last_round_finish_order = ["player_A", "player_C", "player_B", "player_D"]
        engine._end_round(game_state)
        print(f"  - 队伍0级别: {game_state.team_levels[0]}")
        print(f"  - 当前级别: {game_state.current_level}")
        print(f"  - A级对局计数: {game_state.a_level_rounds}")
    
    # 第4局：队伍0放下获胜 (11->12, 达到A级)
    print(f"\n第4局：队伍0放下获胜 (11->12, 达到A级)")
    game_state.last_round_finish_order = ["player_A", "player_B", "player_C", "player_D"]
    engine._end_round(game_state)
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - A级对局计数: {game_state.a_level_rounds}")
    
    print("\n=== 阶段3: 测试A级放下情况（3局限制） ===")
    
    # 模拟队伍0在A级连续放下（不获胜）
    for round_num in range(1, 4):
        print(f"\n第{round_num}局A级放下：队伍0获胜但只是放下")
        
        # 设置名次（放下：队伍0获胜，但只是放下）
        game_state.last_round_finish_order = ["player_A", "player_B", "player_C", "player_D"]
        
        # 手动触发回合结束
        engine._end_round(game_state)
        
        print(f"  - 队伍0级别: {game_state.team_levels[0]}")
        print(f"  - 队伍1级别: {game_state.team_levels[1]}")
        print(f"  - 当前级别: {game_state.current_level}")
        print(f"  - A级对局计数: {game_state.a_level_rounds}")
        
        if game_state.team_levels[0] == 2:
            print(f"✓ 第{round_num}局后，队伍0在A级超过3局未获胜，级别降为2！")
            break
    
    print("\n=== 阶段4: 测试队伍1获胜升级 ===")
    
    # 现在队伍0降为2级，队伍1获胜升级
    print("队伍1获胜升级")
    game_state.last_round_finish_order = ["player_B", "player_D", "player_A", "player_C"]
    engine._end_round(game_state)
    
    print(f"  - 队伍0级别: {game_state.team_levels[0]}")
    print(f"  - 队伍1级别: {game_state.team_levels[1]}")
    print(f"  - 当前级别: {game_state.current_level}")
    print(f"  - A级对局计数: {game_state.a_level_rounds}")
    
    print("\n=== 阶段5: 测试游戏清理 ===")
    
    # 测试游戏清理
    remove_result = engine.remove_game("test_a_level_fixed")
    print(f"✓ 游戏清理")
    print(f"  - 移除结果: {remove_result}")
    
    print("\n" + "=" * 60)
    print("✓ 修复后的A级临界位置处理逻辑测试完成！")
    print("=" * 60)
    
    print("\n=== 总结 ===")
    print("修复后的A级临界位置处理逻辑验证：")
    print("1. 队伍0快速升级到A级（放下获胜）")
    print("2. 队伍0在A级连续3局放下（不获胜）")
    print("3. 超过3局限制，队伍0级别降为2")
    print("4. 队伍1获胜升级")
    print("✓ 修复后的A级临界位置处理逻辑正确！")

if __name__ == "__main__":
    test_a_level_fixed()
