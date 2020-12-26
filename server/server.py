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
    BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
    
    # init socket to address family (host, port) and for TCP connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))

    # we want it to queue up as many as 5 connect requests ?
    s.listen(5)
   
    # TODO: add timeout 10 secs and manage players ir return false
    conn, addr = s.accept()
    print(f'Connection address:{addr}')
    data = conn.recv(BUFFER_SIZE)
    print(f'received data:{data.decode("utf-8")}')
    conn.send(data)  # echo
    time.sleep(5)
    conn.close()
    return True

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