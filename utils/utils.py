import argparse
import socket
import sys
import ipaddress
import os

SOCKET_ADDRESS_FAMILY = socket.AF_INET
SOCKET_KIND = socket.SOCK_STREAM
BUFFER_SIZE = 1024  # determines how much bytes to read at a time
HEADER_LENGTH = 4  # length of header in byte.
HEADER_BYTE_ORDER = "big"  # determines how header is formatted. "big" or "little"
DATA_ENCODING = "utf-8"  # determines the data encoding format.


def validateIp(value):
    try:
        ip = ipaddress.ip_address(str(value))
        if ip.version != 4:
            raise
        else:
            return str(value)
    except:
        raise argparse.ArgumentTypeError(
            "IP address has to be in a valid IPv4 format. Got {value}".format(
                value=value
            )
        )


def validatePort(value):
    try:
        port = int(value)
        if port >= 1 and port <= 65535:
            return port
        else:
            raise
    except:
        raise argparse.ArgumentTypeError(
            "Port number has to be an integer between 1 and 65535. Got {value}".format(
                value=value
            )
        )


def validateFilePath(value):
    try:
        file_path = str(value)
        if os.path.isfile(file_path):
            return file_path
        else:
            raise
    except:
        raise argparse.ArgumentTypeError(
            "File does not exist. Got {value}".format(value=value)
        )


def receive_data_in_chunks(connection, bytes_to_receive):
    data = []
    bytes_received = 0
    while bytes_received < bytes_to_receive:
        next_bytes_to_receive = min(BUFFER_SIZE, bytes_to_receive - bytes_received)
        chunk = connection.recv(next_bytes_to_receive)

        if not chunk:
            raise BrokenPipeError("Sender no longer available.")

        data.append(chunk)
        bytes_received += len(chunk)

    return b"".join(data)


def receive_data(connection):
    header = receive_data_in_chunks(connection, HEADER_LENGTH)
    payload_length = int.from_bytes(header, byteorder=HEADER_BYTE_ORDER)
    payload = receive_data_in_chunks(connection, payload_length)
    return payload


def send_message(connection, message):
    payload_length = len(message.encode(DATA_ENCODING))
    header = payload_length.to_bytes(HEADER_LENGTH, byteorder=HEADER_BYTE_ORDER)
    connection.sendall(header + message.encode(DATA_ENCODING))


def send_file(connection, file_path):
    payload_length = os.path.getsize(file_path)
    header = payload_length.to_bytes(HEADER_LENGTH, byteorder=HEADER_BYTE_ORDER)
    connection.sendall(header)

    with open(file_path, "rb") as file:
        while chunk := file.read(BUFFER_SIZE):
            connection.sendall(chunk)


def error_handler(error_message, exit_on_error=True):
    def decorate(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if exit_on_error:
                    sys.exit(str(e) + "\n" + error_message)
                else:
                    print("Error: " + error_message)
                    raise e

        return wrapper

    return decorate
