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

class GameLogic:
    sim = None

    # path movement logic
    debug_mode = True
    movement_noise = 0.5
    EPSILON = 1
    target_on_path_index = 0
    list_of_path = []
    list_of_vectors = []
    list_of_vectors_noised = []

    path_loaded = False

    def __init__(self, sim):
        self.sim = sim

    def update(self):
        pose = self.sim.get_raw_position()
        # print("game logic pose:", pose)

        dist = pose.position.distance_to(self.list_of_vectors[self.target_on_path_index])
        # print("game logic dist:", dist)

        # check if path should be redrawed
        if dist < self.EPSILON and self.target_on_path_index + 1 < len(self.list_of_vectors):
            # increment node on path index
            self.target_on_path_index = self.target_on_path_index + 1

            # calculate new, shorted, path
            sublist_of_vectors = self.list_of_vectors[self.target_on_path_index:]
            self.sim.draw_path(sublist_of_vectors)

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
