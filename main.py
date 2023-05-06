import random

from src.game import Game


if __name__ == "__main__":
    rnd = random.randint(100000, 200000)
    game = Game(str(rnd), max_players=3, is_full=False)
    game.add_player("Zeljko")
    game.add_player("Observer1", is_observer=True)
    game.add_player("Olegas")
    game.add_player("Observer2", is_observer=True)
    game.add_player("Veljko")
    game.add_player("Observer3", is_observer=True)
    game.start_game()