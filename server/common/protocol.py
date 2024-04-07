import socket

from .utils import Bet, BET_SEPARATOR

MAX_AGENCIES = 5

MSG_TYPE_SIZE = 1
HEADER_SIZE = 2

SEND_BET_MSG_TYPE = 1
END_SEND_BET_MSG_TYPE = 2
CLOSE_CONNECTION_MSG_TYPE = 3

ACK_VALUE = 1
ACK_NUMBER_OF_BYTES = 1


class AgencySocket:
    def __init__(self, sock: socket.socket):
        self._internal_socket = sock

    def send(self, msg: bytes):
        data_sent = 0
        while data_sent < len(msg):
            bytes_sent = self._internal_socket.send(msg)
            if bytes_sent == 0:
                raise OSError("connection was closed")

            data_sent += bytes_sent

    def recv(self, size: int) -> bytes:
        buffer = []
        data_read = 0

        while data_read < size:
            expected_size = size - data_read
            data = self._internal_socket.recv(expected_size)
            if data == b'':
                raise OSError("connection was closed")

            data_read += len(data)
            buffer.append(data)

        return b''.join(buffer)

    def get_peername(self):
        return self._internal_socket.getpeername()

    def recv_msg_type(self) -> int:
        msg_type = self.recv(MSG_TYPE_SIZE)
        return int.from_bytes(msg_type, 'big')

    def recv_tickets(self) -> Bet:
        size_of_payload = self.recv(HEADER_SIZE)
        size_of_payload = int.from_bytes(size_of_payload, 'big')
        if size_of_payload == 0:
            return None

        payload = self.recv(size_of_payload).decode('utf-8')
        list_of_bets = []
        for bet_data in payload.split(BET_SEPARATOR):
            list_of_bets.append(Bet.from_str(bet_data))

        return list_of_bets

    def send_ack(self):
        self.send(ACK_VALUE.to_bytes(ACK_NUMBER_OF_BYTES, 'big'))

    def close(self):
        self._internal_socket.close()
