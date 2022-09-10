"""
Only to be run on the raspberry pi that is acting as the server for the Pico.

The pico sends data to the pi here and then the raspberry pi forwards it onto either
google sheets or a website.

"""
import socket
import time

HOST = "192.168.220.1"  # The pi server IP address that the pico connects to.
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def connect(s):
    clientsocket, addr = s.accept()
    with clientsocket:
        print(f"Connected by {addr}")
        while True:
            data = clientsocket.recv(1024)
            print(f'{data}\n')
            clientsocket.send(bytes('Received', 'utf-8'))
            if not data:  # Nothing is being received/connection lost.
                break  # Break and return nothing. __name__ __main__ will try again.


if __name__ == '__main__':
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            connect(s)
            time.sleep(5)
            print('Connection dropped, trying again')

