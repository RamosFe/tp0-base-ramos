import socket

from .utils import Bet

HEADER_SIZE = 2


class AgencySocket:
    def __init__(self, agency_id: str, sock: socket.socket):
        self._internal_socket = sock
        self._id = agency_id

    def get_peername(self):
        return self._internal_socket.getpeername()

    def recv_tickets(self) -> Bet:
        size_of_payload = self._internal_socket.recv(2)
        size_of_payload = int.from_bytes(size_of_payload, 'big')
        print(f'size of payload: {size_of_payload}')
        payload = self._internal_socket.recv(size_of_payload).decode('utf-8')
        return Bet.from_str(self._id, payload)

    def send(self, msg):
        self._internal_socket.send(msg)

    def close(self):
        self._internal_socket.close()