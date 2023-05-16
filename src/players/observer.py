from src.players.player import Player


class Observer(Player):
    def _play_turn(self) -> None:
        if self._current_player == self.id:
            self._client.turn()

    # Disconnect observer
    def _disconnect(self) -> None:
        self._client.logout()
        self._client.disconnect()
