import socket
import time
import struct
from threading import Thread
import signal
import sys
from scapy.all import *
from concurrent.futures import ThreadPoolExecutor


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
    

def play(TCP_IP):
    TCP_PORT = 2086
    BUFFER_SIZE = 1024
    teams = {}
    group1 = []
    group2 = []
    
    # init socket to address family (host, port) and for TCP connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))

    # make socket a server's one, 5 is only advisory for num of connections
    s.listen(5)

    game_over_msg = 'Some wierd stuff happend\n'
    try:
        connect_to_clients(s, teams, group1, group2)

        # if no teams don't start game
        if bool(teams) :
            return False
        
        for conn in teams.values():
            conn.send(b'Group 1 :\n==\n{0}\n'.format('\n'.join(group1)))
            conn.send(b'Group 2 :\n==\n{0}\n'.format('\n'.join(group2)))

        # shutdown automatically
        with ThreadPoolExecutor() as executor:
            scores_futures = []
            for team, conn in teams.items():
                scores_futures.append(executor.submit(player_runnable, args=[team, conn]))
                conn.send(b'START SPAMMING!!!!!\n')

            # Main thread computes results
            g1_res = 0
            g2_res = 0
            for res in concurrent.futures.as_completed(scores_futures):
                res = res.result()
                if res[0] in group1:
                    g1_res += res[1]
                else: 
                    g2_res += res[1]

        game_over_msg = f'Game Over!\n Group 1 score: {g1_res}\n Group 2 score: {g2_res}\n'
        if g1_res > g2_res:
            game_over_msg += 'Winners : Group 1 !\n'
        elif g2_res > g1_res:
            game_over_msg += 'Winners : Group 2 !\n'
        else:
            game_over_msg += 'Tie !\n'

        
    finally:
        for conn in teams.values():
            conn.send(struct.pack('s', game_over_msg.encode()))
            conn.close()
        print('closing socket')
        s.close()
    
    return True

def player_runnable(team, conn):
    BUFFER_SIZE = 1
    score = 0
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        score += len(data)
    return (team, score)

def connect_to_clients(socket, teams, group1, group2):
    BUFFER_SIZE = 1024

    # start game after 10 seconds
    start_time = time.time()
    group_index = 1
    if time.time() - start_time < 10:
        conn, addr = socket.accept()
        print(f'Connection address:{addr}')

        data = conn.recv(BUFFER_SIZE)
        team_name = data.decode("utf-8")
        print(f'received data:{team_name}')

        teams[team_name] = conn

        # assign team to a group
        if group_index % 2 == 0:
            group2.append(team_name)
        else:
            group1.append(team_name)
        conn.send(b'Welcome to Keyboard Spamming Battle Royale.')
        group_index += 1

def quit(sig, frame):
    print('Goosbye!')
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, quit)

    # TODO: add option for eth2
    IP = get_if_addr("eth1")
    print(f'Server started, listening on IP address {IP}')

    while True:
        thread = Thread(target = send_offer, args=[IP])
        thread.start()
        game = play(IP)
        thread.join()
        if game:
            print('Game over, sending out offer requests...' )
        else:
            print('Looking for players...')


if __name__ == "__main__":
    main()