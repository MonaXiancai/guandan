"""
掼蛋游戏牌型验证模块

此模块定义了掼蛋游戏中的各种牌型和验证逻辑。
掼蛋的牌型包括：单牌、对子、三带二、顺子、同花顺、炸弹等。
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
from collections import Counter
from .card import Card, Rank, Suit


class HandType(Enum):
    """牌型枚举"""
    INVALID = "INVALID"              # 无效牌型
    SINGLE = "SINGLE"                # 单牌
    PAIR = "PAIR"                    # 对子
    TRIO = "TRIO"                    # 三张
    TRIO_WITH_PAIR = "TRIO_WITH_PAIR"  # 三带二（葫芦）
    STRAIGHT = "STRAIGHT"            # 顺子
    STRAIGHT_FLUSH = "STRAIGHT_FLUSH"  # 同花顺
    STRAIGHT_PAIR = "STRAIGHT_PAIR"  # 连对
    STRAIGHT_TRIO = "STRAIGHT_TRIO"  # 飞机
    BOMB_4 = "BOMB_4"                # 四张炸弹
    BOMB_5 = "BOMB_5"                # 五张炸弹
    BOMB_6 = "BOMB_6"                # 六张炸弹
    BOMB_7 = "BOMB_7"                # 七张炸弹
    BOMB_8 = "BOMB_8"                # 八张炸弹
    JOKER_BOMB = "JOKER_BOMB"        # 王炸（四王）

    def __str__(self):
        return self.value


class HandInfo:
    """
    牌型信息类
    
    包含牌型、主要牌面值、次要牌面值等信息
    """
    
    def __init__(self, hand_type: HandType, primary_rank: Optional[Rank] = None, 
                 secondary_rank: Optional[Rank] = None, length: int = 0,
                 cards: Optional[List[Card]] = None):
        """
        初始化牌型信息
        
        Args:
            hand_type: 牌型
            primary_rank: 主要牌面值（如顺子的最高牌、对子的牌面值）
            secondary_rank: 次要牌面值（如三带二中的对子牌面值）
            length: 牌型长度（如顺子长度、连对长度）
            cards: 原始卡牌列表
        """
        self.hand_type = hand_type
        self.primary_rank = primary_rank
        self.secondary_rank = secondary_rank
        self.length = length
        self.cards = cards or []
    
    def __str__(self):
        if self.hand_type == HandType.INVALID:
            return "无效牌型"
        elif self.hand_type == HandType.SINGLE:
            return f"单牌({self.primary_rank})"
        elif self.hand_type == HandType.PAIR:
            return f"对子({self.primary_rank})"
        elif self.hand_type == HandType.TRIO:
            return f"三张({self.primary_rank})"
        elif self.hand_type == HandType.TRIO_WITH_PAIR:
            return f"三带二({self.primary_rank}带{self.secondary_rank})"
        elif self.hand_type == HandType.STRAIGHT:
            return f"顺子(长度{self.length},最高{self.primary_rank})"
        elif self.hand_type == HandType.STRAIGHT_FLUSH:
            return f"同花顺(长度{self.length},最高{self.primary_rank})"
        elif self.hand_type == HandType.STRAIGHT_PAIR:
            return f"连对(长度{self.length},最高{self.primary_rank})"
        elif self.hand_type == HandType.STRAIGHT_TRIO:
            return f"飞机(长度{self.length},最高{self.primary_rank})"
        elif self.hand_type == HandType.BOMB_4:
            return f"四张炸弹({self.primary_rank})"
        elif self.hand_type == HandType.BOMB_5:
            return f"五张炸弹({self.primary_rank})"
        elif self.hand_type == HandType.BOMB_6:
            return f"六张炸弹({self.primary_rank})"
        elif self.hand_type == HandType.BOMB_7:
            return f"七张炸弹({self.primary_rank})"
        elif self.hand_type == HandType.BOMB_8:
            return f"八张炸弹({self.primary_rank})"
        elif self.hand_type == HandType.JOKER_BOMB:
            return "王炸"
        return str(self.hand_type)
    
    def __repr__(self):
        return f"HandInfo({self.hand_type}, {self.primary_rank}, {self.secondary_rank}, {self.length})"


def _get_rank_counts(cards: List[Card]) -> Dict[Rank, int]:
    """
    统计每个牌面值的数量
    
    Args:
        cards: 卡牌列表
        
    Returns:
        牌面值到数量的映射
    """
    return Counter(card.rank for card in cards)


def _get_wildcards(cards: List[Card], level: int) -> List[Card]:
    """
    获取手牌中的逢人配（红桃级牌）
    
    Args:
        cards: 卡牌列表
        level: 当前级别
        
    Returns:
        逢人配卡牌列表
    """
    return [card for card in cards if card.is_wildcard(level)]


def _get_non_wildcards(cards: List[Card], level: int) -> List[Card]:
    """
    获取手牌中的非逢人配卡牌
    
    Args:
        cards: 卡牌列表
        level: 当前级别
        
    Returns:
        非逢人配卡牌列表
    """
    return [card for card in cards if not card.is_wildcard(level)]




def _get_consecutive_ranks(ranks: List[Rank], min_length: int = 2) -> List[List[Rank]]:
    """
    找出连续的牌面值序列
    
    Args:
        ranks: 排序后的牌面值列表
        min_length: 最小连续长度
        
    Returns:
        连续牌面值序列列表
    """
    if len(ranks) < min_length:
        return []
    
    consecutive_groups = []
    
    # 方案1：正常序列检查（2,3,4...J,Q,K,A）
    normal_sorted = sorted(ranks, key=lambda r: r.order)
    current_group = [normal_sorted[0]]
    
    for i in range(1, len(normal_sorted)):
        if normal_sorted[i].order == normal_sorted[i-1].order + 1:
            current_group.append(normal_sorted[i])
        else:
            if len(current_group) >= min_length:
                consecutive_groups.append(current_group)
            current_group = [normal_sorted[i]]
    
    if len(current_group) >= min_length:
        consecutive_groups.append(current_group)
    
    # 方案2：如果包含A和2，检查A作为1的低位序列（A,2,3,4...）
    if Rank.ACE in ranks and Rank.TWO in ranks:
        # 只有当A可以作为低位时才考虑这种情况
        # 即：A,2,3,4,5... 或 A,2,3,4,5,6... 等
        ace_low_order = {
            Rank.ACE: 1, Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, 
            Rank.FIVE: 5, Rank.SIX: 6, Rank.SEVEN: 7, Rank.EIGHT: 8,
            Rank.NINE: 9, Rank.TEN: 10, Rank.JACK: 11, Rank.QUEEN: 12, 
            Rank.KING: 13
        }
        
        # 只考虑可以形成A开头的低位序列的牌
        ace_low_candidates = []
        for rank in ranks:
            if rank in ace_low_order:
                ace_low_candidates.append(rank)
        
        if len(ace_low_candidates) >= min_length:
            ace_low_sorted = sorted(ace_low_candidates, key=lambda r: ace_low_order[r])
            current_group = [ace_low_sorted[0]]
            
            for i in range(1, len(ace_low_sorted)):
                if ace_low_order[ace_low_sorted[i]] == ace_low_order[ace_low_sorted[i-1]] + 1:
                    current_group.append(ace_low_sorted[i])
                else:
                    if len(current_group) >= min_length and current_group[0] == Rank.ACE:
                        # 只添加以A开头的序列
                        consecutive_groups.append(current_group)
                    current_group = [ace_low_sorted[i]]
            
            if len(current_group) >= min_length and current_group[0] == Rank.ACE:
                consecutive_groups.append(current_group)
    
    return consecutive_groups


def _is_joker_bomb(cards: List[Card]) -> bool:
    """
    判断是否为王炸（四王）
    
    Args:
        cards: 卡牌列表
        
    Returns:
        是否为王炸
    """
    if len(cards) != 4:
        return False
    
    joker_count = sum(1 for card in cards if card.is_joker())
    return joker_count == 4


def _parse_single(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析单牌"""
    if len(cards) != 1:
        return None
    
    # 单牌不需要逢人配替换，逢人配单打时就是自己本身
    return HandInfo(HandType.SINGLE, cards[0].rank, cards=cards)


