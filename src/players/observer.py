from src.players.player import Player


class Observer(Player):
    def _play_turn(self) -> None:
        self._client.turn()
