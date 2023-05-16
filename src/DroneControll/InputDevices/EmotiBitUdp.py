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
        self.last_acc_x = "n/a"
        self.last_acc_y = "n/a"
        self.last_acc_z = "n/a"

        # GX,GY,GZ
        self.last_gyro_x = "n/a"
        self.last_gyro_y = "n/a"
        self.last_gyro_z = "n/a"

        self.last_mag_x = "n/a"
        self.last_mag_y = "n/a"
        self.last_mag_z = "n/a"

        # EDA- Electrodermal Activity, EDL- Electrodermal Level
        self.last_EDA = "n/a"
        self.last_EDL = "n/a"

        # BI	Heart Inter-beat Interval
        self.last_BI = "n/a"

        # HR	Heart Rate
        self.last_HR = "n/a"

        # PPG - heart sensor, there 3 colors: Red (PR),Green(PG),InfraRed(PI)
        self.last_PR = "n/a"
        self.last_PG = "n/a"
        self.last_PI = "n/a"

        # SA	Skin Conductance Response (SCR) Amplitude
        self.last_SA = "n/a"

        # SF	Skin Conductance Response (SCR) Frequency
        self.last_SF = "n/a"

        # SR	Skin Conductance Response (SCR) Rise Time
        self.last_SR = "n/a"

        # T1    Temperature
        self.last_T1 = "n/a"


        # B% - battery percentage
        self.last_battery = "n/a"

        # TL    TimeStamp Local. look like a syncronization clock value
        self.last_TL = "n/a"
        self.last_TL_internal_time = "n/a"

    def parse_update(self,string_data):

        print ("parse called for : ",string_data)

        splited_string = string_data.split(",")
        index_of_data = int(splited_string[2]) + 5
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
        if 'EA' in string_data:
            self.last_EDA = data
        if 'EL' in string_data:
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

    def get_header_csv(self):
        return "EmotiBit,AX,AY,AZ,GX,GY,GZ,MX,MY,MZ,EDA,EDL,HR,BI,PR,PG,PI,SA,SF,SR,T1,B%,TL,TLI"

    def get_status_csv(self):
        ans = "EmotiBit,"
        ans = ans + self.last_acc_x + "," + self.last_acc_y + "," + self.last_acc_z + ","
        ans = ans + self.last_gyro_x + "," + self.last_gyro_y + "," + self.last_gyro_z + ","
        ans = ans + self.last_mag_x + "," + self.last_mag_y + "," + self.last_mag_z + ","
        ans = ans + self.last_EDA + "," + self.last_EDL + "," + self.last_HR + "," + self.last_BI + ","
        ans = ans + self.last_PR + "," + self.last_PG + "," + self.last_PI + ","
        ans = ans + self.last_SA + "," + self.last_SF + "," + self.last_SR + "," + self.last_T1 + ","
        ans = ans + self.last_battery + "," + self.last_TL + "," + self.last_TL_internal_time

        return ans

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.bind(("", 12346))
        print("starting emoti upd server")
        while True:
            data, addr = server.recvfrom(1024)
            string_data = data.decode("utf-8")

            # if 'HR' in string_data:
            #print (string_data)
            self.parse_update(string_data)
    #          here we should get the data, parse it, and somehow store in a convinient way
    #          but maybe we just need it as string ? because in the end, the data will be string in csv

    def init(self):
        # here we should start a thread, with a server, that will update internal values
        server_thread = threading.Thread(target=self.listen, daemon=True)
        server_thread.start()
