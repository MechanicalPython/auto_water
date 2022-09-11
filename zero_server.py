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


if __name__ == '__main__':
    sheet = PostToSheets('FernWater')
    last_post = time.time()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("192.168.220.1", 65432))
        s.listen()
        client, addr = s.accept()
        with client:
            client.send(bytes('Received', 'utf-8'))  # If pico is handing for a response, this should kick it.
            while True:
                try:
                    data = client.recv(1024)
                    print(data.decode())
                    client.send(bytes('Received', 'utf-8'))
                    if time.time() - last_post > (10*60):  # Receive data but only post results every 10 minutes.
                        sheet.append_row([f'{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:00")}', float(data.decode())])
                        last_post = time.time()
                    else:
                        pass
                except ConnectionResetError:
                    time.sleep(1)
