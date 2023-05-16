import socket
import json

from src.constants import Action, Result, SERVER_HOST, SERVER_PORT, MAX_CHUNK_SIZE


class ServerConnection:
    def __init__(self) -> None:
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((SERVER_HOST, SERVER_PORT))

    def login(self, name: str, password: str = None, game: str = None, num_turns: int = None,
              num_players: int = None, is_observer: bool = None, is_full: bool = None) -> dict:

        data: dict = {
            "name": name,
            "password": password,
            "game": game,
            "num_turns": num_turns,
            "num_players": num_players,
            "is_observer": is_observer,
            "is_full": is_full
        }

        data = {key: value for (key, value) in data.items() if value is not None}

        return self.__send_data(Action.LOGIN, data)

    def logout(self) -> None:
        self.__send_data(Action.LOGOUT)

    def map(self) -> dict:
        return self.__send_data(Action.MAP)

    def game_state(self) -> dict:
        return self.__send_data(Action.GAME_STATE)

    def game_actions(self) -> dict:
        return self.__send_data(Action.GAME_ACTIONS)

    def turn(self) -> int:
        try:
            self.__send_data(Action.TURN)
        except TimeoutError:
            return -1
        else:
            return 0

    def chat(self, message: str) -> None:
        self.__send_data(Action.CHAT, {"message": message})

    def move(self, data: dict) -> None:
        self.__send_data(Action.MOVE, data)

    def shoot(self, data: dict) -> None:
        self.__send_data(Action.SHOOT, data)

    def disconnect(self) -> None:
        self.__socket.close()

    @staticmethod
    def __parse_response(response_msg: bytes) -> [Result, dict]:
        result_code = int.from_bytes(response_msg[:4], 'little')
        data_len = int.from_bytes(response_msg[4:8], 'little')

        if data_len == 0:
            return result_code, None

        data_json = response_msg[8:8 + data_len].decode('utf-8')
        response_data = json.loads(data_json)
        return result_code, response_data

    @staticmethod
    def __encode_message(data: dict) -> bytes:
        data_json = json.dumps(data).encode('utf-8')
        data_len = len(data_json)
        return data_len.to_bytes(4, 'little') + data_json

    def __send_data(self, action: Action, data: dict = None) -> dict:
        if data is not None:
            msg = action.value.to_bytes(4, "little") + self.__encode_message(data)
        else:
            msg = action.value.to_bytes(8, "little")

        self.__socket.sendall(msg)

        response_code, response_data = self.__parse_response(self.receive_message())

        if response_code == Result.TIMEOUT:
            data: dict = response_data
            raise TimeoutError(f"Error type {response_code}: {data['error_message']}")
        elif response_code != Result.OKEY:
            data: dict = response_data
            raise ConnectionError(f"Error type {response_code}: {data['error_message']}")
        elif response_data is not None and len(response_data) > 0:
            return response_data

        return {}

    def receive_message(self) -> bytes:
        # First, receive the action code and message length
        header = self.__socket.recv(8)
        if not header:
            # If the received header is empty, the connection was closed
            raise ConnectionError("Connection closed by server")

        data_len = int.from_bytes(header[4:], 'little')

        # Receive the rest of the message in chunks
        chunks = []
        bytes_received = 0
        while bytes_received < data_len:
            chunk = self.__socket.recv(min(MAX_CHUNK_SIZE, data_len - bytes_received))
            if not chunk:
                # If the received chunk is empty, the connection was closed
                raise ConnectionError("Connection closed by server")
            chunks.append(chunk)
            bytes_received += len(chunk)
        return header + b"".join(chunks)
