"""
Only to be run on the raspberry pi that is acting as the server for the Pico.

The pico sends data to the pi here and then the raspberry pi forwards it onto either
google sheets or a website.

"""
import socket
import time
import gspread
import os


HOST = "192.168.220.1"  # The pi server IP address that the pico connects to.
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
credentials_file = f"{os.path.dirname(os.path.abspath(__file__))}/autowater-360216-abde0af2cb6b.json"

class PostToSheets:
    """
    From data.pkl, post the data to google sheets, in chronological order
    """

    def __init__(self, sheet_name):
        self.SCOPE = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        sa = gspread.service_account(filename=credentials_file)
        sh = sa.open(sheet_name)
        self.sheet = sh.sheet1

    def append_row(self, data):
        """
        data = [date, moisture reading]
        :param data:
        :return:
        """
        self.sheet.append_row(data)


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
    sheet = PostToSheets('FernWater')
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                connect(s)
                time.sleep(5)
                print('Connection dropped, trying again')
        except ConnectionResetError as e:
            time.sleep(5)


