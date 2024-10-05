import argparse
import socket
from utils.utils import (
    DATA_ENCODING,
    MAX_WORKERS,
    SOCKET_ADDRESS_FAMILY,
    SOCKET_KIND,
    error_handler,
    receive_data,
    send_message,
    validatePort,
)
import ipaddress
import concurrent.futures

class Server:
    def __init__(self, port):
        self.socket: socket.socket
        self.port = port

    @error_handler("Unnable to create socket.")
    def __create_socket(self):
        self.socket = socket.socket(SOCKET_ADDRESS_FAMILY, SOCKET_KIND, 0)

    @error_handler("Unnable to bind socket.")
    def __bind_socket(self):
        address: socket._Address = (
            str(ipaddress.ip_address(socket.INADDR_ANY)),
            self.port,
        )
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(address)

    @error_handler("Unnable to listen to socket.")
    def __listen_socket(self):
        self.socket.listen()

    @error_handler("Unnable to accept client request.", exit_on_error=False)
    def __accept_connection(self):
        return self.socket.accept()

    @error_handler("Unnable to receive data from client.", exit_on_error=False)
    def __receive_data(self, connection):
        return receive_data(connection)

    @error_handler("Unnable to send response to client.", exit_on_error=False)
    def __send_message(self, connection, data):
        send_message(connection, data)

    @error_handler("Unnable to process request.", exit_on_error=False)
    def __count_alphabets(self, data):
        try:
            decoded = data.decode(DATA_ENCODING)
            upper = 0
            lower = 0
            for c in decoded:
                if c.islower():
                    lower += 1
                elif c.isupper():
                    upper += 1
            return "Lowercase: {lower}\nUppercase: {upper}\nTotal: {total}".format(
                lower=lower, upper=upper, total=upper + lower
            )
        except:
            print("There was an error while processing the data")
            return "There was an error while processing the file.\nPlease check if the file is decodable using utf-8.\n"

    def __handle_clien(self, connection):
        try:
            print('Receiving data...')
            data = self.__receive_data(connection)
            count = self.__count_alphabets(data)
            print("Sending response...")
            self.__send_message(connection, count)
        except BrokenPipeError:
            print("Client is no longer available.")
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        except Exception:
            print("There was an error in comminication with the client.")
        finally:
            print("Closing connection with a client...")
            connection.close()

    def start(self):
        self.__create_socket()

        try:
            self.__bind_socket()
            self.__listen_socket()
            print('listening on port {port}'.format(port=self.port))

            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                while True:
                    connection, _ = self.__accept_connection()
                    print('Accepted a client connection')
                    executor.submit(self.__handle_clien, connection)


        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            print('Closing socket')
            self.socket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="\
            Opens socket at <port> and listens for client requests.\
            The request should contain a file, which this program analyzes.\
            The alphabet count in the file will be sent back to the client."
    )
    parser.add_argument(
        "--port",
        required=True,
        type=validatePort,
        help="A port number to bind socket to.",
    )

    args = parser.parse_args()

    server = Server(args.port)
    server.start()