def _parse_pair(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析对子，支持逢人配"""
    if len(cards) != 2:
        return None
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)
    
    # 没有逢人配的情况，按原逻辑处理
    if not wildcards:
        rank_counts = _get_rank_counts(cards)
        if len(rank_counts) != 1 or list(rank_counts.values())[0] != 2:
            return None
        rank = list(rank_counts.keys())[0]
        return HandInfo(HandType.PAIR, rank, cards=cards)
    
    # 有逢人配的情况
    if len(wildcards) == 1 and len(non_wildcards) == 1:
        # 一张逢人配 + 一张普通牌 = 对子
        return HandInfo(HandType.PAIR, non_wildcards[0].rank, cards=cards)
    elif len(wildcards) == 2 and len(non_wildcards) == 0:
        # 两张逢人配 = 对逢人配，按照逢人配本身的级牌大小
        return HandInfo(HandType.PAIR, wildcards[0].rank, cards=cards)
    elif len(wildcards) >= 1:
        # 其他逢人配组合：检查是否可以与非逢人配牌组成对子
        rank_counts = _get_rank_counts(non_wildcards)
        for rank, count in rank_counts.items():
            if count + len(wildcards) >= 2:
                return HandInfo(HandType.PAIR, rank, cards=cards)
    
    return None


def _parse_trio(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析三张，支持逢人配"""
    if len(cards) != 3:
        return None
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)
    
    # 检查逢人配数量（最多只有两张）
    if len(wildcards) > 2:
        return None
    
    # 没有逢人配的情况
    if not wildcards:
        rank_counts = _get_rank_counts(cards)
        if len(rank_counts) != 1 or list(rank_counts.values())[0] != 3:
            return None
        rank = list(rank_counts.keys())[0]
        return HandInfo(HandType.TRIO, rank, cards=cards)
    
    # 有逢人配的情况
    if len(wildcards) == 1 and len(non_wildcards) == 2:
        # 1张逢人配 + 2张相同普通牌 = 三张
        rank_counts = _get_rank_counts(non_wildcards)
        if len(rank_counts) == 1 and list(rank_counts.values())[0] == 2:
            rank = list(rank_counts.keys())[0]
            return HandInfo(HandType.TRIO, rank, cards=cards)
    elif len(wildcards) == 2 and len(non_wildcards) == 1:
        # 2张逢人配 + 1张普通牌 = 三张
        return HandInfo(HandType.TRIO, non_wildcards[0].rank, cards=cards)
    
    return None


