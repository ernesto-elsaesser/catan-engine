# Catan Engine

This repository contains a set of Python modules that encode the "Settlers of Catan" game logic (according to the official rules from Kosmos).

The [bots.py](bots.py) module contains a base class for bot strategy and a very basic implementation. It is designed to be easliy extensible to implement custom bot stragtegies.

Requires Python 3.7 or later.

Usage example:

```python
from state import Game, Player, Human, Bot
from actions import Action
from bots import run_bots

# initialize new game

players = [Human("Amy"), Bot("Bill"), Bot("Cindy")]
game = Game(players)

# print game state

current_state = game.states[-1]
print(current_state)
print(current_state.players[0].resources)
print(current_state.players[0].choice)

# make a move

action = Action(game, player_index=0)
action.choose("camp", "C2B")  # place first camp on node C2B
action.choose("road", "C2b")  # place first road on edge C2b

# let bots move

run_bots(game)

# saving and loading to disk

save_path = "/home/ernesto/catan/game1.pickle"
game.save(save_path)
loaded_game = Game.load(save_path)

# game state serialization (e.g. for conversion into JSON)

game_dict = game.to_dict(target_index=0)
state_dict = game.states[-1].to_dict(target_index=0)
```
