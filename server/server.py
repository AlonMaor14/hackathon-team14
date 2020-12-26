import socket
import time
import struct
from threading import Thread
from scapy.all import *

def send_offer(UDP_IP):
    UDP_PORT = 13117

    # prefix = 0xfeedbeef, type = 0x02, port = 2086
    packet = struct.pack('lhh', 0xfeedbeef, 0x2, 2086)

    # send offers for 10 seconds
    start_time = time.time()

    # init socket to address family (host, port) and for UDP connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while(time.time() - start_time < 10):
        sock.sendto(packet, (UDP_IP, UDP_PORT))
    
    sock.close()
    

def listen_for_clients(TCP_IP):
    TCP_PORT = 2086
    BUFFER_SIZE = 1024
    teams = {}
    
    # init socket to address family (host, port) and for TCP connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))

    # we want it to queue up as many as 5 connect requests ?
    s.listen(5)
   
    # TODO: add timeout 10 secs and manage players ir return false
    conn, addr = s.accept()
    print(f'Connection address:{addr}')
    data = conn.recv(BUFFER_SIZE)
    team_name = data.decode("utf-8")
    print(f'received data:{tean_name}')
    teams[team_name] = conn
    conn.send(b'Welcome to Keyboard Spamming Battle Royale.')

    # open threadpool
    time.sleep(5)
    conn.close()
    return True

def player_runnable(conn):
    BUFFER_SIZE = 1
    score = 0
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        score += len(data)
    return score


def main():

    # TODO: add option for eth2
    IP = get_if_addr("eth1")
    print(f'Server started, listening on IP address {IP}')

    while True:
        thread = Thread(target = send_offer, args=[IP])
        thread.start()
        game = listen_for_clients(IP)
        thread.join()
        if game:
            print('Game over, sending out offer requests...' )
        else:
            print('Looking for players...')


if __name__ == "__main__":
    main()