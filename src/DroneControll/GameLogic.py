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
import easygui
import json
import airsim
import random
import time
import PathApi


class GameLogic:
    # shoul not be changed. game Modes
    STAGE_NOT_IN_GAME = "not_in_game"
    STAGE_TRAINING = "training"
    STAGE_MAIN_PATH = "main"
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

    path_loaded = False

    time_started = 0
    time_finished = 0
    is_time_started = False

    is_path_loaded = False

    def __init__(self, sim):
        self.sim = sim

    def start_game(self, user_name):
        if self.game_stage == self.STAGE_NOT_IN_GAME:
            self.sim.flush_persistent_markers()
            self.load_path_file("SavedPaths\\short_path.json")
            self.game_stage = self.STAGE_TRAINING
            self.sim.restart_training()

    def finish_path(self):
        self.sim.land()
        self.sim.flush_persistent_markers()
        self.time_finished = time.time()
        delta_time = str(self.time_finished - self.time_started)

        # this should be exported to some pdf
        print("delta time: " + delta_time)

        if self.game_stage == self.STAGE_TRAINING:
            self.sim.flush_persistent_markers()

            # finishe training, and load real path
            easygui.msgbox("Yo have finished the Training\n Ready to start the real thing ?", "Path completed")

            self.load_path_file("SavedPaths\\long_path.json")
            self.game_stage = self.STAGE_MAIN_PATH
            self.sim.restart_training()

            return

            # tut nado dron peremestit v nachalnuu positziu
            # i zagruzit'noviy path'

        if self.game_stage == self.STAGE_MAIN_PATH:
            # finishe the game
            self.game_stage = self.STAGE_NOT_IN_GAME
            easygui.msgbox("Yo have completed the assignment in: " + delta_time + "\n Hurray !", "Path completed")

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
            print("time started")

        # update path drawing
        dist = pose.position.distance_to(self.list_of_vectors[self.target_on_path_index])
        if dist < self.EPSILON and self.target_on_path_index + 1 < len(self.list_of_vectors):
            # increment node on path index
            self.target_on_path_index = self.target_on_path_index + 1

            # calculate new, shorted, path
            sublist_of_vectors = self.list_of_vectors[self.target_on_path_index:self.target_on_path_index + 3]
            self.sim.draw_path(sublist_of_vectors)

            # check if experiment ended
            if len(sublist_of_vectors) <= 1:
                self.finish_path()

    def load_path_file(self, filename):
        print("Line 67 called from GameLogic.py")
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
        self.sim.draw_path(self.list_of_vectors)

        # set loaded flag
        self.is_path_loaded = True
