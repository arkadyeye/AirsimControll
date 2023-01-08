import json
import time
import random
import easygui
import airsim

from src.DroneControll.GameLogic import GameLogic


class PathApi:
    list_of_path = []
    def save_path_to_json(self):
        # with open('movePath.json', 'w', encoding='utf-8') as f:
        #     json.dump(list_of_path, f, ensure_ascii=False, indent=4)

        print (self.list_of_path)

        ts = time.time()
        str_timestamp = str(ts)
        with open("SavedPaths/" + str_timestamp[0:9] + ".json", 'w', encoding='utf-8') as f:
            json.dump(self.list_of_path, f, ensure_ascii=False, indent=4)

    def load_path_file(self, filename, game_logic):
        print("Line 67 called from GameLogic.py")
        # open file dialog
        # path = easygui.fileopenbox()

        # read data from file
        with open(filename) as data_file:
            data_loaded = json.load(data_file)
            print("data_loaded", data_loaded)

        # clear older path
        game_logic.list_of_vectors.clear()
        game_logic.list_of_vectors_noised.clear()

        # generate workable path of vectors, and it's noised variant
        for i in range(len(data_loaded)):
            game_logic.list_of_vectors.append(airsim.Vector3r(data_loaded[i][0], data_loaded[i][1], data_loaded[i][2]))
            game_logic.list_of_vectors_noised.append(airsim.Vector3r(
                data_loaded[i][0] + round(random.uniform(-game_logic.movement_noise, game_logic.movement_noise), 3),
                data_loaded[i][1] + round(random.uniform(-game_logic.movement_noise, game_logic.movement_noise), 3),
                data_loaded[i][2] + round(random.uniform(-game_logic.movement_noise, game_logic.movement_noise), 3),
            ))

        # set the target to the first point of the path
        game_logic.target_on_path_index = 0

        # load path to world
        game_logic.sim.draw_path(game_logic.list_of_vectors)

    def add_to_path(self, game_logic):
        #game_logic.list_of_path.append(game_logic.sim.get_position())
        #game_logic.list_of_vectors.append(game_logic.sim.get_position_vector())

        # this will deleta trace - not good
        # client.simFlushPersistentMarkers()

        self.list_of_path.append(game_logic.sim.get_position())

        game_logic.sim.client.simPlotPoints(points=game_logic.list_of_vectors,
                                 color_rgba=[1.0, 0.0, 0.0, 0.2], size=25, duration=1000, is_persistent=False)

        game_logic.sim.client.simPlotLineStrip(
            points=game_logic.list_of_vectors,
            color_rgba=[1.0, 1.0, 0.0, 0.02], thickness=5, duration=300.0, is_persistent=False)

        print("point added")
