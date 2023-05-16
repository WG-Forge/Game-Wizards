from src.game import Game


def online_game(game_name: str, player_name: str, max_players: int = 1, num_turns: int = 45, is_full: bool = False,
                password: str = None, is_observer: bool = False) -> Game:

    game = Game(game_name, max_players, num_turns, is_full)

    # Add only local player
    game.add_local_player(player_name, password, is_observer)

    return game