def _parse_trio_with_pair(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析三带二（葫芦），支持逢人配"""
    if len(cards) != 5:
        return None
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)
    
    # 检查逢人配数量（最多只有两张）
    if len(wildcards) > 2:
        return None
    
    # 没有逢人配的情况，按原逻辑处理
    if not wildcards:
        rank_counts = _get_rank_counts(cards)
        
        # 必须是两种牌面值，一种3张一种2张
        if len(rank_counts) != 2:
            return None
        
        counts = sorted(rank_counts.values())
        if counts != [2, 3]:
            return None
        
        # 找出三张的牌面值作为主要牌面值，两张的作为次要牌面值
        trio_rank = None
        pair_rank = None
        
        for rank, count in rank_counts.items():
            if count == 3:
                trio_rank = rank
            elif count == 2:
                pair_rank = rank
        
        return HandInfo(HandType.TRIO_WITH_PAIR, trio_rank, pair_rank, cards=cards)
    
    # 有逢人配的情况
    rank_counts = _get_rank_counts(non_wildcards)
    
    # 情况1：已有三张相同 + 一张单牌 + 一张逢人配（逢人配作为对子的第二张）
    if len(wildcards) == 1:
        for rank, count in rank_counts.items():
            if count == 3:
                # 找到三张，检查是否还有一张单牌
                other_ranks = [r for r, c in rank_counts.items() if r != rank and c == 1]
                if len(other_ranks) == 1:
                    trio_rank = rank
                    pair_rank = other_ranks[0]
                    return HandInfo(HandType.TRIO_WITH_PAIR, trio_rank, pair_rank, cards=cards)
        
        # 情况2：已有两张相同 + 两张相同 + 一张逢人配（逢人配作为三张的第三张）
        # 主牌是非逢人配中更大的那个
        if len(rank_counts) == 2:
            counts = sorted(rank_counts.values())
            if counts == [2, 2]:  # 两个对子 + 一张逢人配
                # 逢人配与更大的对子组成三张，较小的保持为对子
                ranks = list(rank_counts.keys())
                ranks.sort(key=lambda r: r.order, reverse=True)  # 按大小排序，大的在前
                trio_rank = ranks[0]  # 更大的作为三张
                pair_rank = ranks[1]  # 较小的作为对子
                return HandInfo(HandType.TRIO_WITH_PAIR, trio_rank, pair_rank, cards=cards)
    
    # 情况3：两张逢人配的组合
    elif len(wildcards) == 2:
        # 检查非逢人配牌是否能提供基础
        if len(rank_counts) == 1:
            rank, count = list(rank_counts.items())[0]
            if count == 3:
                # 3张相同 + 2张逢人配 = 三带二（逢人配组成对子）
                return HandInfo(HandType.TRIO_WITH_PAIR, rank, wildcards[0].rank, cards=cards)
        elif len(rank_counts) == 2:
            # 可能是 2+1 或 1+1+1的情况
            counts = sorted(rank_counts.values())
            if counts == [1, 2]:  # 一张单牌 + 一对 + 两张逢人配
                # 两张逢人配里2+1的情况：主牌取较大牌
                ranks = list(rank_counts.keys())
                ranks.sort(key=lambda r: r.order, reverse=True)  # 按大小排序
                # 逢人配与较大的牌组成三张
                trio_rank = ranks[0]  # 较大的作为三张（无论是单牌还是对子）
                pair_rank = ranks[1] if len(ranks) > 1 else ranks[0]  # 较小的作为对子
                return HandInfo(HandType.TRIO_WITH_PAIR, trio_rank, pair_rank, cards=cards)
    
    return None


def _parse_straight(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析顺子，支持逢人配"""
    # 顺子只能是5张
    if len(cards) != 5:
        return None
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)
    
    # 检查逢人配数量（最多只有两张）
    if len(wildcards) > 2:
        return None
    
    # 王牌不能组成顺子
    if any(card.is_joker() for card in non_wildcards):
        return None
    
    # 没有逢人配的情况，按原逻辑处理
    if not wildcards:
        rank_counts = _get_rank_counts(cards)
        if any(count != 1 for count in rank_counts.values()):
            return None
        
        sorted_ranks = sorted(rank_counts.keys(), key=lambda r: r.order)
        consecutive_groups = _get_consecutive_ranks(sorted_ranks, len(cards))
        
        if not consecutive_groups or len(consecutive_groups[0]) != len(cards):
            return None
        
        highest_rank = max(sorted_ranks, key=lambda r: r.order)
        return HandInfo(HandType.STRAIGHT, highest_rank, length=len(cards), cards=cards)
    
    # 有逢人配的处理：检查非逢人配牌是否可以通过填补形成顺子
    if len(non_wildcards) >= 3:  # 至少需要3张非逢人配牌作为基础
        non_wildcard_ranks = sorted([card.rank for card in non_wildcards], key=lambda r: r.order)
        min_rank = min(non_wildcard_ranks, key=lambda r: r.order)
        max_rank = max(non_wildcard_ranks, key=lambda r: r.order)
        min_order = min_rank.order
        max_order = max_rank.order
        
        # 计算跨度
        span = max_order - min_order
        wildcard_count = len(wildcards)
        
        # 情况一：五张牌的跨度（跨度为4），逢人配填补空缺
        if span == 4:
            needed_gaps = 5 - len(non_wildcards)
            if needed_gaps == wildcard_count:
                return HandInfo(HandType.STRAIGHT, max_rank, length=5, cards=cards)
        
        # 情况二：四张牌的跨度（跨度为3），一张逢人配填补空缺，另一张放在后面
        elif span == 3 and wildcard_count == 2:
            needed_gaps = 4 - len(non_wildcards)  # 4张牌跨度需要填补的空缺
            if needed_gaps == 1:  # 只需要1张逢人配填补空缺
                # 另一张逢人配放在后面，最大牌是max(A, 最大的+1)
                if max_order < 14:  # 还没到A
                    final_max_order = max_order + 1
                    # 找到对应的Rank
                    for rank in Rank:
                        if rank.order == final_max_order and rank not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
                            return HandInfo(HandType.STRAIGHT, rank, length=5, cards=cards)
                else:  # 已经是A，那么只能是A-2-3-4-5的A开头顺子
                    return HandInfo(HandType.STRAIGHT, Rank.ACE, length=5, cards=cards)
        
        # 情况三：三张牌跨度（跨度为2），两张逢人配补位
        elif span == 2 and wildcard_count == 2:
            # 两张逢人配都放在后面，最大牌是max(A, 最大的+2)
            if max_order < 13:  # 还能放两张
                final_max_order = max_order + 2
                # 找到对应的Rank
                for rank in Rank:
                    if rank.order == final_max_order and rank not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
                        return HandInfo(HandType.STRAIGHT, rank, length=5, cards=cards)
            else:  # 已经到K或A，需要特殊处理
                return HandInfo(HandType.STRAIGHT, Rank.ACE, length=5, cards=cards)
        
        # 情况四：跨度为1（相邻两张）或跨度为0（相同牌面值，但这种情况不可能组成顺子）
        elif span == 1 and wildcard_count == 2:
            # 两张逢人配放在前后，形成5张连续
            if min_order > 2:  # 前面还能放一张
                if max_order < 14:  # 后面还能放一张
                    final_max_order = max_order + 1
                    for rank in Rank:
                        if rank.order == final_max_order and rank not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
                            return HandInfo(HandType.STRAIGHT, rank, length=5, cards=cards)
        
        # 处理单张逢人配的情况
        elif wildcard_count == 1:
            # 检查是否能通过一张逢人配形成连续序列
            # 需要验证4张非逢人配牌中是否有且仅有一个空缺
            if span == 4:  # 5张牌跨度，需要填补1个空缺
                # 计算实际需要的空缺数
                full_sequence = list(range(min_order, max_order + 1))
                existing_orders = [r.order for r in non_wildcard_ranks]
                gaps = [order for order in full_sequence if order not in existing_orders]
                
                if len(gaps) == 1:  # 正好1个空缺，可以用逢人配填补
                    return HandInfo(HandType.STRAIGHT, max_rank, length=5, cards=cards)
            elif span == 3:  # 4张牌跨度，逢人配放在末尾
                if len(non_wildcards) == 4:  # 4张非逢人配牌连续
                    if max_order < 14:
                        final_max_order = max_order + 1
                        for rank in Rank:
                            if rank.order == final_max_order and rank not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
                                return HandInfo(HandType.STRAIGHT, rank, length=5, cards=cards)
    
    return None


