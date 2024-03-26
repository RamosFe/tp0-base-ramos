import socket
import struct
from typing import List, Optional

from .utils import Bet, BET_SEPARATOR

MSG_TYPE_SIZE = 2
HEADER_SIZE = 2
ACK_VALUE = 1
ACK_NUMBER_OF_BYTES = 1

MSG_TYPE_BET_VALUE = 1
MSG_TYPE_END_VALUE = 2
MSG_TYPE_WINNERS_VALUE = 3

MAX_AGENCIES = 5


class Message:
    def __init__(self, msg_type, header, payload):
        self.msg_type = msg_type
        self.header = header
        self.payload = payload

    def to_bytes(self):
        msg_type_bytes = struct.pack('>H', self.msg_type)
        header_bytes = struct.pack('>H', self.header)
        return msg_type_bytes + header_bytes + self.payload


class AgencySocket:
    def __init__(self, agency_id: str, sock: socket.socket):
        self._internal_socket = sock
        self._id = agency_id

    def get_peername(self):
        return self._internal_socket.getpeername()

    def recv_tickets(self) -> Optional[List[Bet]]:
        msg_type = self._internal_socket.recv(HEADER_SIZE)
        msg_type = int.from_bytes(msg_type, 'big')

        if msg_type == MSG_TYPE_BET_VALUE:
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
        elif msg_type == MSG_TYPE_END_VALUE:
            return None
        else:
            raise ValueError(f'Invalid msg type: {msg_type}')

    def send_winners(self, winners: List[Bet]):
        list_of_documents = list(map(lambda x: x.document, winners))
        list_of_documents = ','.join(list_of_documents)
        documents_bytes = list_of_documents.encode('utf-8')

        message = Message(MSG_TYPE_WINNERS_VALUE, len(documents_bytes), documents_bytes)
        self._internal_socket.send(message.to_bytes())

    def send_ack(self):
        self._internal_socket.send(ACK_VALUE.to_bytes(ACK_NUMBER_OF_BYTES, 'big'))

    def send(self, msg):
        self._internal_socket.send(msg)

    def close(self):
        self._internal_socket.close()