"""
Only to be run on the raspberry pi that is acting as the server for the Pico.

The pico sends data to the pi here and then the raspberry pi forwards it onto either
google sheets or a website.

"""
import datetime
import socket
import time
import gspread
import os


class PostToSheets:
    """
    From data.pkl, post the data to google sheets, in chronological order
    """

    def __init__(self, sheet_name):
        self.SCOPE = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        sa = gspread.service_account(filename=f"{os.path.dirname(os.path.abspath(__file__))}/autowater-360216-abde0af2cb6b.json")
        sh = sa.open(sheet_name)
        self.sheet = sh.sheet1

    def append_row(self, row):
        """
        data = [date, moisture reading]
        :param data:
        :return:
        """
        self.sheet.append_row(row)


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
            self.s.bind((self.host, self.port))
            self.s.listen()

    def get_data(self):
        clientsocket, addr = self.s.accept()
        with clientsocket:
            print(f"Connected by {addr}")
            data = clientsocket.recv(1024)
            print(f'{data.decode()}\n')
            clientsocket.send(bytes('Received', 'utf-8'))
            return data.decode()


if __name__ == '__main__':
    sheet = PostToSheets('FernWater')
    server = Server(host="192.168.220.1", port=65432)  # The pi server IP address that the pico connects to.

    while True:
        try:
            data = server.get_data()
            sheet.append_row([f'{datetime.datetime.now().strftime("%d/%m/%Y %H:00:00")}', data])
            time.sleep(5)
        except Exception as e:
            time.sleep(5)
            # Reboot the two classes, hopefully it'll fix whatever the error is.
            sheet = PostToSheets('FernWater')
            server = Server(host="192.168.220.1", port=65432)



