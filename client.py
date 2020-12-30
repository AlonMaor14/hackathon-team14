import socket
import time
import struct
import signal
from scapy.all import *

import colorize

def listen_to_offers():
    UDP_PORT = 13117
    MAGIC_COOKIE = 0xfeedbeef
    MSG_TYPE = 0x2

    print(colorize._colorize('Client started, listening for offer requests...'))

    # init socket to address family (host, port) and for UDP connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', UDP_PORT))
   
    while True:
        try:

            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

            # TODO: handle error
            msg = struct.unpack('lhh', data)
            print(f'received message: {msg} from {addr}')

            # validate offer
            if len(msg) == 3 and msg[0] == MAGIC_COOKIE and msg[1] == MSG_TYPE:
                print(f'Received offer from {addr[0]}, attempting to connect...')
                sock.close()

                # return tuple (server ip, server tcp port)
                return (addr[0], msg[2])

        except Exception as exc:

            # TODO: handle errors
            raise exc

def connect_to_server(addr):

    # init socket to address family (host, port) and for TCP connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
    
        client_socket.connect((addr[0], addr[1]))
        message = b'Catan settlers'
        client_socket.sendall(message)

        buffer = ''
        while True:
            data = client_socket.recv(1024)
            if data:
                buffer += data.decode()
                if '\n' in buffer:
                    print(buffer)
                    buffer = ''
            else:
                break

    finally:
        print('closing socket')
        client_socket.close()

def quit(sig, frame):
    print(colorize._colorize('\nGoodbye!', colorize.Colors.title))
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, quit)

    while True:
        addr = listen_to_offers()
        connect_to_server(addr)


if __name__ == "__main__":
    main()