def _parse_straight_flush(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析同花顺，支持逢人配"""
    # 同花顺只能是5张
    if len(cards) != 5:
        return None
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)
    
    # 检查逢人配数量（最多只有两张）
    if len(wildcards) > 2:
        return None
    
    # 王牌不能组成同花顺
    if any(card.is_joker() for card in non_wildcards):
        return None
    
    # 检查是否为同一花色（忽略逢人配，因为逢人配可以变成任意花色）
    if non_wildcards:
        non_wildcard_suits = [card.suit for card in non_wildcards]
        if len(set(non_wildcard_suits)) != 1:
            return None  # 非逢人配牌必须是同花色
    
    # 先检查是否能构成顺子结构
    straight_info = _parse_straight(cards, level)
    if not straight_info or straight_info.hand_type != HandType.STRAIGHT:
        return None
    
    # 如果能构成顺子且满足同花条件，则为同花顺
    return HandInfo(HandType.STRAIGHT_FLUSH, straight_info.primary_rank, length=5, cards=cards)


def _parse_straight_pair(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析连对，支持逢人配"""
    # 连对只能是3对（6张牌）
    if len(cards) != 6:
        return None
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)
    
    # 检查逢人配数量（最多只有两张）
    if len(wildcards) > 2:
        return None
    
    # 王牌不能组成连对
    if any(card.is_joker() for card in non_wildcards):
        return None
    
    # 没有逢人配的情况，按原逻辑处理
    if not wildcards:
        rank_counts = _get_rank_counts(cards)
        
        # 连对中每个牌面值都必须出现2次
        if any(count != 2 for count in rank_counts.values()):
            return None
        
        # 检查是否为连续序列
        sorted_ranks = sorted(rank_counts.keys(), key=lambda r: r.order)
        expected_length = len(cards) // 2  # 应该是3
        consecutive_groups = _get_consecutive_ranks(sorted_ranks, expected_length)
        
        if not consecutive_groups or len(consecutive_groups[0]) != expected_length:
            return None
        
        highest_rank = max(sorted_ranks, key=lambda r: r.order)
        return HandInfo(HandType.STRAIGHT_PAIR, highest_rank, length=expected_length, cards=cards)
    
    # 有逢人配的情况：重写连对逻辑
    rank_counts = _get_rank_counts(non_wildcards)
    
    if len(wildcards) == 1:
        # 一张逢人配：剩下必须是三连对缺一张
        pair_count = sum(1 for count in rank_counts.values() if count == 2)
        if pair_count == 2:  # 两对 + 一张单牌 + 一张逢人配
            # 检查是否有单牌可以与逢人配组成第三对
            single_ranks = [rank for rank, count in rank_counts.items() if count == 1]
            if len(single_ranks) == 1:
                # 检查三对是否连续
                pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
                all_ranks = pair_ranks + single_ranks
                sorted_ranks = sorted(all_ranks, key=lambda r: r.order)
                
                # 检查连续性（跨度为2）
                if len(sorted_ranks) == 3 and (sorted_ranks[-1].order - sorted_ranks[0].order) == 2:
                    highest_rank = max(sorted_ranks, key=lambda r: r.order)
                    return HandInfo(HandType.STRAIGHT_PAIR, highest_rank, length=3, cards=cards)
    
    elif len(wildcards) == 2:
        # 两张逢人配
        pair_count = sum(1 for count in rank_counts.values() if count == 2)
        
        if pair_count == 2:
            # 剩下四张牌跨度为2（极差为1），且为两对
            pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            sorted_ranks = sorted(pair_ranks, key=lambda r: r.order)
            span = sorted_ranks[-1].order - sorted_ranks[0].order
            
            if span == 1:  # 极差为1，最大牌为max(A, 更大牌+1)
                # 两张逢人配组成中间或末尾的对子
                highest_rank = max(sorted_ranks[-1], Card._level_to_rank(min(14, sorted_ranks[-1].order + 1)), key=lambda r: r.order)
                return HandInfo(HandType.STRAIGHT_PAIR, highest_rank, length=3, cards=cards)
            elif span == 2:  # 跨度为3，需要连续的三个数字
                # 两张逢人配填补中间的对子
                highest_rank = max(sorted_ranks, key=lambda r: r.order)
                return HandInfo(HandType.STRAIGHT_PAIR, highest_rank, length=3, cards=cards)
        elif pair_count == 1:
            # 一张单牌 + 一张单牌 + 两张逢人配
            # 检查是否有两张单牌可以与逢人配组成连续的三对
            single_ranks = [rank for rank, count in rank_counts.items() if count == 1]
            if len(single_ranks) == 2:
                # 检查三张牌是否连续
                all_ranks = pair_ranks + single_ranks
                sorted_ranks = sorted(all_ranks, key=lambda r: r.order)
                
                # 检查连续性（跨度为2）
                if len(sorted_ranks) == 3 and (sorted_ranks[-1].order - sorted_ranks[0].order) == 2:
                    highest_rank = max(sorted_ranks, key=lambda r: r.order)
                    return HandInfo(HandType.STRAIGHT_PAIR, highest_rank, length=3, cards=cards)
    
    return None


