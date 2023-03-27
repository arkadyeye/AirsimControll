'''
it this class I want to open a UDP service,that wil get data from the emotiBit osiloscope
that is forwarded by UDP.

note that the timestamp maybe sightly wrong, this is the cost of live-streaming
to get the real real times, use sd card for recording, and parser from emotiBit software
'''

import threading
import socket
from time import sleep







class EmotiBitUdp:

    '''
    the logic is like this:

    timestamp |  packet num | num of vals | type |protocol | accurasy | data ...
    1203046	  |  61065      | 2	          |  AX  |	1	   |   100    |	0.774	0.776

    to get the last value we need number of values (here it's 7 = [2]+5)
    and the type [3]

    '''

    def __init__(self):
        # there is several messages types, that can be received from emotibit
        # my logic is just to save the last status, and write it to csv, ance requested (every 30 fps)

        # AX,AY,AZ
        self.last_acc_x = 0
        self.last_acc_y = 0
        self.last_acc_z = 0

        # GX,GY,GZ
        self.last_gyro_x = 0
        self.last_gyro_y = 0
        self.last_gyro_z = 0

        self.last_mag_x = 0
        self.last_mag_y = 0
        self.last_mag_z = 0

        # EDA- Electrodermal Activity, EDL- Electrodermal Level
        self.last_EDA = 0
        self.last_EDL = 0

        # BI	Heart Inter-beat Interval
        self.last_BI = 0

        # HR	Heart Rate
        self.last_HR = 0

        # PPG - heart sensor, there 3 colors: Red (PR),Green(PG),InfraRed(PI)
        self.last_PR = 0
        self.last_PG = 0
        self.last_PI = 0

        # SA	Skin Conductance Response (SCR) Amplitude
        self.last_SA = 0

        # SF	Skin Conductance Response (SCR) Frequency
        self.last_SF = 0

        # SR	Skin Conductance Response (SCR) Rise Time
        self.last_SR = 0

        # T1    Temperature
        self.last_T1 = 0


        # B% - battery percentage
        self.last_battery = 0

        # TL    TimeStamp Local. look like a syncronization clock value
        self.last_TL = ""
        self.last_TL_internal_time = 0

    def parse_update(self,string_data):
        splited_string = string_data.split(",")
        index_of_data = splited_string[2] + 5
        data = splited_string[index_of_data]
        #9 degree orientation
        if 'AX' in string_data:
            self.last_acc_x = data
        if 'AY' in string_data:
            self.last_acc_y = data
        if 'AZ' in string_data:
            self.last_acc_z = data

        if 'GX' in string_data:
            self.last_gyro_x = data
        if 'GY' in string_data:
            self.last_gyro_y = data
        if 'GZ' in string_data:
            self.last_gyro_z = data

        if 'MX' in string_data:
            self.last_mag_x = data
        if 'MY' in string_data:
            self.last_mag_y = data
        if 'MZ' in string_data:
            self.last_mag_z = data

        # biometric data
        if 'EDA' in string_data:
            self.last_EDA = data
        if 'EDL' in string_data:
            self.last_EDL = data

        if 'HR' in string_data:
            self.last_HR = data
        if 'BI' in string_data:
            self.last_BI = data

        if 'PR' in string_data:
            self.last_PR = data
        if 'PG' in string_data:
            self.last_PG = data
        if 'PI' in string_data:
            self.last_PI = data


        if 'SA' in string_data:
            self.last_SA = data
        if 'SF' in string_data:
            self.last_SF = data
        if 'SR' in string_data:
            self.last_SR = data

        if 'T1' in string_data:
            self.last_T1 = data

        # technical_data
        if 'B%' in string_data:
            self.last_battery = data

        if 'TL' in string_data:
            self.last_TL = data
            self.last_TL_internal_time = splited_string[0]


        now, we have to add a funtion, that will output a string of all values in one line

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.bind(("", 12346))
        print("starting emoti upd server")
        while True:
            data, addr = server.recvfrom(1024)
            string_data = data.decode("utf-8")

            # if 'HR' in string_data:
            print (string_data)
    #          here we should get the data, parse it, and somehow store in a convinient way
    #          but maybe we just need it as string ? because in the end, the data will be string in csv

    def init(self):
        # here we should start a thread, with a server, that will update internal values
        server_thread = threading.Thread(target=self.listen, daemon=True)
        server_thread.start()
