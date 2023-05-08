'''

in this class we shouild add logic that is going about the drone movement

for now I see few sections:
a) count collisions, and fail the task when needed
b) update the path, and switch from autonomus to manual
c) make a detailed log, and give a score

note: how do you compare real path with 1000 points, and a virtual path build from 10 points ?

the class should be hooket to game event loop, and should not use heavy logic,
as it will block the controll, and the game will be lag

'''

'''
game logic for experement #1
the experement goes like this:
step a: a user starts with guided short path, just for training with the controll device (like wheel)
step b: the user flying a more complex path, still guided
step c: the user have a free style moving, but have to collect waypoints in any order
step d: the same, but with "vied of view limitation" glasess

'''

import easygui
import json
import airsim
import random
import PathApi

from Logger import PostAnalyser
from PDFMaker import PDFMaker

import numpy as np
import similaritymeasures
from csv import reader

import os
import time
from datetime import datetime

import winsound
from pathlib import Path


class GameLogicExp2:
    # shoul not be changed. game Modes
    STAGE_NOT_IN_GAME = "not_in_game"
    STAGE_SHORT = "short_1"
    STAGE_LONG = "long_1"
    round_counter = 0
    max_rounds = 4

    TIME_GAME_OVER = 600  # 600sec = 10 min

    PATH_DRAW_AHEAD = 3

    mark = 400

    game_stage = STAGE_NOT_IN_GAME
    folder_name = ""

    sim = None

    # path movement logic
    debug_mode = True
    movement_noise = 0.5
    EPSILON = 2
    target_on_path_index = 0
    list_of_path = []
    list_of_vectors = []
    list_of_vectors_noised = []
    last_collected_waypoint = None
    zero_vector = airsim.Vector3r(0, 0, 0)

    path_loaded = False

    time_started = 0
    time_finished = 0
    is_time_started = False

    is_path_loaded = False

    pa = None
    pdfMaker = None
    user_name = ""
    age = ""
    gender = ""
    driving_license = ""
    flying_experience = ""
    adhd = ""

    train_csv = None
    time_train = 0
    time_main = 0

    total_dist = 0
    prev_point = None

    csv_header = ""
    csv_line = ""

    # remember the x,y,z coordinates, so we can compare to optimal path layetr
    a_x = []
    a_y = []
    a_z = []
    counter = 0

    optimal_short = None
    optimal_Long = None

    optimal_short_time = 32  # sec
    optimal_long_time = 86  # sec
    optimal_long_2_time = 90  # sec

    # beep on waypoint collected
    duration = 30 # ms
    freq = 2000 # hz

    def __init__(self, sim):
        self.sim = sim
        self.optimal_short = self.load_optimal_path_data("SavedPaths\\optimal_2min.csv")
        self.optimal_long = self.load_optimal_path_data("SavedPaths\\optimal_4min.csv")

    def start_game(self, user_name, age, gender, driving_lic, flying_exp, adhd):

        self.last_collected_waypoint = None
        self.mark = 400
        self.total_dist = 0
        self.a_x = []
        self.a_y = []
        self.a_z = []
        self.counter = 0

        self.round_counter = 0

        if self.pa is not None:
            self.pa.close()

        if self.pdfMaker is not None:
            self.pdfMaker.generate_pdf()

        # if self.game_stage == self.STAGE_NOT_IN_GAME:
        self.user_name = user_name
        self.age = age
        self.gender = gender
        self.driving_license = driving_lic
        self.flying_experience = flying_exp
        self.adhd = adhd

        folder_name = "..//..//Results//" + user_name + "_" +"{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
        path = Path(folder_name)
        path.mkdir(parents=True, exist_ok=True)
        print("Directory '%s' created" % folder_name)
        self.folder_name = folder_name

        self.pa = PostAnalyser(folder_name, "short_1", self.csv_header)
        self.pdfMaker = PDFMaker(folder_name+"/", self.user_name, self.age, self.gender, self.driving_license, self.flying_experience,
                                 self.adhd)
        self.train_csv = self.pa
        self.sim.flush_persistent_markers()
        self.load_path_file("SavedPaths\\shraga_2min.json")
        self.sim.draw_path(self.list_of_vectors[0:self.PATH_DRAW_AHEAD], style="path")
        self.game_stage = self.STAGE_SHORT
        self.sim.restart_training()

    def finish_path(self):
        self.sim.land()
        self.sim.flush_persistent_markers()
        self.time_finished = time.time()
        self.time_train = self.time_finished - self.time_started
        self.is_time_started = False

        # this should be exported to some pdf

        self.sim.flush_persistent_markers()
        self.pa.close()
        print("training time - ", self.time_train)

        self.last_collected_waypoint = None

    def restart_training(self):
        self.sim.flush_persistent_markers()
        self.sim.restart_training()

        self.pa = PostAnalyser(self.folder_name, self.game_stage+str(self.round_counter), self.csv_header)
        if self.game_stage == self.STAGE_SHORT:
            self.load_path_file("SavedPaths\\shraga_2min.json")
        if self.game_stage == self.STAGE_LONG:
            self.load_path_file("SavedPaths\\shraga_4min.json")

        self.sim.draw_path(self.list_of_vectors[0:self.PATH_DRAW_AHEAD], style="path")

        self.train_csv = self.pa

        self.last_collected_waypoint = None
        self.mark = 400
        self.total_dist = 0
        self.a_x = []
        self.a_y = []
        self.a_z = []
        self.counter = 0

    def advance_next_stage(self):

        # here we should update pdf generator

        # reduce for collisions

        # calc ferchet distance
        exp_data = np.zeros((self.counter, 3))
        exp_data[:, 0] = self.a_x
        exp_data[:, 1] = self.a_y
        exp_data[:, 2] = self.a_z

        if self.game_stage == self.STAGE_SHORT:
            self.mark = self.mark - self.sim.get_colisons_counter() * 10
            df = similaritymeasures.frechet_dist(exp_data, self.optimal_short)
            self.mark = self.mark - df

            df_time = self.time_train - self.optimal_short_time
            self.mark = self.mark - df_time

            df = round(df, 2)
            self.time_train = round(self.time_train, 2)
            self.total_dist = round(self.total_dist, 2)
            self.mark = round(self.mark, 2)

            easygui.msgbox("You have done the stage \n collisions " + str(self.sim.get_colisons_counter()) + " \n" + \
                           "time:" + str(self.time_train) + " \n" + \
                           "dist: " + str(self.total_dist) + " \n" + \
                           "fr.dist: " + str(df) + " \n" + \
                           "total mark is: " + str(self.mark), "Path completed")

            self.pdfMaker.update_phase(self.STAGE_SHORT+"_"+str(self.round_counter), self.time_train, self.total_dist, df,exp_data, self.optimal_short)

            # finish training, and load real path
            easygui.msgbox("Ready to start the next thing ?", "Path completed")
            self.game_stage = self.STAGE_LONG
            self.restart_training()
            return

        if self.game_stage == self.STAGE_LONG:
            self.mark = self.mark - self.sim.get_colisons_counter() * 10

            df = similaritymeasures.frechet_dist(exp_data, self.optimal_long)
            self.mark = self.mark - df

            df_time = self.time_train - self.optimal_long_time
            self.mark = self.mark - df_time

            df = round(df, 2)
            self.time_train = round(self.time_train, 2)
            self.total_dist = round(self.total_dist, 2)
            self.mark = round(self.mark, 2)

            easygui.msgbox("You have done the stage \n collisions " + str(self.sim.get_colisons_counter()) + " \n" + \
                           "time:" + str(self.time_train) + " \n" + \
                           "dist: " + str(self.total_dist) + " \n" + \
                           "fr.dist: " + str(df) + " \n" + \
                           "total mark is: " + str(self.mark), "Path completed")

            self.pdfMaker.update_phase(self.STAGE_SHORT+"_"+str(self.round_counter), self.time_train, self.total_dist, df, exp_data, self.optimal_long )

            if self.round_counter < self.max_rounds:
                self.round_counter = self.round_counter + 1
                easygui.msgbox("Ready to start the next thing ?", "Path completed")
                self.game_stage = self.STAGE_SHORT
                self.restart_training()
            else:
                easygui.msgbox("You have reached the end of the tsk\nThank you for your time", "Path completed")
                self.game_stage =  self.STAGE_NOT_IN_GAME
                self.restart_training()

            return

    def escape_position(self):  # this function should take you out of a problematic position
        if self.game_stage == self.STAGE_NOT_IN_GAME:
            self.sim.teleport_to(self.zero_vector)
            return

        self.mark = self.mark - 50

        if self.last_collected_waypoint is None:
            self.sim.teleport_to(self.zero_vector)
        else:
            self.sim.teleport_to(self.last_collected_waypoint)

        # if self.game_stage == self.STAGE_FREE_STYLE_1 or self.game_stage == self.STAGE_FREE_STYLE_2:
        #     self.sim.teleport_to(self.zero_vector)

    def update(self):

        # if we are not in game, just return
        if self.game_stage == self.STAGE_NOT_IN_GAME:
            return

        # here we are running on training/main path
        if not self.is_path_loaded:
            print("ERROR, no path loaded, but expected to be")
            return

        # get drone position
        pose = self.sim.get_raw_position()

        # check if movement started
        if self.is_time_started == False and (pose.position.x_val != 0 or pose.position.y_val != 0):
            self.time_started = time.time()
            self.is_time_started = True
            self.csv_line = ""
            self.prev_point = self.sim.get_position_vector()
            print("time started")

        # update path drawing
        if not self.is_time_started:
            return

        # check if time ended
        if time.time() - self.time_started > self.TIME_GAME_OVER:
            self.finish_path()
            result = easygui.ynbox("5 minutes is over, do you want to restart teh game (yes) \n or abandon it (no) ?",
                                   "time up")
            if result:  # means yes
                self.finish_path()
                self.restart_training()
                self.time_started = time.time()
            else:
                self.finish_path()
                self.game_stage = self.STAGE_NOT_IN_GAME
                return

        # update performance analyzer
        pow_tuple = self.sim.get_position_by_pose(pose)
        self.pa.add_pose(pow_tuple)
        self.pa.add_collision(self.sim.get_colisons_counter())
        self.pa.add_csv_data(self.csv_line)
        self.pa.write_full_line()
        self.csv_line = ""

        self.a_x.append(pow_tuple[0])
        self.a_y.append(pow_tuple[1])
        self.a_z.append(pow_tuple[2])
        self.counter += 1

        self.total_dist = self.total_dist + pose.position.distance_to(self.prev_point)
        self.prev_point = self.sim.get_position_vector()


        # update path drawing (remove already passed cubes)
        dist = pose.position.distance_to(self.list_of_vectors[self.target_on_path_index])
        if dist < self.EPSILON and self.target_on_path_index + 1 < len(self.list_of_vectors):

            # beep on collected
            winsound.Beep(self.freq, self.duration)

            # save colleted waypoit
            self.last_collected_waypoint = self.list_of_vectors[self.target_on_path_index]

            # increment node on path index
            self.target_on_path_index = self.target_on_path_index + 1

            # calculate new, shorted, path
            sublist_of_vectors = self.list_of_vectors[
                                 self.target_on_path_index:self.target_on_path_index + self.PATH_DRAW_AHEAD]
            self.sim.draw_path(sublist_of_vectors, "path")

            # check if experiment ended
            if len(sublist_of_vectors) <= 1:
                self.finish_path()
                self.advance_next_stage()

    def addCsvHeader(self, csv_header):
        self.csv_header = self.csv_header + "," + csv_header

    def addCsvData(self, csv_data):
        self.csv_line = self.csv_line + "," + csv_data

    def load_path_file(self, filename):

        # open file dialog
        # path = easygui.fileopenbox()

        # read data from file
        with open(filename) as data_file:
            data_loaded = json.load(data_file)
            print("data_loaded", data_loaded)

        # clear older path
        self.list_of_vectors.clear()
        self.list_of_vectors_noised.clear()

        # generate workable path of vectors, and it's noised variant
        for i in range(len(data_loaded)):
            self.list_of_vectors.append(airsim.Vector3r(data_loaded[i][0], data_loaded[i][1], data_loaded[i][2]))
            self.list_of_vectors_noised.append(airsim.Vector3r(
                data_loaded[i][0] + round(random.uniform(-self.movement_noise, self.movement_noise), 3),
                data_loaded[i][1] + round(random.uniform(-self.movement_noise, self.movement_noise), 3),
                data_loaded[i][2] + round(random.uniform(-self.movement_noise, self.movement_noise), 3),
            ))

        # set the target to the first point of the path
        self.target_on_path_index = 0

        # load path to world
        # self.sim.draw_path(self.list_of_vectors)

        # set loaded flag
        self.is_path_loaded = True

    def load_optimal_path_data(self, path):
        in_x = []
        in_y = []
        in_z = []
        in_counter = 0
        with open(path, 'r') as read_obj:
            # pass the file object to reader() to get the reader object
            csv_reader = reader(read_obj)
            header = next(csv_reader)
            header = next(csv_reader)
            # Iterate over each row in the csv using reader object
            for row in csv_reader:
                # row variable is a list that represents a row in csv
                # print(row)
                in_x.append(row[1])
                in_y.append(row[2])
                in_z.append(row[3])
                in_counter += 1

        ref_data = np.zeros((in_counter, 3))
        ref_data[:, 0] = in_x
        ref_data[:, 1] = in_y
        ref_data[:, 2] = in_z
        return ref_data
