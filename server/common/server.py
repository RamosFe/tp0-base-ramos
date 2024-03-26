import signal
import socket
import logging
import sys

from .utils import Bet, store_bets
from .protocol import AgencySocket


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._active_clients = []
        self._agencies_id = {}
        self._id_counter = 0

        # Define signal handlers
        signal.signal(signal.SIGINT, self.__handle_signal)
        signal.signal(signal.SIGTERM, self.__handle_signal)

    def __handle_signal(self, signum, stack):
        logging.info(
            f'action: signal_handler | result: success | signal: {signum}'
        )
        # Closes the server socket
        self._server_socket.close()
        logging.debug(f'action: close server socket | result: success')
        # Closes the clients sockets
        for client in self._active_clients:
            addr = client.getpeername()
            logging.info(f'action: close client socket | result: success | ip: {addr[0]}')
            client.close()

        sys.exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while True:
            client_sock = self.__accept_new_connection()
            self._active_clients.append(client_sock)
            self.__handle_client_connection(client_sock)
            self._active_clients.remove(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            # Receive the message from the client
            bet = client_sock.recv_tickets()

            addr = client_sock.get_peername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {vars(bet)}')

            # Stores bet
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')

            # Handle properly the ACK
            client_sock.send_ack()
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        # Adds unique id to address
        if not addr[0] in self._agencies_id:
            self._id_counter += 1
            self._agencies_id[addr[0]] = self._id_counter
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')

        # Create Agency Socket
        agency_socket = AgencySocket(str(self._agencies_id[addr[0]]), c)
        return agency_socket
