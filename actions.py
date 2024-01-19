from __future__ import annotations

import copy
import random

from .state import Game, GameState, PlayerState, Choice, Resources


class Action:

    COSTS = {
        'road': Resources({'R0': -1, 'R1': -1}),
        'camp': Resources({'R0': -1, 'R1': -1, 'R2': -1, 'R3': -1}),
        'fort': Resources({'R2': -2, 'R4': -3}),
        'card': Resources({'R2': -1, 'R3': -1, 'R4': -1}),
    }

    def __init__(self, game: Game, player_index: int):

        self.game = game
        self.index = player_index
        self.player_count = len(game.players)

        self.state: GameState
        self.action_params: tuple

    def choose(self, option: str, argument: int | str | None = None):

        last_state = self.game.states[-1]
        player = last_state.players[self.index]
        choice = player.choice

        assert choice is not None, f"no choice for {self.index}"
        assert option in choice.options, option

        args = choice.option_args.get(option)
        if args is None:
            assert argument is None, (option, argument)
        else:
            assert argument in args, (option, argument)

        self.action_params = choice.action_params

        self.state = copy.deepcopy(last_state)
        self.state.actor = self.index
        self.state.action = choice.action
        self.state.option = option
        self.state.argument = argument
        self.state.deltas = [None] * self.player_count
        self.state.players[self.index].choice = None

        method = getattr(self, choice.action + '_' + option)
        if argument is None:
            method()
        else:
            method(argument)

        self.commit_state()

    def commit_state(self):

        for player, delta in zip(self.state.players, self.state.deltas):
            if delta is None:
                continue
            for res_key, amount in delta.items():
                player.resources[res_key] += amount

        final_state = copy.deepcopy(self.state)
        self.game.states.append(final_state)

        self.state.deltas = [None] * self.player_count

    def get_player(self) -> PlayerState:

        return self.state.players[self.index]

    def get_other_players(self) -> list[int]:

        return [i for i in range(self.player_count) if i != self.index]

    def get_choice(self) -> Choice:

        player = self.get_player()
        assert player.choice is not None, f"no choice for {self.index}"
        return player.choice

    def set_choice(self, choice: Choice, player_index: int | None = None):

        if player_index is None:
            player_index = self.index
        self.state.players[player_index].choice = choice

    def build_base_camp_choice(self, action: str) -> Choice:

        choice = Choice(action, "")
        node_ids = self.state.get_basecamp_options()
        choice.add_option('camp', node_ids)
        return choice

    def build_base_road_choice(self, action: str, node_id: str) -> Choice:

        choice = Choice(action, node_id)
        edge_ids = self.state.get_baseroad_options(node_id)
        choice.add_option('road', edge_ids)
        return choice

    def base1_camp(self, node_id: str):

        self.build_camp(node_id)
        choice = self.build_base_road_choice('base1', node_id)
        self.set_choice(choice)

    def base1_road(self, edge_id: str):

        self.build_road(edge_id)

        if self.state.current == self.player_count - 1:
            self.state.round += 1
            choice = self.build_base_camp_choice('base2')
        else:
            self.state.current += 1
            choice = self.build_base_camp_choice('base1')

        self.set_choice(choice, self.state.current)

    def base2_camp(self, node_id: str):

        self.build_camp(node_id)
        self.state.deltas[self.index] = self.game.get_home_yields(node_id)
        choice = self.build_base_road_choice('base2', node_id)
        self.set_choice(choice)

    def base2_road(self, edge_id: str):

        self.build_road(edge_id)

        if self.state.current == 0:
            self.state.round += 1
            self.start_next_turn()
            return

        self.state.current -= 1
        choice = self.build_base_camp_choice('base2')
        self.set_choice(choice, self.state.current)

    def start_next_turn(self):

        self.commit_state()

        self.index = self.state.current

        dice1 = random.randrange(6)
        dice2 = random.randrange(6)
        roll = 2 + dice1 + dice2

        self.state.actor = self.index
        self.state.action = 'roll'

        if roll == 7:
            self.state.option = 'robber'
            self.start_drops()
        else:
            self.state.option = 'yield'
            self.state.argument = roll
            self.game.add_yields(self.state, roll)
            self.continue_turn()

    def start_drops(self):

        for index, player in enumerate(self.state.players):
            res_count = player.resources.count()
            if res_count < 8:
                continue

            drop_count = res_count // 2
            choice = self.build_select_choice(index, 0, drop_count)
            self.set_choice(choice, index)

        self.end_drops()

    def build_select_choice(self,
                            player_index: int,
                            dropped: int,
                            drop_count: int,
                            *drops,
                            ) -> Choice:

        choice = Choice('select', dropped, drop_count, *drops)
        player = self.state.players[player_index]
        resources_left = Resources(player.resources)
        for res_key in drops:
            resources_left[res_key] -= 1
        res_keys = [r for r, n in resources_left.items() if n > 0]
        choice.add_option('res', res_keys)
        return choice

    def select_res(self, res_key: str):

        dropped, drop_count, *drops = self.action_params

        drops.append(res_key)
        dropped += 1

        if dropped == drop_count:
            choice = Choice('drop', drop_count, *drops)
            choice.add_option('commit', [dropped])  # for log entry
            choice.add_option('reset')
        else:
            choice = self.build_select_choice(
                self.index, dropped, drop_count, *drops)

        self.set_choice(choice)

    def drop_reset(self):

        drop_count, *_ = self.action_params
        choice = self.build_select_choice(self.index, 0, drop_count)
        self.set_choice(choice)

    def drop_commit(self, dropped):

        _, *drops = self.action_params

        delta = Resources({})
        for res_key in drops:
            delta[res_key] -= 1
        self.state.deltas[self.index] = delta

        self.end_drops()

    def end_drops(self):

        for player in self.state.players:
            if player.choice is not None:
                return

        choice = self.build_robber_choice()
        self.set_choice(choice, self.state.current)

    def build_robber_choice(self) -> Choice:

        choice = Choice('move')
        tile_ids = self.state.get_robber_options()
        choice.add_option('robber', tile_ids)
        return choice

    def move_robber(self, tile_id: str):

        self.state.robber = tile_id

        owners = self.state.get_adjacent_owners(tile_id)
        victim_indices: set[int] = set()
        for index in owners.values():
            if index == self.index:
                continue
            if self.state.players[index].resources.count() == 0:
                continue
            victim_indices.add(index)

        if len(victim_indices) == 0:
            self.continue_turn()
            return

        choice = Choice('rob')
        choice.add_option('player', sorted(victim_indices))
        choice.add_option('none')
        self.set_choice(choice)

    def rob_none(self):

        self.continue_turn()

    def rob_player(self, player_index: int):

        resources = self.state.players[player_index].resources
        rob_choices = []
        for res_key, amount in resources.items():
            rob_choices += [res_key] * amount
        rob_res_key = random.choice(rob_choices)
        self.state.deltas[self.index] = Resources({rob_res_key: 1})
        self.state.deltas[player_index] = Resources({rob_res_key: -1})
        self.continue_turn()

    def build_turn_choice(self) -> Choice:

        player = self.get_player()
        resources = Resources(player.resources)
        delta = self.state.deltas[self.index]
        if delta is not None:
            for res_key, amount in delta.items():
                resources[res_key] += amount

        choice = Choice('turn')

        points = self.state.compute_points(self.index)
        if points >= self.game.WIN_POINTS:
            choice.add_option('win')

        if self.can_afford(resources, 'road'):
            edge_ids = self.state.get_road_options(self.index)
            if len(edge_ids) > 0:
                choice.add_option('road', edge_ids)

        if self.can_afford(resources, 'camp') and len(player.camps) < 5:
            node_ids = self.state.get_camp_options(self.index)
            if len(node_ids) > 0:
                choice.add_option('camp', node_ids)

        if self.can_afford(resources, 'fort') and len(player.forts) < 4:
            node_ids = self.state.get_fort_options(self.index)
            if len(node_ids) > 0:
                choice.add_option('fort', node_ids)

        if self.can_afford(resources, 'card') and len(self.state.stack) > 0:
            choice.add_option('card')

        playable_cards = [
            c for c in player.cards if c not in PlayerState.VICTORY_CARDS]
        if len(playable_cards) > 0:
            choice.add_option('play', playable_cards)

        swap_res_keys: list[str] = []
        for res_key, amount in resources.items():
            rate = self.state.get_swap_rate(self.index, res_key)
            if amount >= rate:
                swap_res_keys.append(res_key)

        if len(swap_res_keys) > 0:
            choice.add_option('swap', swap_res_keys)

        choice.add_option('trade')
        choice.add_option('end')

        return choice

    def continue_turn(self, player_index: int | None = None):

        if player_index is not None:
            self.index = player_index

        choice = self.build_turn_choice()
        self.set_choice(choice)

    def turn_win(self):

        self.state.winner_index = self.index

    def turn_end(self):

        self.get_player().unlock_cards()

        if self.state.current == self.player_count - 1:
            self.state.current = 0
            self.state.round += 1
        else:
            self.state.current += 1

        self.start_next_turn()

    def turn_road(self, edge_id: str):

        self.build_road(edge_id)
        self.state.deltas[self.index] = self.COSTS['road']
        self.continue_turn()

    def turn_camp(self, node_id: str):

        self.build_camp(node_id)
        self.state.deltas[self.index] = self.COSTS['camp']
        self.continue_turn()

    def turn_fort(self, node_id: str):

        self.build_fort(node_id)
        self.state.deltas[self.index] = self.COSTS['fort']
        self.continue_turn()

    def turn_card(self):

        card = self.state.stack.pop()
        player = self.get_player()
        if card in PlayerState.VICTORY_CARDS:
            player.cards.append(card)
        else:
            player.draws.append(card)

        self.state.deltas[self.index] = self.COSTS['card']
        self.continue_turn()

    def turn_swap(self, res_key: str):

        choice = Choice('swap', res_key)
        other_res_keys = [r for r in Resources.KEYS if r != res_key]
        choice.add_option('res', other_res_keys)
        choice.add_option('cancel')
        self.set_choice(choice)

    def swap_cancel(self):

        self.continue_turn()

    def swap_res(self, res_key: str):

        give_res_key, = self.action_params

        rate = self.state.get_swap_rate(self.index, give_res_key)
        delta = Resources({give_res_key: -rate, res_key: 1})
        self.state.deltas[self.index] = delta
        self.continue_turn()

    def turn_play(self, card: str):

        player = self.get_player()
        player.discard_card(card)

        if card == "Road Building":
            choice = Choice('roads', 1)
            edge_ids = self.state.get_road_options(self.index)
            choice.add_option('road', edge_ids)
        elif card == "Monopoly":
            choice = Choice('monopoly')
            choice.add_option('res', Resources.KEYS)
        elif card == "Year of Plenty":
            choice = Choice('plenty', 1)
            choice.add_option('res', Resources.KEYS)
        elif card == "Knight":
            self.state.increment_army_size(self.index)
            choice = self.build_robber_choice()
        else:
            raise RuntimeError("invalid card")

        self.set_choice(choice)

    def turn_trade(self):

        choice = Choice('partner')
        other_indices = self.get_other_players()
        choice.add_option('player', other_indices)
        choice.add_option('cancel')
        self.set_choice(choice)

    def partner_cancel(self):

        self.continue_turn()

    def partner_player(self, player_index: int):

        choice = Choice('request', player_index)
        choice.add_option('res', Resources.KEYS)
        choice.add_option('cancel')
        self.set_choice(choice)

    def request_cancel(self):

        self.continue_turn()

    def request_res(self, res_key: str):

        choice = Choice('offer', *self.action_params, res_key)
        resources = self.get_player().resources
        res_keys = [r for r, a in resources.items() if r != res_key and a > 0]
        choice.add_option('res', res_keys)
        choice.add_option('nothing')
        choice.add_option('cancel')
        self.set_choice(choice)

    def offer_cancel(self):

        self.continue_turn()

    def offer_nothing(self):

        partner_index, request_key = self.action_params
        choice = Choice('donate', self.index, request_key)
        resources = self.state.players[partner_index].resources
        if resources[request_key] > 0:
            choice.add_option('grant')
        choice.add_option('decline')
        self.set_choice(choice, partner_index)

    def offer_res(self, res_key: str):

        choice = Choice('quote', *self.action_params, res_key)
        resources = self.get_player().resources
        amounts = [n + 1 for n in range(resources[res_key])]
        choice.add_option('amount', amounts)
        choice.add_option('cancel')
        self.set_choice(choice)

    def quote_cancel(self):

        self.continue_turn()

    def quote_amount(self, amount: str):

        partner_index, request_key, offer_key = self.action_params
        choice = Choice('trade', self.index, request_key, offer_key, amount)
        resources = self.state.players[partner_index].resources
        if resources[request_key] > 0:
            choice.add_option('accept')
        choice.add_option('decline')
        self.set_choice(choice, partner_index)

    def trade_decline(self):

        player_index, _, _, _ = self.action_params
        self.continue_turn(player_index)

    def trade_accept(self):

        player_index, request_key, offer_key, amount = self.action_params
        self.state.deltas[self.index] = Resources(
            {request_key: -1, offer_key: amount})
        self.state.deltas[player_index] = Resources(
            {request_key: 1, offer_key: -amount})
        self.continue_turn(player_index)

    def donate_decline(self):

        player_index, _ = self.action_params
        self.continue_turn(player_index)

    def donate_grant(self):

        player_index, request_key = self.action_params
        self.state.deltas[self.index] = Resources({request_key: -1})
        self.state.deltas[player_index] = Resources({request_key: 1})
        self.continue_turn(player_index)

    def monopoly_res(self, res_key: str):

        gains = Resources({})

        for index, player in enumerate(self.state.players):
            if index == self.index:
                continue
            count = player.resources[res_key]
            if count == 0:
                continue
            self.state.deltas[index] = Resources({res_key: -count})
            gains[res_key] += count

        if gains.count() > 0:
            self.state.deltas[self.index] = gains

        self.continue_turn()

    def roads_road(self, edge_id: str):

        num, = self.action_params

        self.build_road(edge_id)

        if num == 1:
            choice = Choice('roads', 2)
            edge_ids = self.state.get_road_options(self.index)
            choice.add_option('road', edge_ids)
            self.set_choice(choice)
        else:
            self.continue_turn()

    def plenty_res(self, res_key: str):

        num, = self.action_params

        self.state.deltas[self.index] = Resources({res_key: 1})

        if num == 1:
            choice = Choice('plenty', 2)
            choice.add_option('res', Resources.KEYS)
            self.set_choice(choice)
        else:
            self.continue_turn()

    def build_road(self, edge_id: str):

        self.get_player().roads.add(edge_id)
        self.state.update_road_length(self.index)

    def build_camp(self, node_id: str):

        self.get_player().camps.add(node_id)

    def build_fort(self, node_id: str):

        player = self.get_player()
        player.camps.remove(node_id)
        player.forts.add(node_id)

    def can_afford(self, resources: Resources, item: str) -> bool:

        costs = self.COSTS[item]
        for res_key, cost in costs.items():
            if resources[res_key] < -cost:
                return False
        return True
