import argparse
import socket
import ipaddress
from utils.utils import (
    DATA_ENCODING,
    SOCKET_ADDRESS_FAMILY,
    SOCKET_KIND,
    ValidateFilePath,
    ValidateIP,
    ValidatePort,
    error_handler,
    receive_data,
    send_file,
)


class Client:
    def __init__(self, server_ip, server_port, file):
        self.socket: socket.socket
        self.file = file
        self.server_ip = server_ip
        self.server_port = server_port

    @error_handler("Unnable to create a socket.")
    def __create_socket(self):
        self.socket = socket.socket(SOCKET_ADDRESS_FAMILY, SOCKET_KIND, 0)

    @error_handler("Unnable to connect to a socket.")
    def __connect_socket(self):
        address: socket._Address = (
            str(ipaddress.ip_address(self.server_ip)),
            self.server_port,
        )
        self.socket.connect(address)

    @error_handler("Unnable to send data.")
    def __send_file(self):
        send_file(self.socket, self.file)

    @error_handler("Unnable to receive response from server.")
    def __receive_data(self):
        return receive_data(self.socket).decode(DATA_ENCODING)

    def start(self):
        self.__create_socket()
        try:
            self.__connect_socket()
            self.__send_file()
            response = self.__receive_data()
            print(response)
        except KeyboardInterrupt:
            print("Finishing due to KeyboardInterrupt")
        finally:
            self.socket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="\
            Connects to a socket at <host> on <port>,\
            then sends a file to server.\
            Server response is to be printed out on client."
    )
    parser.add_argument(
        "--host",
        required=True,
        action=ValidateIP,
        help="The server ip address.",
    )
    parser.add_argument(
        "--port",
        required=True,
        action=ValidatePort,
        help="The port number in which server is hosting the server application on.",
    )
    parser.add_argument(
        "--file",
        required=True,
        action=ValidateFilePath,
        help="A path to a file to be sent over to the server for analysis.",
    )

    args = parser.parse_args()

    client = Client(args.host, args.port, args.file)
    client.start()
