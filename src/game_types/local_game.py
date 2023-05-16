from src.game import Game


def local_game(game_name: str, players: list[str], observers: list[str], max_players: int = 1, num_turns: int = 45,
               is_full: bool = False) -> Game:

    print(f"Game name: {game_name}\n"
          f"Players: {players}\n"
          f"Observers: {observers}\n"
          f"Max players: {max_players}\n"
          f"Num turns: {num_turns}\n"
          f"Is Full: {is_full}")
    game = Game(game_name, max_players, num_turns, is_full)

    # Add players to game
    for player_name in players:
        game.add_local_player(player_name, is_observer=False)

    # Add observers to game
    for observer_name in observers:
        game.add_local_player(observer_name, is_observer=True)

    return game
