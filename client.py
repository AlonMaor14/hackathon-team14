import socket
import time
import struct
import signal
import sys
import select
import tty
import termios
from scapy.all import *

import colorize

def listen_to_offers():
    UDP_PORT = 13119
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
                sock.close()

                # return tuple (server ip, server tcp port)
                return (addr[0], msg[2])

        except Exception as exc:
            print(colorize._colorize(exc, colorize.Colors.error))

def connect_to_server(addr):

    # init socket to address family (host, port) and for TCP connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f'Received offer from {addr[0]}, attempting to connect...')
        client_socket.connect((addr[0], addr[1]))
        client_socket.setblocking(False)

        team_name = b'Catan settlers\n'
        client_socket.sendall(team_name)
        play(client_socket)

    except Exception as exc:
        print(colorize._colorize(exc, colorize.Colors.fatal))

    finally:

        print('closing socket')
        client_socket.close()

def play(client_socket):
    buffer = ''
    while True:

        # check if we can read from server or write to it
        readable, _, _ = select([client_socket], [], [])
        if readable:
            data = client_socket.recv(1024)

            # EOF means server disconnected
            if not data:
                if buffer:
                    print(colorize._colorize(buffer, colorize.Colors.server))
                print(colorize._colorize('Disconnected from server', colorize.Colors.title))
                break
            buffer += data.decode()
            if '\n' in buffer:
                print(colorize._colorize(buffer, colorize.Colors.server))
                buffer = ''
        else:
            read_stdin(client_socket)
            

def read_stdin(client_socket):
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        if select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            client_socket.send(sys.stdin.read(1).encode())

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
def quit(sig, frame):
    print(colorize._colorize('\nGoodbye!', colorize.Colors.title))
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    while True:
        addr = listen_to_offers()
        connect_to_server(addr)


if __name__ == "__main__":
    main()