def _parse_straight_trio(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析飞机（连续的三张），支持逢人配"""
    # 飞机只能是2组（6张牌）
    if len(cards) != 6:
        return None
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)
    
    # 检查逢人配数量（最多只有两张）
    if len(wildcards) > 2:
        return None
    
    # 王牌不能组成飞机
    if any(card.is_joker() for card in non_wildcards):
        return None
    
    # 没有逢人配的情况，按原逻辑处理
    if not wildcards:
        rank_counts = _get_rank_counts(cards)
        
        # 飞机中每个牌面值都必须出现3次
        if any(count != 3 for count in rank_counts.values()):
            return None
        
        # 检查是否为连续序列
        sorted_ranks = sorted(rank_counts.keys(), key=lambda r: r.order)
        expected_length = len(cards) // 3  # 应该是2
        consecutive_groups = _get_consecutive_ranks(sorted_ranks, expected_length)
        
        if not consecutive_groups or len(consecutive_groups[0]) != expected_length:
            return None
        
        highest_rank = max(sorted_ranks, key=lambda r: r.order)
        return HandInfo(HandType.STRAIGHT_TRIO, highest_rank, length=expected_length, cards=cards)
    
    # 有逢人配的情况：重写飞机逻辑
    rank_counts = _get_rank_counts(non_wildcards)
    
    if len(wildcards) == 1:
        # 一张逢人配：剩下必须是连续的3张和两张，主牌取大牌
        trio_count = sum(1 for count in rank_counts.values() if count == 3)
        pair_count = sum(1 for count in rank_counts.values() if count == 2)
        
        if trio_count == 1 and pair_count == 1:
            # 一个三张 + 一个对子 + 一张逢人配
            trio_ranks = [rank for rank, count in rank_counts.items() if count == 3]
            pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            
            # 检查三张和对子是否连续
            all_ranks = trio_ranks + pair_ranks
            sorted_ranks = sorted(all_ranks, key=lambda r: r.order)
            
            if len(sorted_ranks) == 2 and (sorted_ranks[1].order - sorted_ranks[0].order) == 1:
                highest_rank = max(sorted_ranks, key=lambda r: r.order)
                return HandInfo(HandType.STRAIGHT_TRIO, highest_rank, length=2, cards=cards)
    
    elif len(wildcards) == 2:
        # 两张逢人配：剩下的必须是连续的三张和一张或者两对，主牌取大牌
        trio_count = sum(1 for count in rank_counts.values() if count == 3)
        pair_count = sum(1 for count in rank_counts.values() if count == 2)
        single_count = sum(1 for count in rank_counts.values() if count == 1)
        
        if trio_count == 1 and single_count == 1:
            # 一个三张 + 一张单牌 + 两张逢人配
            trio_ranks = [rank for rank, count in rank_counts.items() if count == 3]
            single_ranks = [rank for rank, count in rank_counts.items() if count == 1]
            
            all_ranks = trio_ranks + single_ranks
            sorted_ranks = sorted(all_ranks, key=lambda r: r.order)
            
            if len(sorted_ranks) == 2 and (sorted_ranks[1].order - sorted_ranks[0].order) == 1:
                highest_rank = max(sorted_ranks, key=lambda r: r.order)
                return HandInfo(HandType.STRAIGHT_TRIO, highest_rank, length=2, cards=cards)
        
        elif pair_count == 2:
            # 两个对子 + 两张逢人配
            pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            sorted_ranks = sorted(pair_ranks, key=lambda r: r.order)
            
            if len(sorted_ranks) == 2 and (sorted_ranks[1].order - sorted_ranks[0].order) == 1:
                highest_rank = max(sorted_ranks, key=lambda r: r.order)
                return HandInfo(HandType.STRAIGHT_TRIO, highest_rank, length=2, cards=cards)
    
    return None


def _parse_bomb(cards: List[Card], level: int = 2) -> Optional[HandInfo]:
    """解析炸弹，支持逢人配: 原牌数+逢人配张数=炸弹最终张数"""
    if len(cards) < 4:
        return None
    
    # 先检查是否为王炸
    if _is_joker_bomb(cards):
        return HandInfo(HandType.JOKER_BOMB, cards=cards)
    
    wildcards = _get_wildcards(cards, level)
    non_wildcards = _get_non_wildcards(cards, level)

    if any(card.is_joker() for card in non_wildcards):
        return None
    # 没有逢人配的情况
    if not wildcards:
        rank_counts = _get_rank_counts(cards)
        # 炸弹必须是4张或更多相同牌面值的牌
        if len(rank_counts) != 1:
            return None
        
        rank, count = list(rank_counts.items())[0]
        if count < 4:
            return None
    else:
        # 有逢人配的情况：逢人配可以和相同牌面值的牌组成炸弹
        if not non_wildcards:
            return None  # 纯逢人配无法组成炸弹
        
        rank_counts = _get_rank_counts(non_wildcards)
        if len(rank_counts) != 1:
            return None  # 非逢人配必须是相同牌面值
        
        rank, count = list(rank_counts.items())[0]
        total_count = count + len(wildcards)
        if total_count < 4:
            return None
        
        count = total_count  # 总张数
    
    # 根据炸弹张数确定类型
    bomb_type_map = {
        4: HandType.BOMB_4,
        5: HandType.BOMB_5,
        6: HandType.BOMB_6,
        7: HandType.BOMB_7,
        8: HandType.BOMB_8
    }
    
    bomb_type = bomb_type_map.get(count)
    if not bomb_type:
        # 超过8张的炸弹按8张炸弹处理
        bomb_type = HandType.BOMB_8
    
    return HandInfo(bomb_type, rank, cards=cards)


def parse_hand(cards: List[Card], level: int = 2) -> List[HandInfo]:
    """
    解析手牌牌型，支持逢人配（红桃级牌）万能牌功能，返回所有可能的牌型
    
    Args:
        cards: 已排序的卡牌列表
        level: 当前打的级别（2-14），用于识别逢人配
        
    Returns:
        所有可能的牌型信息对象列表
    """
    if not cards:
        return []
    
    possible_hands = []
    card_count = len(cards)
    
    # 先尝试解析炸弹（包括王炸）
    bomb_info = _parse_bomb(cards, level)
    if bomb_info:
        possible_hands.append(bomb_info)
    
    # 根据牌数解析其他牌型
    if card_count == 1:
        result = _parse_single(cards, level)
        if result:
            possible_hands.append(result)
    elif card_count == 2:
        result = _parse_pair(cards, level)
        if result:
            possible_hands.append(result)
    elif card_count == 3:
        result = _parse_trio(cards, level)
        if result:
            possible_hands.append(result)
    elif card_count == 5:
        # 可能是三带二、同花顺或顺子
        trio_pair_result = _parse_trio_with_pair(cards, level)
        if trio_pair_result:
            possible_hands.append(trio_pair_result)
            
        straight_flush_result = _parse_straight_flush(cards, level)
        if straight_flush_result:
            possible_hands.append(straight_flush_result)
            
        straight_result = _parse_straight(cards, level)
        if straight_result:
            possible_hands.append(straight_result)
    elif card_count == 6:
        # 可能是连对或飞机
        straight_pair_result = _parse_straight_pair(cards, level)
        if straight_pair_result:
            possible_hands.append(straight_pair_result)
            
        straight_trio_result = _parse_straight_trio(cards, level)
        if straight_trio_result:
            possible_hands.append(straight_trio_result)
    
    return possible_hands


def get_best_hand_for_comparison(possible_hands: List[HandInfo], target_hand_type: HandType, level: int = 2) -> Optional[HandInfo]:
    """
    从多个可能的牌型中选择最适合与目标牌型比较的牌型，支持级牌最大
    
    Args:
        possible_hands: 所有可能的牌型
        target_hand_type: 目标牌型（要比较的牌型）
        level: 当前级别，用于判断级牌
        
    Returns:
        最适合比较的牌型，如果没有可比较的牌型则返回None
    """
    if not possible_hands:
        return None
    
    # 首先尝试找到相同类型的牌型
    same_type_hands = [hand for hand in possible_hands if hand.hand_type == target_hand_type]
    if same_type_hands:
        # 如果有多个相同类型，选择最大的（考虑级牌）
        return max(same_type_hands, key=lambda h: _get_rank_value_for_comparison(h.primary_rank, level))
    
    # 如果没有相同类型，检查是否有特殊牌型（炸弹、同花顺）可以压制
    special_hands = [hand for hand in possible_hands if hand.hand_type in [
        HandType.JOKER_BOMB, HandType.BOMB_8, HandType.BOMB_7, HandType.BOMB_6, 
        HandType.BOMB_5, HandType.BOMB_4, HandType.STRAIGHT_FLUSH
    ]]
    
    if special_hands:
        # 返回强度最高的特殊牌型
        return max(special_hands, key=get_hand_strength)
    
    return None


def _get_rank_value_for_comparison(rank: Optional[Rank], level: int) -> int:
    """
    获取牌面值用于比较，支持级牌大于普通牌小于王牌
    
    Args:
        rank: 牌面值
        level: 当前级别
        
    Returns:
        用于比较的数值，越大表示越强
    """
    if not rank:
        return 0
    
    # 王牌最大
    if rank in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
        if rank == Rank.BIG_JOKER:
            return 2000  # 大王最大
        else:
            return 1500  # 小王次之
    
    # 级牌大于普通牌（但小于王牌）
    if rank.value == str(level):
        return 1000 + rank.order
    
    # 普通牌按正常顺序
    return rank.order


def is_valid_hand(cards: List[Card], level: int = 2) -> bool:
    """
    判断给定的牌是否构成有效牌型
    
    Args:
        cards: 卡牌列表
        level: 当前级别
        
    Returns:
        是否为有效牌型
    """
    if not cards:
        return False
    
    possible_hands = parse_hand(cards, level)
    return len(possible_hands) > 0


def get_hand_strength(hand_info: HandInfo) -> int:
    """
    获取牌型强度值，用于比较不同牌型的大小
    
    大小顺序：王炸 > 六张以上炸弹 > 同花顺 > 五张炸弹 > 四张炸弹 > 其他牌型
    
    Args:
        hand_info: 牌型信息
        
    Returns:
        牌型强度值，越大越强
    """
    strength_map = {
        HandType.INVALID: 0,
        HandType.SINGLE: 1,
        HandType.PAIR: 2,
        HandType.TRIO: 3,
        HandType.STRAIGHT: 4,
        HandType.STRAIGHT_PAIR: 5,
        HandType.TRIO_WITH_PAIR: 6,
        HandType.STRAIGHT_TRIO: 7,
        HandType.BOMB_4: 8,        # 四张炸弹
        HandType.BOMB_5: 9,        # 五张炸弹
        HandType.STRAIGHT_FLUSH: 10,  # 同花顺
        HandType.BOMB_6: 11,       # 六张炸弹
        HandType.BOMB_7: 12,       # 七张炸弹
        HandType.BOMB_8: 13,       # 八张炸弹
        HandType.JOKER_BOMB: 14    # 王炸
    }
    
    return strength_map.get(hand_info.hand_type, 0)


def is_ace_low_straight(hand_info: HandInfo) -> bool:
    """
    判断连续牌型是否以A开头（A-2-3...的形式）
    
    以A开头的连续牌在比较时被认为是最小的
    
    Args:
        hand_info: 牌型信息
        
    Returns:
        是否为以A开头的连续牌
    """
    if hand_info.hand_type not in [HandType.STRAIGHT, HandType.STRAIGHT_FLUSH, 
                                   HandType.STRAIGHT_PAIR, HandType.STRAIGHT_TRIO]:
        return False
    
    if not hand_info.cards:
        return False
    
    # 检查是否包含A和2
    ranks = [card.rank for card in hand_info.cards]
    return Rank.ACE in ranks and Rank.TWO in ranks


def _compare_same_hand_type(new_hand: HandInfo, last_hand: HandInfo, level: int = 2) -> bool:
    """
    比较相同牌型的大小，支持级牌最大
    
    Args:
        new_hand: 新出的牌型信息
        last_hand: 上一手牌型信息
        level: 当前级别，用于判断级牌
        
    Returns:
        True如果新牌能大过上一手牌，否则False
    """
    # 检查牌型是否相同
    if new_hand.hand_type != last_hand.hand_type:
        return False
    
    # 对于连续牌型，需要检查长度是否相同
    if new_hand.hand_type in [HandType.STRAIGHT, HandType.STRAIGHT_FLUSH, 
                              HandType.STRAIGHT_PAIR, HandType.STRAIGHT_TRIO]:
        if new_hand.length != last_hand.length:
            return False
        
        # 特殊处理A开头的连续牌（被认为是最小的）
        new_is_ace_low = is_ace_low_straight(new_hand)
        last_is_ace_low = is_ace_low_straight(last_hand)
        
        if new_is_ace_low and not last_is_ace_low:
            # 新牌是A开头，上一手不是，新牌更小
            return False
        elif not new_is_ace_low and last_is_ace_low:
            # 新牌不是A开头，上一手是，新牌更大
            return True
        else:
            # 都是A开头或都不是A开头，比较主要牌面值
            return _compare_rank_with_level(new_hand.primary_rank, last_hand.primary_rank, level)
    
    # 对于三带二，主要比较三张的牌面值
    if new_hand.hand_type == HandType.TRIO_WITH_PAIR:
        return _compare_rank_with_level(new_hand.primary_rank, last_hand.primary_rank, level)
    
    # 对于炸弹，比较牌面值（级牌炸弹大于普通炸弹）
    if new_hand.hand_type in [HandType.BOMB_4, HandType.BOMB_5, HandType.BOMB_6, 
                              HandType.BOMB_7, HandType.BOMB_8]:
        return _compare_rank_with_level(new_hand.primary_rank, last_hand.primary_rank, level)
    
    # 对于其他牌型（单牌、对子、三张），比较主要牌面值
    if new_hand.primary_rank and last_hand.primary_rank:
        return _compare_rank_with_level(new_hand.primary_rank, last_hand.primary_rank, level)
    
    return False


def _compare_rank_with_level(rank1: Rank, rank2: Rank, level: int) -> bool:
    """
    比较两个牌面值的大小，支持级牌大于普通牌小于王牌
    
    Args:
        rank1: 第一个牌面值
        rank2: 第二个牌面值
        level: 当前级别
        
    Returns:
        True如果rank1大于rank2，否则False
    """
    # 王牌最大
    if rank1 in [Rank.SMALL_JOKER, Rank.BIG_JOKER] and rank2 not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
        return True
    if rank1 not in [Rank.SMALL_JOKER, Rank.BIG_JOKER] and rank2 in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
        return False
    
    # 级牌大于普通牌（但小于王牌）
    if rank1.value == str(level) and rank2.value != str(level) and rank2 not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
        return True
    if rank1.value != str(level) and rank2.value == str(level) and rank1 not in [Rank.SMALL_JOKER, Rank.BIG_JOKER]:
        return False
    
    # 如果都是级牌或都不是级牌，按正常顺序比较
    return rank1.order > rank2.order


def is_valid_play(new_hand: List[Card], last_hand: List[Card], level: int = 2) -> bool:
    """
    判断新出的牌是否能大过上一手牌
    
    根据掼蛋规则：
    1. 炸弹可以大过任何非炸弹牌型
    2. 王炸最大
    3. 六张以上炸弹大于同花顺大于五张炸弹大于四张炸弹
    4. 相同牌型比较牌面值大小
    5. 以A开头的连续牌被认为是最小的
    
    Args:
        new_hand: 新出的牌列表
        last_hand: 上一手牌列表
        level: 当前级别
        
    Returns:
        True如果新牌能大过上一手牌，否则False
    """
    if not new_hand:
        return False
    
    # 如果上一手为空，任何有效牌型都可以出
    if not last_hand:
        return is_valid_hand(new_hand, level)
    
    # 解析牌型，获取所有可能的牌型
    new_possible_hands = parse_hand(new_hand, level)
    last_possible_hands = parse_hand(last_hand, level)
    
    # 新牌必须是有效牌型
    if not new_possible_hands:
        return False
    
    # 上一手牌也必须是有效牌型
    if not last_possible_hands:
        return True  # 如果上一手无效，新牌有效即可
    
    # 对于上一手牌，选择最强的牌型作为目标
    last_hand_info = max(last_possible_hands, key=get_hand_strength)
    
    # 尝试找到能击败上一手牌的最佳牌型
    best_new_hand = get_best_hand_for_comparison(new_possible_hands, last_hand_info.hand_type, level)
    
    if not best_new_hand:
        return False
    
    # 获取牌型强度
    new_strength = get_hand_strength(best_new_hand)
    last_strength = get_hand_strength(last_hand_info)
    
    # 定义特殊牌型（炸弹和同花顺）
    special_types = [HandType.BOMB_4, HandType.BOMB_5, HandType.BOMB_6, 
                     HandType.BOMB_7, HandType.BOMB_8, HandType.JOKER_BOMB, HandType.STRAIGHT_FLUSH]
    
    is_new_special = best_new_hand.hand_type in special_types
    is_last_special = last_hand_info.hand_type in special_types
    
    # 如果都是特殊牌型，按强度比较
    if is_new_special and is_last_special:
        if new_strength != last_strength:
            return new_strength > last_strength
        else:
            # 相同强度，比较具体值
            return _compare_same_hand_type(best_new_hand, last_hand_info, level)
    
    # 如果新牌是特殊牌型，上一手不是，新牌获胜
    elif is_new_special and not is_last_special:
        return True
    
    # 如果新牌不是特殊牌型，上一手是，新牌失败
    elif not is_new_special and is_last_special:
        return False
    
    # 都不是特殊牌型，必须是相同牌型才能比较
    else:
        if best_new_hand.hand_type != last_hand_info.hand_type:
            return False
        
        # 相同牌型，进一步比较
        return _compare_same_hand_type(best_new_hand, last_hand_info, level)


def can_beat_hand(new_hand: List[Card], last_hand: List[Card], level: int = 2) -> bool:
    """
    is_valid_play的别名，用于更清晰的函数命名
    
    Args:
        new_hand: 新出的牌列表
        last_hand: 上一手牌列表
        
    Returns:
        True如果新牌能大过上一手牌，否则False
    """
    return is_valid_play(new_hand, last_hand, level)


def get_playable_combinations(hand_cards: List[Card], last_hand: List[Card], level: int = 2) -> List[List[Card]]:
    """
    获取从手牌中能够大过上一手牌的所有可能组合
    
    这是一个辅助函数，可以用于AI决策或提示玩家可出的牌
    
    Args:
        hand_cards: 手牌列表
        last_hand: 上一手牌列表
        
    Returns:
        所有能够大过上一手牌的牌组合列表
    """
    from itertools import combinations
    
    playable_combinations = []
    
    # 如果上一手为空，返回所有有效牌型
    if not last_hand:
        # 这里只返回一些基本的单牌组合作为示例
        # 实际实现中可能需要更复杂的逻辑来生成所有可能的牌型
        for card in hand_cards:
            if is_valid_hand([card], level):
                playable_combinations.append([card])
        return playable_combinations
    
    # 尝试所有可能的牌组合
    max_combo_size = min(len(hand_cards), 13)  # 限制最大组合大小避免性能问题
    
    for combo_size in range(1, max_combo_size + 1):
        for combo in combinations(hand_cards, combo_size):
            combo_list = list(combo)
            if is_valid_play(combo_list, last_hand, level):
                playable_combinations.append(combo_list)
    
    return playable_combinations
