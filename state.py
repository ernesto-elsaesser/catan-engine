from __future__ import annotations

import copy
import pickle
import random

from .board import *


class Player:

    def __init__(self, name: str):

        self.name = name

    def __repr__(self) -> str:

        return self.name


class Human(Player):

    def __init__(self, name: str, secret: str | None = None):

        super().__init__(name)

        self.secret = secret


class Bot(Player):

    def __init__(self, name: str, strategy: str = 'basic'):

        super().__init__(name)

        self.strategy = strategy


class Resources(dict):

    KEYS = ['R0', 'R1', 'R2', 'R3', 'R4']

    def __init__(self, amounts: dict[str, int]):

        super().__init__()

        for key in self.KEYS:
            self[key] = amounts.get(key, 0)

    def count(self) -> int:

        return sum(self.values())


class Choice:

    def __init__(self, action: str, *args):

        self.action = action
        self.action_params = args
        self.options: list[str] = []
        self.option_args: dict[str, list] = {}

    def add_option(self, option: str, args: list | None = None):

        self.options.append(option)
        if args is not None:
            self.option_args[option] = args

    def to_dict(self) -> dict:

        return {
            'action': self.action,
            'actionParams': self.action_params,
            'options': self.options,
            'optionArgs': self.option_args,
        }

    def __repr__(self) -> str:

        option_list = '|'.join(self.options)
        return f"{self.action} [{option_list}]"


class PlayerState:

    VICTORY_CARDS = ["Library", "Market", "Great Hall", "Chapel", "University"]

    PROGRESS_CARDS = [
        "Road Building", "Road Building",
        "Monopoly", "Monopoly",
        "Year of Plenty", "Year of Plenty",
        "Knight", "Knight", "Knight", "Knight", "Knight",
        "Knight", "Knight", "Knight", "Knight", "Knight",
        "Knight", "Knight", "Knight", "Knight",
    ]

    def __init__(self):

        self.resources = Resources({})
        self.draws: list[str] = []
        self.cards: list[str] = []
        self.roads: set[str] = set()
        self.camps: set[str] = set()
        self.forts: set[str] = set()

        self.choice: Choice | None = None

        self.road_length = 0
        self.army_size = 0

    def unlock_cards(self):

        self.cards += self.draws
        self.draws = []

    def discard_card(self, card: str):

        index = self.cards.index(card)
        del self.cards[index]

    def get_sites(self) -> set[str]:

        return self.camps | self.forts

    def get_conns(self) -> set[str]:

        sites = self.get_sites()

        conns: set[str] = set()
        for edge_id in self.roads:
            for node_id, next_edge_ids in CONNECTIONS[edge_id].items():
                if node_id in sites:
                    continue
                if any(e in self.roads for e in next_edge_ids):
                    conns.add(node_id)

        return conns


