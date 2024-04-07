import socket
import struct
from typing import List

from .utils import Bet, BET_SEPARATOR

MAX_AGENCIES = 5

MSG_TYPE_SIZE = 1
HEADER_SIZE = 2

SEND_BET_MSG_TYPE = 1
END_SEND_BET_MSG_TYPE = 2
CLOSE_CONNECTION_MSG_TYPE = 3
REQUEST_WINNER_MSG_TYPE = 4
UNAVAILABLE_WINNER_MSG_TYPE = 5
AVAILABLE_WINNER_MSG_TYPE = 6

ACK_VALUE = 1
ACK_NUMBER_OF_BYTES = 1


class PayloadMessage:
    def __init__(self, msg_type, header, payload):
        self.msg_type = msg_type
        self.header = header
        self.payload = payload

    def to_bytes(self):
        msg_type_bytes = struct.pack('>B', self.msg_type)
        header_bytes = struct.pack('>H', self.header)
        return msg_type_bytes + header_bytes + self.payload

class SignalMessage:
    def __init__(self, msg_type):
        self.msg_type = msg_type

    def to_bytes(self):
        msg_type_bytes = struct.pack('>B', self.msg_type)
        return msg_type_bytes


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

    def send_winners(self, winners: List[Bet]):
        list_of_documents = list(map(lambda x: x.document, winners))
        list_of_documents = ','.join(list_of_documents)
        documents_bytes = list_of_documents.encode('utf-8')

        message = PayloadMessage(AVAILABLE_WINNER_MSG_TYPE, len(documents_bytes), documents_bytes)
        self.send(message.to_bytes())

    def send_unavailable_winners(self):
        message = SignalMessage(UNAVAILABLE_WINNER_MSG_TYPE)
        self.send(message.to_bytes())

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

    def recv_agency_id(self):
        size_of_payload = self.recv(HEADER_SIZE)
        size_of_payload = int.from_bytes(size_of_payload, 'big')

        payload = self.recv(size_of_payload)
        agency_id = int.from_bytes(payload, 'big')
        return agency_id

    def send_ack(self):
        self.send(ACK_VALUE.to_bytes(ACK_NUMBER_OF_BYTES, 'big'))

    def close(self):
        self._internal_socket.close()
