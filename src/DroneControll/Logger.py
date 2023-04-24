'''

this class should get a name, create a directory, and write there a log file

probably it will be extended to game analysis, in parallel with log creation
'''

import os
import time

from datetime import datetime


class PostAnalyser:
    csv_file = None
    full_line = ""


    def __init__(self, name,header):
        #create folder
        folder_name = "..//..//"+"{:%Y_%m_%d_%H_%M_%S}".format(datetime.now()) + "_" + name
        os.mkdir(folder_name)
        print("Directory '%s' created" % folder_name)

        #create csv file for the results
        self.csv_file = open(folder_name + "//path.csv", "w")
        self.csv_file.write("timeMS,x,y,z,yaw,collisions,"+header+"\n")

        ##f.close()

    def close(self):
        self.csv_file.close()

    def add_pose(self, position):
        self.full_line = self.full_line + str(round(time.time()*1000))+","+str(position[0])+","+str(position[1])+","+str(position[2])+","+str(position[3])
    def add_collision(self, collision_counter):
        self.full_line = self.full_line + str(collision_counter)+","

    def add_csv_data(self,csv_data):
        self.full_line = self.full_line + "," + csv_data

    def write_full_line(self):
        self.csv_file.write(self.full_line + "\n")
        self.full_line = ""



