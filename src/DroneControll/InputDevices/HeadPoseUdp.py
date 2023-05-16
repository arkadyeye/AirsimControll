'''
it this class I want to open a UDP service, that will get measurment from presure sensors
the sensors connected do esp32, that will send a udp broadcast (maybe milticast is better?)
I expect the esp devices to have their own ID, and sensors amount,
and then the sensors value
'''

import threading
import socket
from time import sleep


class HeadPoseUdp:
    last_status = "head_pose,n/a,n/a,n/a,n/a"

    def listen(self):
        self.last_status = "head_pose,n/a,n/a,n/a,n/a"
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.bind(("", 42544))

        print("starting head tracking upd server")
        while True:
            data, addr = server.recvfrom(1024)
            string_data = data.decode("utf-8")
            # print("received message: %s" % data)
            # if 'HR' in string_data:

            if string_data.startswith("HP:"):
                self.last_status = string_data[3:]
                print(self.last_status)
    #          here we should get the data, parse it, and somehow store in a convinient way
    #          but maybe we just need it as string ? because in the end, the data will be string in csv


    def get_header_csv(self):
        return "head_pose,head_x,head_y,head_z,blink"

    def get_status_csv(self):
       return self.last_status


    def init(self):
        # here we should start a thread, with a server, that will update internal values

        self.last_status = ""

        server_thread = threading.Thread(target=self.listen, daemon=True)
        server_thread.start()
