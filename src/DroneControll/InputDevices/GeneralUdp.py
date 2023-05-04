'''
it this class I want to open a UDP service, that will get measurment from presure sensors
the sensors connected do esp32, that will send a udp broadcast (maybe milticast is better?)
I expect the esp devices to have their own ID, and sensors amount,
and then the sensors value
'''

import threading
import socket
from time import sleep


class PressureUdp:

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.bind(("", 42544))

        print("starting upd server")
        while True:
            data, addr = server.recvfrom(1024)
            string_data = data.decode("utf-8")
            # print("received message: %s" % data)
            # if 'HR' in string_data:
            print (string_data)
            if string_data.startswith("HP:"):
                pass
    #          here we should get the data, parse it, and somehow store in a convinient way
    #          but maybe we just need it as string ? because in the end, the data will be string in csv


    def get_header_csv(self):
        return "AX,AY,AZ,GX,GY,GZ,MX,MY,MZ,EDA,EDL,HR,BI,PR,PG,PI,SA,SF,SR,T1,B%,TL,TLI"

    def get_status_csv(self):
        ans = ""
        ans = ans + self.last_acc_x + "," + self.last_acc_y + "," + self.last_acc_z + ","
        ans = ans + self.last_gyro_x + "," + self.last_gyro_y + "," + self.last_gyro_z + ","
        ans = ans + self.last_mag_x + "," + self.last_mag_y + "," + self.last_mag_z + ","
        ans = ans + self.last_EDA + "," + self.last_EDL + "," + self.last_HR + "," + self.last_BI + ","
        ans = ans + self.last_PR + "," + self.last_PG + "," + self.last_PI + ","
        ans = ans + self.last_SA + "," + self.last_SF + "," + self.last_SR + "," + self.last_T1 + ","
        ans = ans + self.last_battery + "," + self.last_TL + "," + self.last_TL_internal_time

        return ans


    def init(self):
        # here we should start a thread, with a server, that will update internal values
        server_thread = threading.Thread(target=self.listen, daemon=True)
        server_thread.start()
