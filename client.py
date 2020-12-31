import socket
import struct
import signal
import sys
import os
import select
import tty
import termios
from scapy.all import *

import colorize


def listen_to_offers():
    UDP_PORT = 13117
    MAGIC_COOKIE = 0xfeedbeef
    MSG_TYPE = 0x2

    print(colorize.colorize('Client started, listening for offer requests...'))

    # init socket to address family (host, port) and for UDP connection and broadcast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', UDP_PORT))

    got_offer = False
    while not got_offer:
        try:

            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes

            msg = struct.unpack('!IBH', data)

            # validate offer
            if len(msg) == 3 and msg[0] == MAGIC_COOKIE and msg[1] == MSG_TYPE:
                got_offer = True
                sock.close()

                # return tuple (server ip, server tcp port)
                return addr[0], msg[2]
            time.sleep(0.5)

        except Exception as exc:
            print(colorize.colorize(exc, colorize.Colors.error))


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
        print(colorize.colorize(exc, colorize.Colors.fatal))

    finally:

        client_socket.close()


def play(client_socket):
    thread = Thread(target=write_input, args=[client_socket])
    thread.start()
    buffer = ''
    while True:

        # check if we can read from server or write to it
        readable, _, _ = select([client_socket], [], [])
        if readable:
            data = client_socket.recv(1024)

            # EOF means server disconnected
            if not data:
                if buffer:
                    print(colorize.colorize(buffer, colorize.Colors.server))
                print(colorize.colorize('Disconnected from server', colorize.Colors.title))
                break
            buffer += data.decode()
            if '\n' in buffer:
                print(colorize.colorize(buffer, colorize.Colors.server))
                buffer = ''

        time.sleep(0.5)
    print(colorize.colorize('Press anything to continue', colorize.Colors.pink))
    thread.join()


def write_input(client_socket):
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setcbreak(sys.stdin.fileno())
        i = 0

        # run approx 10 sec
        while i < 50:
            if client_socket.fileno() == -1:
                break
            client_socket.sendall(sys.stdin.read(1).encode())
            i += 1
            time.sleep(0.2)
    except Exception:
        pass
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
    


def quit(sig, frame):
    os.system('reset')
    print(colorize.colorize('\nGoodbye! Enter q to quit:', colorize.Colors.title))
    sys.exit(0)


def main():
    global old_settings
    old_settings = None
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    while True:
        addr = listen_to_offers()
        connect_to_server(addr)


if __name__ == "__main__":
    main()
