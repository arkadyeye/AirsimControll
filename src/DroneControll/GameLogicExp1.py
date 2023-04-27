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
import time
import PathApi

from Logger import PostAnalyser
from ExportData import ExportData


class GameLogic:
    # shoul not be changed. game Modes
    STAGE_NOT_IN_GAME = "not_in_game"
    STAGE_TRAINING = "training"
    STAGE_MAIN_PATH = "main"
    STAGE_FREE_STYLE_1 = "free1"
    STAGE_FREE_STYLE_2 = "free2"

    TIME_GAME_OVER = 180 # 300sec = 5 min
    # STAGE_FINISHED = "finished"

    game_stage = STAGE_NOT_IN_GAME

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
    user_name = ""
    age = ""
    gender = ""
    driving_license = ""
    flying_experience = ""
    adhd = ""

    train_csv = None
    time_train = 0
    time_main = 0

    csv_header = ""
    csv_line = ""

    def __init__(self, sim):
        self.sim = sim

    def start_game(self, user_name, age, gender, driving_lic, flying_exp, adhd):
        if self.game_stage == self.STAGE_NOT_IN_GAME:
            self.user_name = user_name
            self.age = age
            self.gender = gender
            self.driving_license = driving_lic
            self.flying_experience = flying_exp
            self.adhd = adhd

            self.pa = PostAnalyser(user_name + "_training", self.csv_header)
            self.train_csv = self.pa
            self.sim.flush_persistent_markers()
            self.load_path_file("SavedPaths\\short_path.json")
            self.sim.draw_path(self.list_of_vectors,style = "path")
            self.game_stage = self.STAGE_TRAINING
            self.sim.restart_training()

    def finish_path(self):
        self.sim.land()
        self.sim.flush_persistent_markers()
        self.time_finished = time.time()
        delta_time = str(self.time_finished - self.time_started)
        self.is_time_started = False

        # this should be exported to some pdf
        print("delta time: " + delta_time)

        self.sim.flush_persistent_markers()
        self.pa.close()
        self.time_train = delta_time
        print("training time - ", self.time_train)

        self.last_collected_waypoint = None


    def restart_training(self):
        self.sim.flush_persistent_markers()

        if self.game_stage == self.STAGE_TRAINING:
            self.pa = PostAnalyser(self.user_name + "_training", self.csv_header)
            self.load_path_file("SavedPaths\\short_path.json")
            self.sim.draw_path(self.list_of_vectors, style="path")

        if self.game_stage == self.STAGE_MAIN_PATH:
            self.pa = PostAnalyser(self.user_name + "_real", self.csv_header)
            self.load_path_file("SavedPaths\\long_path.json")
            self.sim.draw_path(self.list_of_vectors, style="path")

        if self.game_stage == self.STAGE_FREE_STYLE_1:
            self.pa = PostAnalyser(self.user_name + "_free1", self.csv_header)
            self.load_path_file("SavedPaths\\free_style_waypoints.json")
            self.sim.draw_path(self.list_of_vectors, style="free")

        if self.game_stage == self.STAGE_FREE_STYLE_2:
            self.pa = PostAnalyser(self.user_name + "_free2", self.csv_header)
            self.load_path_file("SavedPaths\\free_style_waypoints.json")
            self.sim.draw_path(self.list_of_vectors, style="free")


        self.train_csv = self.pa
        self.sim.restart_training()

        self.last_collected_waypoint = None


    def advance_next_stage(self):

        if self.game_stage == self.STAGE_TRAINING:
            # finish training, and load real path
            easygui.msgbox("Yo have finished the Training\n Ready to start the real thing ?", "Path completed")
            self.game_stage = self.STAGE_MAIN_PATH
            self.restart_training()
            return

        if self.game_stage == self.STAGE_MAIN_PATH:
            easygui.msgbox("Now you have to find the objects on your own", "Path completed")
            self.game_stage = self.STAGE_FREE_STYLE_1
            self.restart_training()
            return

        if self.game_stage == self.STAGE_FREE_STYLE_1:
            easygui.msgbox("Now you have to find the objects on your own", "Path completed")
            self.game_stage = self.STAGE_FREE_STYLE_2
            self.restart_training()
            return

        if self.game_stage == self.STAGE_FREE_STYLE_2:
            easygui.msgbox("You have done perfectly ! thanks for your time", "Path completed")

            # Insert here Comparator Function
            # parameters = (self.user_name, self.age, self.gender, self.driving_license,
            #              self.flying_experience, self.adhd, self.time_train, self.time_finished)
            # exp_dataa = ExportData()
            # exp_dataa.exp_data(parameters)

            self.game_stage = self.STAGE_NOT_IN_GAME

            return


    def escape_position(self): #this function should take you out of a problematic position
        if self.game_stage == self.STAGE_NOT_IN_GAME:
            return
        if self.game_stage == self.STAGE_TRAINING or self.game_stage == self.STAGE_MAIN_PATH:
            if self.last_collected_waypoint is None:
                self.sim.teleport_to(self.zero_vector)
            else:
                self.sim.teleport_to(self.last_collected_waypoint)

        if self.game_stage == self.STAGE_FREE_STYLE_1 or self.game_stage == self.STAGE_FREE_STYLE_2:
            self.sim.teleport_to(self.zero_vector)

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
            print("time started")

        # update path drawing
        if not self.is_time_started:
            return


        # check if time ended
        if time.time() - self.time_started > self.TIME_GAME_OVER:
            self.finish_path()
            result = easygui.ynbox("5 minutes is over, do you want to restart teh game (yes) \n or abadon it (no) ?","time up")
            if result : # means yes
                self.finish_path()
                self.restart_training()
                self.time_started = time.time()
            else:
                self.finish_path()
                self.game_stage = self.STAGE_NOT_IN_GAME
                return

        # update performance analyzer
        self.pa.add_pose(self.sim.get_position_by_pose(pose))
        self.pa.add_collision(self.sim.get_colisons_counter())
        self.pa.add_csv_data(self.csv_line)
        self.pa.write_full_line()
        self.csv_line = ""

        if self.game_stage == self.STAGE_TRAINING or self.game_stage == self.STAGE_MAIN_PATH:
            # update path drawing (remove already passed cubes)
            dist = pose.position.distance_to(self.list_of_vectors[self.target_on_path_index])
            if dist < self.EPSILON and self.target_on_path_index + 1 < len(self.list_of_vectors):

                # save colleted waypoit
                self.last_collected_waypoint = self.list_of_vectors[self.target_on_path_index]

                # increment node on path index
                self.target_on_path_index = self.target_on_path_index + 1

                # calculate new, shorted, path
                sublist_of_vectors = self.list_of_vectors[self.target_on_path_index:self.target_on_path_index + 3]
                self.sim.draw_path(sublist_of_vectors,"path")

                # check if experiment ended
                if len(sublist_of_vectors) <= 1:
                    self.finish_path()
                    self.advance_next_stage()

        if self.game_stage == self.STAGE_FREE_STYLE_1 or self.game_stage == self.STAGE_FREE_STYLE_2:

            '''
            the logic here should be like this:
            we have a collection of waypoint (relativly small,max 10).
            check if we are close enoth to at least one of them.
            if do: remove it from the list (and display)
            
            the stage end when there is no waypoints left
            '''

            # update path drawing (remove already passed cubes)

            for i in range(0, len(self.list_of_vectors)):
                dist = pose.position.distance_to(self.list_of_vectors[i])
                if dist < self.EPSILON*2:
                    # remove element at I
                    del self.list_of_vectors[i]
                    self.sim.draw_path(self.list_of_vectors, style="free")
                    break

            # check if experiment ended
            if len(self.list_of_vectors) == 0:
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
        #self.sim.draw_path(self.list_of_vectors)

        # set loaded flag
        self.is_path_loaded = True
