# Catan Engine

This repository contains a set of Python modules that encode the complete "Settlers of Catan" game logic (following the official rules from Kosmos). The code is used in the browser-based [catan.one](https://catan.one/) game (free to play!).

The [bots.py](bots.py) module contains a class interface to implement custom bot strategies. The provided default strategy is rather simple, but can be surprisingly challenging to play against.

Usage example:

```python
from state import Game, Human, Bot
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