class GameState:

    def __init__(self, player_count: int, stack: list[str], robber: str):

        self.stack = stack
        self.robber = robber

        self.players = [PlayerState() for _ in range(player_count)]

        self.largest_army_index: int | None = None
        self.longest_road_index: int | None = None
        self.winner_index = -1
        self.round = -2
        self.current = 0

        self.actor: int | None = None
        self.action = 'game'
        self.option = 'start'
        self.argument: int | str | None = None
        self.deltas: list[Resources | None] = [None] * player_count

        choice = Choice('base1', "")
        node_ids = self.get_basecamp_options()
        choice.add_option('camp', node_ids)
        self.players[0].choice = choice

    def __repr__(self) -> str:

        actor = "-" if self.actor is None else self.actor
        return f"{actor}: {self.action}.{self.option}({self.argument})"

    def compute_points(self, player_index: int) -> int:

        player = self.players[player_index]

        points = len(player.camps)
        points += 2 * len(player.forts)
        for card in player.cards:
            if card in PlayerState.VICTORY_CARDS:
                points += 1
        if self.largest_army_index == player_index:
            points += 2
        if self.longest_road_index == player_index:
            points += 2

        return points

    def get_adjacent_owners(self, tile_or_edge_id: str) -> dict[str, int]:

        if tile_or_edge_id in TILE_NODES:
            adj_node_ids = TILE_NODES[tile_or_edge_id]
        else:
            adj_node_ids = EDGE_NODES[tile_or_edge_id]

        owners: dict[str, int] = {}
        for index, player in enumerate(self.players):
            for node_id in player.get_sites():
                if node_id in adj_node_ids:
                    owners[node_id] = index
        return owners

    def get_other_sites(self, player_index: int) -> set[str]:

        others = [p for i, p in enumerate(self.players) if i != player_index]
        return {n for p in others for n in p.get_sites()}

    def get_unlinked_neighbour_nodes(self, node_id: str) -> list[str]:

        all_roads = {e for p in self.players for e in p.roads}
        return [n for e, n in NEIGHBORS[node_id].items() if e not in all_roads]

    def get_basecamp_options(self) -> list[str]:

        all_sites = {n for p in self.players for n in p.get_sites()}

        options: list[str] = []

        for node_id, neighbors in NEIGHBORS.items():
            if node_id in all_sites:
                continue
            if any(n in all_sites for n in neighbors.values()):
                continue
            options.append(node_id)

        return options

    def get_baseroad_options(self, node_id: str) -> list[str]:

        return NODE_EDGES[node_id]

    def get_robber_options(self) -> list[str]:

        return [t for t in TILE_NODES if t != self.robber]

    def get_road_options(self, player_index: int) -> list[str]:

        all_roads = {e for p in self.players for e in p.roads}
        player_roads = self.players[player_index].roads
        other_sites = self.get_other_sites(player_index)

        options: list[str] = []

        for edge_id in player_roads:

            for node_id, edge_ids in CONNECTIONS[edge_id].items():
                neighbors = NEIGHBORS[node_id]
                for next_edge_id in edge_ids:
                    if next_edge_id in all_roads:
                        continue
                    if next_edge_id in options:
                        continue
                    if neighbors[next_edge_id] not in other_sites:
                        options.append(next_edge_id)

        return options

    def get_camp_options(self, player_index: int) -> list[str]:

        player_roads = set(self.players[player_index].roads)

        options: list[str] = []

        for node_id in self.get_basecamp_options():
            if any(e in player_roads for e in NODE_EDGES[node_id]):
                options.append(node_id)

        return options

    def get_fort_options(self, player_index: int) -> list[str]:

        return list(self.players[player_index].camps)

    def get_swap_rate(self, player_index: int, res_key: str) -> int:

        node_ids = self.players[player_index].get_sites()
        if any(n in SPECIFIC_HARBORS[res_key] for n in node_ids):
            return 2
        if any(n in GENERIC_HARBORS for n in node_ids):
            return 3
        return 4

    def update_road_length(self, player_index: int):

        player = self.players[player_index]

        player_roads = set(player.roads)
        other_sites = self.get_other_sites(player_index)

        road_length = get_max_road_length(player_roads, other_sites)

        player.road_length = road_length
        if road_length < 5:
            return

        if self.longest_road_index is None:
            self.longest_road_index = player_index
        else:
            current = self.players[self.longest_road_index]
            if road_length > current.road_length:
                self.longest_road_index = player_index

    def increment_army_size(self, player_index: int):

        player = self.players[player_index]

        army_size = player.army_size + 1
        player.army_size = army_size

        if army_size < 3:
            return

        if self.largest_army_index is None:
            self.largest_army_index = player_index
        else:
            current = self.players[self.largest_army_index]
            if army_size > current.army_size:
                self.largest_army_index = player_index

    def to_dict(self, target_index: int) -> dict:

        player_dicts: list[dict] = []

        for index, player in enumerate(self.players):

            player_dict: dict = {
                'resourceCount': player.resources.count(),
                'handCount': len(player.cards + player.draws),
                'roads': list(player.roads),
                'conns': list(player.get_conns()),
                'camps': list(player.camps),
                'forts': list(player.forts),
                'knightCount': player.army_size,
                'roadLength': player.road_length,
            }

            if index == target_index:

                swap_rates = Resources({})
                for res_key in Resources.KEYS:
                    swap_rates[res_key] = self.get_swap_rate(index, res_key)

                player_dict['resources'] = player.resources
                player_dict['swapRates'] = swap_rates
                player_dict['cards'] = player.cards
                player_dict['draws'] = player.draws
                player_dict['points'] = self.compute_points(index)
                if player.choice is not None:
                    player_dict['choice'] = player.choice.to_dict()

            player_dicts.append(player_dict)

        state_dict = {
            'round': self.round,
            'current': self.current,
            'robber': self.robber,
            'largest': self.largest_army_index,
            'longest': self.longest_road_index,
            'winner': self.winner_index,
            'actor': self.actor,
            'action': self.action,
            'option': self.option,
            'argument': self.argument,
            'players': player_dicts,
        }

        if target_index is not None:
            state_dict['delta'] = self.deltas[target_index]

        return state_dict


