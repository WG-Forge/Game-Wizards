import random

from src.game import Game


if __name__ == "__main__":
    rnd = random.randint(100000, 200000)
    game = Game(str(rnd), max_players=3)
    game.add_player("Zeljko")
    game.add_player("Olegas")
    game.add_player("Veljko")
    game.start_game()
