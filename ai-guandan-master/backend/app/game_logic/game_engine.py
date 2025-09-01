#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
掼蛋游戏引擎

负责驱动游戏流程，包括进贡/抗贡逻辑
"""

from typing import List, Dict, Optional, Tuple, Any
from .game_state import GameState, GamePhase, TurnAction
from .player import Player
from .card import Card, Rank, Suit
from .deck import Deck
from .hand_validator import is_valid_play, parse_hand


class TributeInfo:
    """进贡信息"""
    
    def __init__(self, tribute_player_id: str, receive_player_id: str, tribute_count: int = 1, is_first_tribute: bool = True):
        """
        初始化进贡信息
        
        Args:
            tribute_player_id: 进贡玩家ID
            receive_player_id: 接收进贡玩家ID
            tribute_count: 进贡牌数，默认1张
            is_first_tribute: 是否为头游进贡（用于双上情况下区分头游和二游）
        """
        self.tribute_player_id = tribute_player_id
        self.receive_player_id = receive_player_id
        self.tribute_count = tribute_count
        self.is_first_tribute = is_first_tribute  # 是否为头游进贡
        self.is_resisted = False  # 是否抗贡
        self.tribute_cards: List[Card] = []  # 进贡的牌
        self.return_cards: List[Card] = []   # 回贡的牌


class GameEngine:
    """掼蛋游戏引擎"""
    
    def __init__(self):
        """初始化游戏引擎"""
        self.active_games: Dict[str, GameState] = {}
    
    def start_new_game(self, game_id: str, players: List[Player], current_level: int = 2) -> GameState:
        """
        开始新游戏
        
        Args:
            game_id: 游戏ID
            players: 玩家列表（4人）
            current_level: 当前级别，默认从2开始
            
        Returns:
            游戏状态对象
        """
        if len(players) != 4:
            raise ValueError("掼蛋游戏需要4名玩家")
        
        # 创建游戏状态
        game_state = GameState(game_id)
        game_state.current_level = current_level
        
        # 初始化队伍级别
        game_state.team_levels = {0: current_level, 1: current_level}
        
        # 初始化A级对局计数
        game_state.a_level_rounds = {0: 0, 1: 0}
        
        # 设置玩家队伍（0,1,0,1 交替）
        for i, player in enumerate(players):
            player.team = i % 2
            game_state.players.append(player)
        
        # 发牌
        deck = Deck()
        deck.shuffle()
        
        # 掼蛋：每人27张牌，总共108张（两副牌）
        # 使用前108张牌，每人27张
        for i, player in enumerate(players):
            start_index = i * 27
            end_index = start_index + 27
            player_cards = deck.cards[start_index:end_index]
            player.add_cards(player_cards, level=current_level)
        
        # 设置游戏阶段为进贡阶段
        game_state.phase = GamePhase.TRIBUTING
        game_state.current_turn_index = 0
        
        # 保存游戏状态
        self.active_games[game_id] = game_state
        
        return game_state
    
    def process_tribute_phase(self, game_id: str) -> Dict[str, Any]:
        """
        处理进贡阶段
        
        Args:
            game_id: 游戏ID
            
        Returns:
            处理结果字典
        """
        game_state = self.get_game_state(game_id)
        if not game_state:
            return {"success": False, "error": "游戏不存在"}
        
        if game_state.phase != GamePhase.TRIBUTING:
            return {"success": False, "error": "当前不是进贡阶段"}
        
        # 如果是第一局，没有上一轮结果，直接进入游戏阶段
        if not game_state.last_round_finish_order:
            game_state.phase = GamePhase.PLAYING
            # 随机选择先手玩家
            import random
            game_state.current_turn_index = random.randint(0, 3)
            return {
                "success": True,
                "message": "第一局，随机选择先手玩家",
                "first_player_index": game_state.current_turn_index
            }
        
        # 计算进贡信息
        tribute_list = self.calculate_tribute(game_state.last_round_finish_order, game_state.players)
        
        if not tribute_list:
            # 没有进贡，直接进入游戏阶段
            game_state.phase = GamePhase.PLAYING
            # 头游先手
            first_player_id = game_state.last_round_finish_order[0]
            first_player_index = next((i for i, p in enumerate(game_state.players) if p.player_id == first_player_id), 0)
            game_state.current_turn_index = first_player_index
            return {
                "success": True,
                "message": "无进贡，头游先手",
                "first_player_index": first_player_index
            }
        
        # 执行进贡
        tribute_results = self.handle_all_tributes(tribute_list, game_state.players, game_state.current_level)
        
        # 根据进贡结果确定先手玩家
        first_player_index = self._determine_first_player_after_tribute(tribute_results, game_state)
        game_state.current_turn_index = first_player_index
        
        # 切换到游戏阶段
        game_state.phase = GamePhase.PLAYING
        
        return {
            "success": True,
            "tribute_results": tribute_results,
            "first_player_index": first_player_index,
            "message": "进贡完成，确定先手玩家"
        }
    
    def _determine_first_player_after_tribute(self, tribute_results: List[Dict[str, Any]], game_state: GameState) -> int:
        """
        根据进贡结果确定先手玩家
        
        根据掼蛋规则：
        - 若产生进贡，进贡最大牌（给上游）的人先手
        - 若抗贡，上游先手
        
        Args:
            tribute_results: 进贡结果列表
            game_state: 游戏状态
            
        Returns:
            先手玩家的索引
        """
        # 检查是否有抗贡
        has_resistance = any(result.get("resisted", False) for result in tribute_results)
        
        if has_resistance:
            # 抗贡：上游先手
            first_player_id = game_state.last_round_finish_order[0]
            first_player_index = next((i for i, p in enumerate(game_state.players) if p.player_id == first_player_id), 0)
            return first_player_index
        else:
            # 有进贡：进贡最大牌的人先手
            # 找到进贡最大牌的人
            max_tribute_value = -1
            first_player_id = None
            
            for result in tribute_results:
                if result.get("success") and not result.get("resisted"):
                    tribute_card_str = result.get("tribute_card", "")
                    # 解析牌的价值，找到最大的进贡牌
                    if tribute_card_str:
                        # 这里需要解析牌的价值，暂时使用简单的字符串比较
                        # 在实际实现中，应该使用Card对象的价值比较
                        tribute_value = self._get_card_value_from_string(tribute_card_str)
                        if tribute_value > max_tribute_value:
                            max_tribute_value = tribute_value
                            first_player_id = result.get("tribute_player_id")
            
            if first_player_id:
                first_player_index = next((i for i, p in enumerate(game_state.players) if p.player_id == first_player_id), 0)
                return first_player_index
            
            # 如果没有找到，默认头游先手
            first_player_id = game_state.last_round_finish_order[0]
            first_player_index = next((i for i, p in enumerate(game_state.players) if p.player_id == first_player_id), 0)
            return first_player_index
    
    def _get_card_value_from_string(self, card_str: str) -> int:
        """
        从字符串解析牌的价值（用于确定先手玩家）
        
        Args:
            card_str: 牌的字符串表示
            
        Returns:
            牌的价值
        """
        # 简单的字符串解析，实际应该使用Card对象
        if "BIG_JOKER" in card_str:
            return 1000
        elif "SMALL_JOKER" in card_str:
            return 900
        elif "A" in card_str:
            return 14
        elif "K" in card_str:
            return 13
        elif "Q" in card_str:
            return 12
        elif "J" in card_str:
            return 11
        elif "10" in card_str:
            return 10
        else:
            # 数字牌
            for i in range(2, 10):
                if str(i) in card_str:
                    return i
            return 0
    
    def calculate_tribute(self, last_round_finish_order: List[str], players: List[Player]) -> List[TributeInfo]:
        """
        计算进贡信息
        
        根据掼蛋规则：
        1. 若上一局为"双上"（头游和二游同一队），则失败对方两人都需要进贡
        2. 若为"单上"，则末游一人进贡给头游一人
        3. 若为"放下"，则末游一人进贡给头游一人
        
        Args:
            last_round_finish_order: 上一轮结束顺序，按名次排列
            players: 玩家列表，用于判断队伍
            
        Returns:
            进贡信息列表
        """
        if len(last_round_finish_order) != 4:
            return []
        
        # 获取名次对应的玩家
        first_player = next((p for p in players if p.player_id == last_round_finish_order[0]), None)
        second_player = next((p for p in players if p.player_id == last_round_finish_order[1]), None)
        third_player = next((p for p in players if p.player_id == last_round_finish_order[2]), None)
        fourth_player = next((p for p in players if p.player_id == last_round_finish_order[3]), None)
        
        if not all([first_player, second_player, third_player, fourth_player]):
            return []
        
        tribute_list = []
        
        # 判断是否为双上（头游和二游同一队）
        if first_player.team == second_player.team:
            # 双上：失败对方两人都需要进贡
            # 头游获得最大牌，二游获得略小的牌
            tribute_list.append(TributeInfo(third_player.player_id, first_player.player_id, 1, is_first_tribute=True))   # 三游进贡给头游
            tribute_list.append(TributeInfo(fourth_player.player_id, second_player.player_id, 1, is_first_tribute=False)) # 末游进贡给二游
        else:
            # 单上或放下：末游一人进贡给头游一人
            tribute_list.append(TributeInfo(fourth_player.player_id, first_player.player_id, 1, is_first_tribute=True))
        
        return tribute_list
    
    def handle_tribute(self, tribute_info: TributeInfo, players: List[Player], level: int = 2) -> Dict[str, Any]:
        """
        处理单个进贡/抗贡
        
        Args:
            tribute_info: 进贡信息
            players: 玩家列表
            level: 当前级别，用于判断逢人配
            
        Returns:
            处理结果字典
        """
        # 找到进贡方和接收方
        tribute_player = next((p for p in players if p.player_id == tribute_info.tribute_player_id), None)
        receive_player = next((p for p in players if p.player_id == tribute_info.receive_player_id), None)
        
        if not tribute_player or not receive_player:
            return {"success": False, "error": "玩家不存在"}
        
        # 检查是否可以抗贡（有双大王）
        if self._can_resist_tribute(tribute_player):
            tribute_info.is_resisted = True
            return {
                "success": True,
                "resisted": True,
                "message": f"{tribute_player.name} 有双大王，抗贡成功！"
            }
        
        # 执行进贡
        tribute_card = self._select_tribute_card(tribute_player)
        if not tribute_card:
            return {"success": False, "error": "无法选择进贡牌"}
        
        # 从进贡方移除牌
        tribute_player.remove_cards([tribute_card], level)
        
        # 添加到接收方
        receive_player.add_cards([tribute_card], level)
        
        # 记录进贡信息
        tribute_info.tribute_cards = [tribute_card]
        
        # 执行回贡（被进贡的人需要还回一张小于等于10的单牌，但不能是级牌）
        return_card = self._select_return_card(receive_player, level)
        if return_card:
            # 从接收方移除牌
            receive_player.remove_cards([return_card], level)
            
            # 添加到进贡方
            tribute_player.add_cards([return_card], level)
            
            # 记录回贡信息
            tribute_info.return_cards = [return_card]
        
        return {
            "success": True,
            "resisted": False,
            "tribute_card": str(tribute_card),
            "return_card": str(return_card) if return_card else None,
            "message": f"{tribute_player.name} 向 {receive_player.name} 进贡 {tribute_card}，" +
                      (f"{receive_player.name} 回贡 {return_card}" if return_card else f"{receive_player.name} 没有回贡")
        }
    
    def handle_all_tributes(self, tribute_list: List[TributeInfo], players: List[Player], level: int = 2) -> List[Dict[str, Any]]:
        """
        处理所有进贡/抗贡
        
        Args:
            tribute_list: 进贡信息列表
            players: 玩家列表
            level: 当前级别，用于判断逢人配
            
        Returns:
            处理结果列表
        """
        if not tribute_list:
            return []
        
        results = []
        
        # 检查是否为双上情况（有两个进贡信息且都是同一队的）
        is_double_up = len(tribute_list) == 2
        
        if is_double_up:
            # 双上情况：需要特殊处理
            # 1. 先检查抗贡（三四游两人加起来摸到两张大王即可）
            if self._can_resist_tribute_double_up(tribute_list, players):
                # 抗贡成功
                for tribute_info in tribute_list:
                    tribute_info.is_resisted = True
                    results.append({
                        "success": True,
                        "resisted": True,
                        "message": f"双上抗贡成功！三四游有双大王"
                    })
                return results
            
            # 2. 执行进贡：头游获得最大牌，二游获得略小的牌
            # 为每个进贡方分别选择最好的牌
            for i, tribute_info in enumerate(tribute_list):
                tribute_player = next((p for p in players if p.player_id == tribute_info.tribute_player_id), None)
                receive_player = next((p for p in players if p.player_id == tribute_info.receive_player_id), None)
                
                if tribute_player and receive_player:
                    # 为当前进贡方选择最好的牌（排除逢人配）
                    available_cards = [card for card in tribute_player.hand if not card.is_wildcard(level)]
                    
                    if not available_cards:
                        results.append({
                            "success": False,
                            "error": f"{tribute_player.name} 没有可用的进贡牌"
                        })
                        continue
                    
                    # 按价值排序，选择最大的牌
                    available_cards.sort(key=lambda card: self._get_card_value_for_tribute(card), reverse=True)
                    tribute_card = available_cards[0]
                    
                    # 从进贡方移除牌
                    tribute_player.remove_cards([tribute_card], level)
                    
                    # 添加到接收方
                    receive_player.add_cards([tribute_card], level)
                    
                    # 记录进贡信息
                    tribute_info.tribute_cards = [tribute_card]
                    
                    # 执行回贡（被进贡的人需要还回一张小于等于10的单牌，但不能是级牌）
                    return_card = self._select_return_card(receive_player, level)
                    if return_card:
                        receive_player.remove_cards([return_card], level)
                        tribute_player.add_cards([return_card], level)
                        tribute_info.return_cards = [return_card]
                    
                    results.append({
                        "success": True,
                        "resisted": False,
                        "tribute_card": str(tribute_card),
                        "return_card": str(return_card) if return_card else None,
                        "message": f"{tribute_player.name} 向 {receive_player.name} 进贡 {tribute_card}，" +
                                  (f"{receive_player.name} 回贡 {return_card}" if return_card else f"{receive_player.name} 没有回贡")
                    })
        else:
            # 单上或放下情况：按原来的逻辑处理
            for tribute_info in tribute_list:
                result = self.handle_tribute(tribute_info, players, level)
                results.append(result)
        
        return results
    
    def _can_resist_tribute(self, player: Player) -> bool:
        """
        检查单个玩家是否可以抗贡（有双大王）
        
        Args:
            player: 玩家对象
            
        Returns:
            True如果可以抗贡，False否则
        """
        big_jokers = [card for card in player.hand if card.rank == Rank.BIG_JOKER]
        return len(big_jokers) >= 2
    
    def _can_resist_tribute_double_up(self, tribute_list: List[TributeInfo], players: List[Player]) -> bool:
        """
        检查双上情况下是否可以抗贡（三四游两人加起来摸到两张大王即可）
        
        Args:
            tribute_list: 进贡信息列表
            players: 玩家列表
            
        Returns:
            True如果可以抗贡，False否则
        """
        if len(tribute_list) != 2:
            return False
        
        # 获取三四游玩家
        tribute_player_ids = [info.tribute_player_id for info in tribute_list]
        tribute_players = [p for p in players if p.player_id in tribute_player_ids]
        
        # 统计三四游玩家手中的大王总数
        total_big_jokers = 0
        for player in tribute_players:
            big_jokers = [card for card in player.hand if card.rank == Rank.BIG_JOKER]
            total_big_jokers += len(big_jokers)
        
        return total_big_jokers >= 2
    
    def _select_tribute_card(self, player: Player, level: int = 2) -> Optional[Card]:
        """
        选择进贡牌（手牌中最大的牌，但不能进贡逢人配）
        
        根据掼蛋规则：
        进贡通常给最大的一张单牌（包含大小王和级牌），但不能进贡逢人配（级牌红桃）
        
        Args:
            player: 玩家对象
            level: 当前级别，用于判断逢人配
            
        Returns:
            选择的进贡牌，如果没有牌则返回None
        """
        if not player.hand:
            return None
        
        # 过滤掉逢人配（红桃级牌）
        available_cards = [card for card in player.hand if not card.is_wildcard(level)]
        
        if not available_cards:
            return None
        
        # 按牌力值排序，选择最大的牌
        # 王牌 > 级牌 > 普通牌
        sorted_cards = sorted(available_cards, key=lambda card: self._get_card_value_for_tribute(card), reverse=True)
        return sorted_cards[0]
    
    def _select_return_card(self, player: Player, level: int = 2) -> Optional[Card]:
        """
        选择回贡牌（手牌中小于等于10的单牌，但不能是级牌）
        
        根据掼蛋规则：
        被进贡的人需要还回一张小于等于10的单牌，可以挑选，但不能是级牌
        
        Args:
            player: 玩家对象
            level: 当前级别，用于判断级牌
            
        Returns:
            选择的回贡牌，如果没有合适的牌则返回None
        """
        if not player.hand:
            return None
        
        # 选择小于等于10的单牌，且不能是级牌
        suitable_cards = []
        for card in player.hand:
            if (card.rank in [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, 
                             Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN] and
                not card.is_wildcard(level)):  # 排除级牌
                suitable_cards.append(card)
        
        if not suitable_cards:
            return None
        
        # 选择最小的牌作为回贡
        sorted_cards = sorted(suitable_cards, key=lambda card: self._get_card_value_for_tribute(card))
        return sorted_cards[0]
    
    def _get_card_value_for_tribute(self, card: Card) -> int:
        """
        获取牌的价值，用于选择进贡/回贡牌
        
        Args:
            card: 卡牌对象
            
        Returns:
            牌的价值（越大越重要）
        """
        # 王牌最大
        if card.rank == Rank.BIG_JOKER:
            return 1000
        elif card.rank == Rank.SMALL_JOKER:
            return 900
        
        # 普通牌按顺序
        return card.rank.order
    
    def get_game_state(self, game_id: str) -> Optional[GameState]:
        """
        获取游戏状态
        
        Args:
            game_id: 游戏ID
            
        Returns:
            游戏状态对象，如果不存在则返回None
        """
        return self.active_games.get(game_id)
    
    def process_player_action(self, game_id: str, player_id: str, action: str, cards: List[Card] = None) -> Dict[str, Any]:
        """
        处理玩家动作（出牌或过牌）
        
        Args:
            game_id: 游戏ID
            player_id: 玩家ID
            action: 动作类型（"play_cards" 或 "pass"）
            cards: 要出的牌（过牌时为None）
            
        Returns:
            处理结果字典
        """
        game_state = self.get_game_state(game_id)
        if not game_state:
            return {"success": False, "error": "游戏不存在"}
        
        if game_state.phase != GamePhase.PLAYING:
            return {"success": False, "error": "当前不是游戏阶段"}
        
        # 检查是否是当前玩家的回合
        current_player = game_state.players[game_state.current_turn_index]
        if current_player.player_id != player_id:
            return {"success": False, "error": "不是当前玩家的回合"}
        
        if action == "play_cards":
            if not cards:
                return {"success": False, "error": "出牌时必须指定要出的牌"}
            
            # 检查玩家是否拥有这些牌
            if not current_player.has_cards(cards):
                return {"success": False, "error": "玩家没有这些牌"}
            
            # 检查出牌是否合法（调用hand_validator）
            # 验证牌型是否有效
            if not parse_hand(cards, game_state.current_level):
                return {"success": False, "error": "无效的牌型"}
            
            # 检查是否能大过上家（如果有上家出牌的话）
            if game_state.last_played_hand and game_state.last_player_id != player_id:
                if not is_valid_play(cards, game_state.last_played_hand, game_state.current_level):
                    return {
                        "success": False, 
                        "error": f"出牌不能大过上家，请重新选择。上家出牌：{[str(card) for card in game_state.last_played_hand]}"
                    }
            
            # 从玩家手牌中移除牌
            current_player.remove_cards(cards, game_state.current_level)
            
            # 更新游戏状态
            game_state.last_played_hand = cards
            game_state.last_player_id = player_id
            game_state.last_action = TurnAction.PLAY_CARDS
            game_state.pass_count = 0
            
            # 检查玩家是否出完牌
            if len(current_player.hand) == 0:
                self._handle_player_finished(game_state, current_player)
            
            # 移动到下一个玩家
            self._move_to_next_player(game_state)
            
            return {
                "success": True,
                "message": f"{current_player.name} 出牌 {[str(card) for card in cards]}",
                "next_player_index": game_state.current_turn_index,
                "player_finished": len(current_player.hand) == 0
            }
            
        elif action == "pass":
            # 过牌
            game_state.last_action = TurnAction.PASS
            game_state.pass_count += 1
            
            # 检查是否连续3个玩家过牌
            if game_state.pass_count >= game_state.max_pass_count:
                game_state.pass_count = 0
                game_state.last_played_hand = []
                game_state.last_player_id = None
            
            # 移动到下一个玩家
            self._move_to_next_player(game_state)
            
            return {
                "success": True,
                "message": f"{current_player.name} 过牌",
                "next_player_index": game_state.current_turn_index,
                "pass_count": game_state.pass_count
            }
        
        else:
            return {"success": False, "error": "无效的动作类型"}
    
    def _handle_player_finished(self, game_state: GameState, player: Player):
        """
        处理玩家出完牌的情况
        
        Args:
            game_state: 游戏状态
            player: 出完牌的玩家
        """
        # 记录玩家完成顺序
        if player.player_id not in game_state.last_round_finish_order:
            game_state.last_round_finish_order.append(player.player_id)
        
        # 检查是否所有玩家都出完牌
        finished_players = [p for p in game_state.players if len(p.hand) == 0]
        if len(finished_players) == 4:
            # 所有玩家都出完牌，游戏结束
            self._end_round(game_state)
    
    def _move_to_next_player(self, game_state: GameState):
        """
        移动到下一个玩家
        
        Args:
            game_state: 游戏状态
        """
        # 记录当前玩家索引（在更新之前）
        current_index = game_state.current_turn_index
        
        # 简单移动到下一个玩家
        next_index = (current_index + 1) % 4
        game_state.current_turn_index = next_index
        
        # 记录回合转移
        print(f"DEBUG: Turn moved from player_{current_index + 1} to player_{next_index + 1}")
    
    def _end_round(self, game_state: GameState):
        """
        结束一轮游戏
        
        Args:
            game_state: 游戏状态
        """
        game_state.phase = GamePhase.ROUND_OVER
        
        # 计算得分和升级
        self._calculate_score_and_level_up(game_state)
    
    def _calculate_score_and_level_up(self, game_state: GameState):
        """
        计算得分和升级
        
        Args:
            game_state: 游戏状态
        """
        if len(game_state.last_round_finish_order) != 4:
            return
        
        # 获取头游和二游
        first_player_id = game_state.last_round_finish_order[0]
        second_player_id = game_state.last_round_finish_order[1]
        
        first_player = next((p for p in game_state.players if p.player_id == first_player_id), None)
        second_player = next((p for p in game_state.players if p.player_id == second_player_id), None)
        
        if not first_player or not second_player:
            return
        
        # 获取获胜队伍
        winning_team = first_player.team
        
        # 判断升级情况
        if first_player.team == second_player.team:
            # 双上：获胜队伍升级3级
            upgrade_type = "双上"
            level_increase = 3
        elif len(game_state.last_round_finish_order) >= 3:
            # 获取第三名玩家
            third_player_id = game_state.last_round_finish_order[2]
            third_player = next((p for p in game_state.players if p.player_id == third_player_id), None)
            if third_player and first_player.team == third_player.team:
                # 单上：获胜队伍升级2级
                upgrade_type = "单上"
                level_increase = 2
            else:
                # 放下：获胜队伍升级1级
                upgrade_type = "放下"
                level_increase = 1
        else:
            # 放下：获胜队伍升级1级
            upgrade_type = "放下"
            level_increase = 1
        
        # 更新获胜队伍的级别
        # 注意：这里需要为每个队伍单独维护级别
        if not hasattr(game_state, 'team_levels'):
            game_state.team_levels = {0: 2, 1: 2}  # 初始每个队伍都是2级
        
        # 获胜队伍升级
        game_state.team_levels[winning_team] += level_increase
        
        # 当前游戏级别是获胜队伍的级别
        game_state.current_level = game_state.team_levels[winning_team]
        
        # 检查是否达到A级
        if game_state.current_level >= 14:  # A是14
            game_state.current_level = 14  # 限制在A级
            
            # 如果达到A级且获胜，需要特殊处理
            if upgrade_type in ["单上", "双上"]:
                # 达到A级且获胜，游戏结束
                game_state.phase = GamePhase.GAME_END
                return
            else:
                # 达到A级但只是放下，需要记录A级对局次数
                if not hasattr(game_state, 'a_level_rounds'):
                    game_state.a_level_rounds = {0: 0, 1: 0}  # 每个队伍在A级的对局次数
                
                # 记录当前队伍在A级的对局次数
                game_state.a_level_rounds[winning_team] += 1
                
                # 检查是否超过3局限制
                if game_state.a_level_rounds[winning_team] >= 3:
                    # 超过3局限制，该队伍级别降为2
                    game_state.team_levels[winning_team] = 2
                    game_state.current_level = 2
                    # 重置A级对局计数
                    game_state.a_level_rounds[winning_team] = 0
                    print(f"队伍{winning_team}在A级超过3局未获胜，级别降为2")
        else:
            # 如果队伍级别已经是A级，但获胜队伍不是通过单上或双上获胜
            # 需要记录A级对局次数
            if game_state.team_levels[winning_team] >= 14:  # 队伍级别已经是A级
                if not hasattr(game_state, 'a_level_rounds'):
                    game_state.a_level_rounds = {0: 0, 1: 0}
                
                # 记录当前队伍在A级的对局次数
                game_state.a_level_rounds[winning_team] += 1
                
                # 检查是否超过3局限制
                if game_state.a_level_rounds[winning_team] >= 3:
                    # 超过3局限制，该队伍级别降为2
                    game_state.team_levels[winning_team] = 2
                    game_state.current_level = 2
                    # 重置A级对局计数
                    game_state.a_level_rounds[winning_team] = 0
                    print(f"队伍{winning_team}在A级超过3局未获胜，级别降为2")
        
        # 更新队伍信息
        game_state.declarer_team = first_player.team
    
    def start_next_round(self, game_id: str) -> Dict[str, Any]:
        """
        开始下一轮游戏
        
        Args:
            game_id: 游戏ID
            
        Returns:
            处理结果字典
        """
        game_state = self.get_game_state(game_id)
        if not game_state:
            return {"success": False, "error": "游戏不存在"}
        
        if game_state.phase != GamePhase.ROUND_OVER:
            return {"success": False, "error": "当前不是回合结束阶段"}
        
        # 清空上一轮的结果
        game_state.last_round_finish_order = []
        
        # 重置玩家状态
        for player in game_state.players:
            player.clear_hand()
            player.is_finished = False
        
        # 发新牌
        deck = Deck()
        deck.shuffle()
        
        for i, player in enumerate(game_state.players):
            start_index = i * 13
            end_index = start_index + 13
            player_cards = deck.cards[start_index:end_index]
            player.add_cards(player_cards, game_state.current_level)
        
        # 切换到进贡阶段
        game_state.phase = GamePhase.TRIBUTING
        game_state.current_turn_index = 0
        
        return {
            "success": True,
            "message": f"开始第{game_state.current_level}级游戏",
            "current_level": game_state.current_level
        }
    
    def get_game_summary(self, game_id: str) -> Dict[str, Any]:
        """
        获取游戏摘要信息
        
        Args:
            game_id: 游戏ID
            
        Returns:
            游戏摘要字典
        """
        game_state = self.get_game_state(game_id)
        if not game_state:
            return {"error": "游戏不存在"}
        
        return {
            "game_id": game_state.game_id,
            "phase": game_state.phase.value,
            "current_level": game_state.current_level,
            "current_turn_index": game_state.current_turn_index,
            "players": [
                {
                    "player_id": p.player_id,
                    "name": p.name,
                    "team": p.team,
                    "hand_count": len(p.hand),
                    "is_finished": p.is_finished
                }
                for p in game_state.players
            ],
            "last_round_finish_order": game_state.last_round_finish_order,
            "round_number": game_state.round_number
        }
    
    def remove_game(self, game_id: str) -> bool:
        """
        移除游戏
        
        Args:
            game_id: 游戏ID
            
        Returns:
            True如果成功移除，False否则
        """
        if game_id in self.active_games:
            del self.active_games[game_id]
            return True
        return False
