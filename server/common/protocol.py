import socket

from .utils import Bet, BET_SEPARATOR

HEADER_SIZE = 2
ACK_VALUE = 1
ACK_NUMBER_OF_BYTES = 1


class AgencySocket:
    def __init__(self, agency_id: str, sock: socket.socket):
        self._internal_socket = sock
        self._id = agency_id

    def get_peername(self):
        return self._internal_socket.getpeername()

    def recv_tickets(self) -> Bet:
        size_of_payload = self._internal_socket.recv(HEADER_SIZE)
        size_of_payload = int.from_bytes(size_of_payload, 'big')
        print(f'size of payload: {size_of_payload}')
        if size_of_payload == 0:
            return None

        payload = self._internal_socket.recv(size_of_payload).decode('utf-8')
        list_of_bets = []
        for bet_data in payload.split(BET_SEPARATOR):
            list_of_bets.append(Bet.from_str(self._id, bet_data))

        return list_of_bets

    def send_ack(self):
        self._internal_socket.send(ACK_VALUE.to_bytes(ACK_NUMBER_OF_BYTES, 'big'))

    def send(self, msg):
        self._internal_socket.send(msg)

    def close(self):
        self._internal_socket.close()