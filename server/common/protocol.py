import socket

from .utils import Bet

HEADER_SIZE = 2
ACK_VALUE = 1
ACK_NUMBER_OF_BYTES = 1


class AgencySocket:
    def __init__(self, agency_id: str, sock: socket.socket):
        self._internal_socket = sock
        self._id = agency_id

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

    def recv_tickets(self) -> Bet:
        size_of_payload = self.recv(HEADER_SIZE)
        size_of_payload = int.from_bytes(size_of_payload, 'big')
        payload = self.recv(size_of_payload).decode('utf-8')
        return Bet.from_str(self._id, payload)

    def send_ack(self):
        self.send(ACK_VALUE.to_bytes(ACK_NUMBER_OF_BYTES, 'big'))

    def close(self):
        self._internal_socket.close()
