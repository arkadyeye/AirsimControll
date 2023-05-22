'''
it this class I want to open a UDP service, that will get measurment from presure sensors
the sensors connected do esp32, that will send a udp broadcast (maybe milticast is better?)
I expect the esp devices to have their own ID, and sensors amount,
and then the sensors value
'''

import threading
import socket
import time
from time import sleep


class GripForceUdp:
    '''

    for now, there is only 3 devices that can send grip force data
    "Joystick"  - aka f16 stick
    "Boeing" - the yoke boeing "wheel"
    "Wheel" - red car wheel

    for each of them, save the status, so it can be accured at 30 fps

    '''

    joystick_max = 0

    wheel_data = []
    wheel_max = 0

    yoke_data_0 = []
    yoke_data_1 = []
    yoke_max = 0

    wheel_flag = False
    joystick_flag = False
    yoke_flag = False

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.bind(("", 42533))

        print("starting grip force upd server")
        while True:
            data, addr = server.recvfrom(1024)
            string_data = data.decode("utf-8")

            #print("received message: %s" % data)

            if 'Joystik' in string_data:
                data = string_data.split(",")
                data.pop(0)  # pop uot header
                self.joystick_max = max(data)

                if not self.joystick_flag:
                    self.joystick_flag = True
                    print ("Got Joystick Grip Data")

            if 'Grip' in string_data:
                data = string_data.split(",")
                data.pop(0)  # pop out header
                row_index = data.pop(0)  # pop out index
                if int(row_index) == 0:
                    if len(self.wheel_data) > 0:
                        self.wheel_max = max(self.wheel_data)
                    self.wheel_data.clear()
                    self.wheel_data = self.wheel_data + data
                else:
                    self.wheel_data = self.wheel_data + data

                if not self.wheel_flag:
                    self.wheel_flag = True
                    print ("Got Wheel Grip Data")

            if 'Boing' in string_data:
                data = string_data.split(",")
                data.pop(0)  # pop out header
                row_index = int(data.pop(0))  # pop out index

                if row_index == 0:
                    self.yoke_data_0.clear()
                    #b'Boing,0,877,894,453,0,676,585'
                    self.yoke_data_0.append(int(data[0]) - 877)
                    self.yoke_data_0.append(int(data[1]) - 894)
                    self.yoke_data_0.append(int(data[2]) - 453)
                    self.yoke_data_0.append(int(data[3]))
                    self.yoke_data_0.append(int(data[4]) - 679)
                    self.yoke_data_0.append(int(data[5]) - 585)
                else:
                    #b'Boing,1,,944,702,427,0,464,369'
                    self.yoke_data_1.clear()
                    self.yoke_data_1.append(int(data[0]) - 971)
                    self.yoke_data_1.append(int(data[1]) - 702)
                    self.yoke_data_1.append(int(data[2]) - 423)
                    self.yoke_data_1.append(int(data[3]))
                    self.yoke_data_1.append(int(data[4]) - 435)
                    self.yoke_data_1.append(int(data[5]) - 354)

                self.yoke_max = max (self.yoke_data_0 + self.yoke_data_1)

                if not self.yoke_flag:
                    self.yoke_flag = True
                    print ("Got Yoke Grip Data")


        # print (str(time.time())+"   "+string_data)

        # if string_data.startswith("HP:"):
        #    pass

    #          here we should get the data, parse it, and somehow store in a convinient way
    #          but maybe we just need it as string ? because in the end, the data will be string in csv

    def get_header_csv(self):
        return "grip,joystick,wheel,yoke"

    def get_status_csv(self):

        #print("joystick_max: " + str(self.joystick_max) + " wheel: " + str(self.wheel_max) + " yoke: " + str(self.yoke_max))

        ans = "grip," + str(self.joystick_max) + "," + str(self.wheel_max) + "," + str(self.yoke_max) + ","
        return ans

    def init(self):
        # here we should start a thread, with a server, that will update internal values

        server_thread = threading.Thread(target=self.listen, daemon=True)
        server_thread.start()
