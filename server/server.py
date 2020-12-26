import socket
import time
from threading import Thread

def send_offer():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 13117
    packet = bytearray.fromhex('feedbeef022086')
    print(f'Server started, listening on IP address {UDP_IP}')
    start_time = time.time()
    while(time.time() - start_time < 10):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(packet, (UDP_IP, UDP_PORT))

def main():
    thread = Thread(target = send_offer)
    thread.start()


    thread.join()


if __name__ == "__main__":
    main()