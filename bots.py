from __future__ import annotations
from typing import Callable, Any
import random

from .state import Game, Bot, Resources
from .actions import Action
from .board import *


def run_bots(game: Game):

    implementations = {'basic': BasicStrategy}

    changed = True
    
    while changed:

        changed = False

        for index, player in enumerate(game.players):

            if not isinstance(player, Bot):
                continue

            strategy_class = implementations[player.strategy]

            while True:
                strategy = strategy_class(game, index)
                if strategy.run():
                    changed = True
                else:
                    break


class Strategy:

    BASE_LEVELS = {'R0': 1, 'R1': 1, 'R2': 2, 'R3': 1, 'R4': 3}

    def __init__(self, game: Game, player_index: int):

        self.game = game
        self.index = player_index

        self.state = game.states[-1]
        self.player = self.state.players[self.index]

        self.options: dict[str, list] = {}

    def run(self) -> bool:

        choice = self.player.choice
        if choice is None:
            return False
        self.options.clear()
        for option in choice.options:
            self.options[option] = choice.option_args.get(option, [])
        getattr(self, choice.action)(*choice.action_params)
        return True

    def choose(self,
               option: str,
               rank: Callable[[Any], int] | None = None,
               min_rank: int | None = None,
               ) -> bool:

        action = Action(self.game, self.index)

        values = self.options[option]
        if len(values) == 0:
            action.choose(option)
            return True

        if rank is not None:
            ranking = {v: rank(v) for v in values}
            top_rank = max(ranking.values())
            if min_rank and top_rank < min_rank:
                return False
            values = [v for v, r in ranking.items() if r == top_rank]

        chosen_value = random.choice(values)
        action.choose(option, chosen_value)
        return True


class BasicStrategy(Strategy):

    def __init__(self, game: Game, player_index: int):

        super().__init__(game, player_index)

        self.camp_options = set(self.state.get_basecamp_options())

    def rank_camp_option(self, node_id: str) -> int:

        yield_set: set[str] = set()
        score = 0
        for tile_id in NODE_TILES[node_id]:
            res_key = self.game.yields[tile_id]
            if res_key is None:
                continue
            if res_key in yield_set:
                score += 1
            else:
                score += 2
                yield_set.add(res_key)
        if node_id in HARBORS:
            score += 1
        return score

    def rank_road_option(self, edge_id: str) -> int:

        unlocked_node_id = ""
        for node_id, con_edge_ids in CONNECTIONS[edge_id].items():
            if node_id in self.player.get_sites():
                continue
            if not any(e in self.player.roads for e in con_edge_ids):
                unlocked_node_id = node_id

        if unlocked_node_id == "":  # connects two existing roads
            return 0

        if unlocked_node_id in self.camp_options:
            return self.rank_camp_option(unlocked_node_id) + 2

        all_roads = {e for p in self.state.players for e in p.roads}
        score = 0
        for next_edge_id, next_node_id in NEIGHBORS[unlocked_node_id].items():
            if next_edge_id in all_roads:
                continue
            if next_node_id not in self.camp_options:
                continue
            camp_score = self.rank_camp_option(next_node_id)
            if camp_score > score:
                score = camp_score

        return score

    def rank_robber_option(self, tile_id: str) -> int:

        owners = self.state.get_adjacent_owners(tile_id)
        if self.index in owners.values():
            return 0
        if len(owners) == 0:
            return 1
        return 2

    def rank_lose_option(self, res_key: str) -> int:

        base_level = self.BASE_LEVELS[res_key]
        amount = self.player.resources[res_key]
        return amount - base_level

    def rank_gain_option(self, res_key: str) -> int:

        return -self.player.resources[res_key]

    def rank_swap_option(self, res_key: str) -> int:

        swap_rate = self.state.get_swap_rate(self.index, res_key)
        excess = self.player.resources[res_key] - swap_rate
        base = self.BASE_LEVELS[res_key]
        return excess - base

    def base1(self, node_id: str):

        if node_id == "":
            self.choose('camp', self.rank_camp_option)
        else:
            self.choose('road', self.rank_road_option)

    def base2(self, item: str):

        self.base1(item)

    def select(self, dropped: int, drop_count: int, *drops):

        self.choose('res', self.rank_lose_option)

    def drop(self, drop_count, *drops):

        self.choose('commit')

    def move(self):

        self.choose('robber', self.rank_robber_option)

    def rob(self):

        self.choose('player', self.state.compute_points)

    def turn(self):

        if 'win' in self.options:
            self.choose('win')
            return

        if 'play' in self.options:
            self.choose('play')
            return

        if 'fort' in self.options:
            self.choose('fort', self.rank_camp_option)
            return

        if 'camp' in self.options:
            self.choose('camp', self.rank_camp_option)
            return

        if 'road' in self.options:
            camp_options = self.state.get_camp_options(self.index)
            site_count = len(camp_options)
            res0 = self.player.resources["R0"]
            res1 = self.player.resources["R1"]
            has_multi = res0 > 1 and res1 > 1
            if site_count == 0 or (has_multi and site_count < 2):
                self.choose('road', self.rank_road_option)
                return

        if 'card' in self.options:
            points = self.state.compute_points(self.index)
            res2 = self.player.resources["R2"]
            res3 = self.player.resources["R3"]
            has_multi = res2 > 1 and res3 > 1
            if points > 5 or (has_multi and points > 3):
                self.choose('card')
                return

        if 'swap' in self.options:
            if self.choose('swap', self.rank_swap_option, min_rank=1):
                return

        if self.player.resources.count() > 6:
            last_trade_round = 0
            for state in reversed(self.game.states):
                if state.actor == self.index and state.option == 'trade':
                    last_trade_round = state.round
                    break
            if last_trade_round != self.state.round:
                self.choose('trade')
                return

        self.choose('end')

    def swap(self, give_res_key: str):

        resources = self.player.resources
        max_progress = -1
        target_costs = Resources({})
        for item in ['fort', 'camp', 'road', 'card']:
            progress = 0
            costs = Action.COSTS[item]
            for res_key, amount in costs.items():
                progress += min(resources[res_key], amount)  # type: ignore
            if progress > max_progress:
                target_costs = costs

        def rank(res_key: str):
            return -(target_costs[res_key] + resources[res_key])

        self.choose('res', rank)

    def monopoly(self):

        self.choose('res', self.rank_gain_option)

    def roads(self, num: int):

        self.choose('road', self.rank_road_option)

    def plenty(self, num: int):

        self.choose('res', self.rank_gain_option)

    def trade(self, player_index: int, request_key: str, offer_key: str, amount: int):

        if 'accept' not in self.options:
            self.choose('decline')
        elif amount < 2:
            self.choose('decline')
        elif self.player.resources[request_key] <= self.BASE_LEVELS[request_key]:
            self.choose('decline')
        else:
            self.choose('accept')

    def donate(self, player_index: int, request_key: str):

        self.choose('decline')
