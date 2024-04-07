import signal
import socket
import logging

from .utils import store_bets, load_bets, has_won
from .protocol import AgencySocket, SEND_BET_MSG_TYPE, \
    END_SEND_BET_MSG_TYPE, CLOSE_CONNECTION_MSG_TYPE, MAX_AGENCIES, REQUEST_WINNER_MSG_TYPE


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self._active_clients = []
        self._finished_agencies = 0
        self._winners = []

        self._running = True

        # Define signal handlers
        signal.signal(signal.SIGINT, self.__handle_signal)
        signal.signal(signal.SIGTERM, self.__handle_signal)

    def __handle_signal(self, signum, stack):
        logging.info(f'action: signal_handler | result: success | signal: {signum}')
        # Starts shutdown
        self.__shutdown()
        # Set running to false
        self._running = False
        return

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running:
            # Check if it is time to get the winners
            if self._finished_agencies == MAX_AGENCIES:
                logging.info("action: sorteo | result: success")
                bets = load_bets()
                self._winners = list(filter(lambda x: has_won(x), bets))

            try:
                client_sock = self.__accept_new_connection()
                self._active_clients.append(client_sock)
                self.__handle_client_connection(client_sock)
                self._active_clients.remove(client_sock)
            except OSError as err:
                # The server is shutting down
                if not self._running:
                    return

                # The server has an internal error, starts shutdown
                logging.error(f'action: new connection | result: fail | error: {err}')
                self.__shutdown()

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        agency_id = None

        try:
            while True:
                msg_type = client_sock.recv_msg_type()
                if msg_type == SEND_BET_MSG_TYPE:
                    # Receive the message from the client
                    bets = client_sock.recv_tickets()

                    # Stores bet
                    store_bets(bets)
                    for bet in bets:
                        if not agency_id:
                            agency_id = bet.agency
                        logging.info(f'action: apuesta_almacenada | result: success | '
                                     f'dni: {bet.document} | numero: {bet.number}')

                    # Handle properly the ACK
                    client_sock.send_ack()
                elif msg_type == END_SEND_BET_MSG_TYPE:
                    logging.info(f'action: fin de envio de apuestas | result: success | agency: {agency_id}')

                    # Add 1 to finished agencies
                    self._finished_agencies += 1
                elif msg_type == CLOSE_CONNECTION_MSG_TYPE:
                    logging.info(f'action: mensaje de fin de conexión | result: success | agency: {agency_id}')
                    break
                elif msg_type == REQUEST_WINNER_MSG_TYPE:
                    requested_agency = client_sock.recv_agency_id()
                    agency_id = requested_agency

                    if self._finished_agencies == MAX_AGENCIES:
                        logging.info(f'action: consulta ganadores | result: success | agency: {requested_agency}')
                        winners = list(filter(lambda x: x.agency == requested_agency, self._winners))
                        client_sock.send_winners(winners)
                    else:
                        logging.info(f'action: consulta ganadores | result: failed | agency: {requested_agency}'
                                     f' | msg: missing {MAX_AGENCIES - self._finished_agencies} agencies')
                        client_sock.send_unavailable_winners()

        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            logging.info(f'action: close client socket | result: success | agency: {agency_id}')
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
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')

        # Create Agency Socket
        agency_socket = AgencySocket(c)
        return agency_socket

    def __shutdown(self):
        # Closes the clients sockets
        for client in self._active_clients:
            addr = client.getpeername()
            logging.info(f'action: close client socket | result: success | ip: {addr[0]}')
            client.close()

        # Closes the server socket
        self._server_socket.close()
        logging.debug(f'action: close server socket | result: success')
