import multiprocessing
import signal
import socket
import logging
import sys

from .utils import Bet, store_bets, load_bets, has_won
from .protocol import AgencySocket, MAX_AGENCIES


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        # Define a process manager
        manager = multiprocessing.Manager()

        # Define locks
        self._locks = {
            'store_bets': manager.Lock(),
            'finished_agencies': manager.Lock()
        }

        # Define shared state
        self._shared_data = manager.dict({
            'finished_agencies': 0
        })

        self._active_clients = []
        self._agencies_id = {}
        self._id_counter = 0

        # List of processes
        self._processes = []

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
        while True:
            client_sock = self.__accept_new_connection()

            # End server if already has a winner
            if self._shared_data['finished_agencies'] == MAX_AGENCIES:
                client_sock.close()
                break

            self._active_clients.append(client_sock)

            # Creates new process for the client
            client_process = multiprocessing.Process(
                target=self.__handle_client_connection, args=(client_sock, self._locks)
            )
            client_process.start()
            self._processes.append(client_process)

    def __handle_winners(self):
        logging.info("action: sorteo | result: success")
        bets = load_bets()
        winners = list(filter(lambda x: has_won(x), bets))
        for client in self._active_clients:
            client.send_winners(winners)
            client.close()

    def __handle_client_connection(self, client_sock, locks):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                # Receive the message from the client
                bets = client_sock.recv_tickets()
                if bets is None:
                    break

                # Stores bet
                with locks['store_bets']:
                    store_bets(bets)

                for bet in bets:
                    logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')

                # Handle properly the ACK
                client_sock.send_ack()

            # Add 1 to finished agencies
            with locks['finished_agencies']:
                self._shared_data['finished_agencies'] += 1
                print(f"Valor de finished {self._shared_data['finished_agencies']}")

                if self._shared_data['finished_agencies'] == MAX_AGENCIES:
                    self.__handle_winners()
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
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