class Game:

    WIN_POINTS = 10

    SPIRAL_TILE_IDS = [
        'A3', 'A2', 'A1', 'B1', 'C1', 'D1', 'E1', 'E2', 'E3', 'D4',
        'C5', 'B4', 'B3', 'B2', 'C2', 'D2', 'D3', 'C4', 'C3',
    ]

    BEGINNER_YIELDS = [
        "R4", "R3", "R0", "R1", "R4", "R3", "R3", "R2", "R1", "R0",
        "R2", "R2", "R1", "R3", "R0", "R2", "R4", "R0", None,
    ]

    BEGINNER_ROLLS = [
        10, 2, 9, 10, 8, 5, 11, 6, 5, 8, 9, 12, 6, 4, 3, 4, 3, 11, None,
    ]

    VARIABLE_ROLLS: list[int | None] = [
        5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11
    ]

    def __init__(self, players: list[Player], randomize_map: bool = True):

        self.players = players

        if randomize_map:
            yields = copy.deepcopy(self.BEGINNER_YIELDS)
            rolls = copy.deepcopy(self.VARIABLE_ROLLS)
            random.shuffle(yields)
            desert_index = yields.index(None)
            rolls.insert(desert_index, None)
        else:
            yields = self.BEGINNER_YIELDS
            rolls = self.BEGINNER_ROLLS
            desert_index = len(yields) - 1

        self.yields = dict(zip(self.SPIRAL_TILE_IDS, yields))
        self.rolls = dict(zip(self.SPIRAL_TILE_IDS, rolls))
        robber = self.SPIRAL_TILE_IDS[desert_index]

        stack = PlayerState.VICTORY_CARDS + PlayerState.PROGRESS_CARDS
        random.shuffle(stack)

        initial_state = GameState(len(players), stack, robber)

        self.states = [initial_state]

    @staticmethod
    def load(path: str):

        with open(path, 'rb') as file:
            return pickle.load(file)

    def save(self, path: str):

        with open(path, 'wb') as file:
            pickle.dump(self, file)

    def get_player_index(self, secret: str) -> int | None:

        for index, player in enumerate(self.players):
            if isinstance(player, Human):
                if player.secret == secret:
                    return index
        return None

    def get_home_yields(self, node_id: str) -> Resources:

        yields = Resources({})
        for tile_id in NODE_TILES[node_id]:
            res_key = self.yields[tile_id]
            if res_key is not None:
                yields[res_key] += 1
        return yields

    def add_yields(self, state: GameState, roll: int):

        for tile_id in self.SPIRAL_TILE_IDS:
            if self.rolls[tile_id] != roll:
                continue
            if state.robber == tile_id:
                continue
            res_key = self.yields[tile_id]
            owners = state.get_adjacent_owners(tile_id)
            for node_id, index in owners.items():
                is_fort = node_id in state.players[index].forts
                resources = state.deltas[index]
                if resources is None:
                    resources = Resources({})
                    state.deltas[index] = resources
                resources[res_key] += 2 if is_fort else 1

    def to_dict(self, target_index: int) -> dict:

        return {
            'goal': self.WIN_POINTS,
            'players': [p.name for p in self.players],
            'yields': self.yields,
            'rolls': self.rolls,
            'states': [s.to_dict(target_index) for s in self.states[:-1]],
        }
