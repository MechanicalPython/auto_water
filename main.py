"""
Now with new Pico W code!
Pico w version rp2-pico-w-20220825-unstable-v1.19.1-318-g923375380.uf2 appears to work.

Capacitive sensor measurement profile. From dry to water, it takes 40 seconds to slowly drop to 100% wet
and then wet to dry takes 10 seconds in a natural log increase pattern.

0% wet = 24000
100% wet = 59000

## Workflow
1. Read moisture sensor - 1 per second.
2. Pass it to google sheet via pi zero server. - every 10 minutes
3. Water plant if needed.
4. Change lights.

"""
from imports import secrets
import network
import socket
import machine
import neopixel
import time
import requests
from machine import Pin
import math


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    while wlan.isconnected() is False:
        time.sleep(1)
    print(f'Connected to {secrets.SSID}')


class AutoWater:
    """
    The min and max readings for the sensor changes from 50,000 to 30-20000
    """

    def __init__(self, vcc_pin=22, adc_pin=26, neo_pin=1):
        machine.Pin(vcc_pin, Pin.OUT).on()  # Turn moisture sensor power on.
        self.adc_pin = machine.Pin(adc_pin)  # Pin 31/GPIO 26/ADC 0.
        self.sensor = machine.ADC(self.adc_pin)
        self.pump = Pin(18, Pin.OUT)  # Relay GPIO pin is pin 18.
        self.np = neopixel.NeoPixel(Pin(neo_pin), 12)
        self.max = 54000  # 0% wet.
        self.min = 21000  # 100% wet
        # All colours set to low brightness.
        self.red = (1, 0, 0)
        self.green = (0, 1, 0)
        self.blue = (0, 0, 1)
        self.off = (0, 0, 0)

    def get_moisture(self, number_of_readings):
        # New capacitive sensor can be constantly powered so no need to turn the sensor on and off.
        total = 0
        for x in range(0, number_of_readings):
            total += self.sensor.read_u16()
        value = total / number_of_readings
        return value

    def convert_raw_to_perc(self, raw):
        """
        Returns % wet. Max = 100% wet, min = 0% wet.
        Can (in theory) be +- 0 to 100%
        :param raw:
        :return:
        """
        # wet = 21600, dry = 59000
        percentage = (raw - self.min) / (self.max - self.min)  # Gives it as if 100% is dry.
        invert = ((percentage - 1) * -1) * 100  # to make 100% = wet.
        return round(invert, 2)

    def set_lights(self, value):
        """
        10 lights for watered status. 100-50 = 10 to 1 green light. 49 - 0 = 1 to 10 red lights.
        Light 11 is blue when there is a wifi connection, and off when no connection.
        Light 12 is blue when there is connection to the raspberry pi 0.
        :param: value = % of wet.
        :return:
        """
        if value >= 50:
            colour = self.green
            number_of_lights_on = math.ceil((value - 50) / 5)
            if number_of_lights_on > 10:
                number_of_lights_on = 10
        else:
            colour = self.red
            number_of_lights_on = (math.ceil(value / 5) - 10) * 1
            if number_of_lights_on > 10:
                number_of_lights_on = 10

        self.lights_off()  # Reset the lights.

        for x in range(1, int(number_of_lights_on)):  # Light leds 1 to 10.
            self.np[x] = colour
        self.np.write()

    def lights_off(self):
        for x in range(0, 12):
            self.np[x] = self.off
        self.np.write()

    def pump_water(self, seconds):
        self.pump.on()
        time.sleep(seconds)
        self.pump.off()

    def main(self):
        moisture = self.get_moisture(1000)
        moisture = self.convert_raw_to_perc(moisture)
        self.set_lights(moisture)
        if moisture < 40:  # High moisture level to keep the plant watered. This value may need to be altered.
            self.pump_water(4)
        return moisture


def post_to_sheet(data):
    spreadsheet_id = '1ttF8UqHQJObrt6sr1N9UgYTzUR8WP56yIxjcMWVZcpw'
    API_Key = "AIzaSyAWk3gh2IgLWSdosBmNBRm-hhnQftFXvUE"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/A1%3AA2:append?insertDataOption=INSERT_ROWS&valueInputOption=RAW&key={API_Key}"
    data = {
        "values": [
            [
                "2"
            ]
        ]
    }
    requests.post(url, data=data)


if __name__ == '__main__':
    post_to_sheet('1')

    # connect_to_wifi()
    # auto_water = AutoWater()
    # while True:
    #     measurement = auto_water.main()
    #     print(measurement)
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     try:
    #         s.connect(("192.168.220.1", 65432))
    #     except OSError as e:
    #         machine.soft_reset()
    #     s.send(bytes(f'{measurement}', 'utf-8'))
    #     s.close()
    #     time.sleep(60)
