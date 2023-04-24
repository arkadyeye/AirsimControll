import json
import time
import random
import easygui

import GameLogic


'''
this class should be devided in game logic, keyboard controller, and path maker
maybe the path maker and game logic should be the same for now



'''

debug_mode = True
movement_noise = 0.5
EPSILON = 1
target_on_path_index = 0
list_of_path = []
list_of_vectors = []
list_of_vectors_noised = []

"""
This class controls the path adding:

    Paths: 
        'A' - Save a point in a track
        'P' - Go to next saved path
        'O' - Save a path to JSON file
        'L' - Load a path from JSON file
        'Spacebar' - Stop auto pilot mode when 'P' is being pressed
    
    
    Results: 
        'S' - Start recording a report (times, etc..)
        'X' - Stop recording a report 
        'T' - Take a screenshot
        'N' - Cause a crash ERROR:root:Writing PNG file.... 
    
    TODO: 
        Write a function that when stopping path key is pressed ending the path and asking
        where to save 
"""

class OperationsFacade():

    def start_path(self, pygame, sim, pathapi, gamelogic):
        # EVENT PROCESSING STEP
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                pygame.quit() # breaks the loop so the gui can be closed

            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

            # checking if keydown event happened or not
            if event.type == pygame.KEYDOWN:
                # print ("event.key",event.key)

                if event.key == pygame.K_s:
                    sim.start_recording()
                if event.key == pygame.K_x:
                    sim.stop_recording()

                # checking if key "N" was pressed
                if event.key == pygame.K_n:
                    print("Key N has been pressed")
                    user_name = easygui.enterbox("What, is your ID?", "New Experiment setup")
                    age = easygui.enterbox("What, is your age?", "New Experiment setup")
                    gender = easygui.enterbox("What, is your gender?", "New Experiment setup")
                    driving_license = easygui.enterbox("Do you have driving license?", "New Experiment setup")
                    flying_experience = easygui.enterbox("Do you have any flight experience?", "New Experiment setup")
                    adhd = easygui.enterbox("Do you have ADHD or similar?", "New Experiment setup")
                    print("user name is:", user_name)
                    gamelogic.start_game(user_name,age,gender,driving_license,flying_experience,adhd)
                    # here we should load the easypath. or maybe call to
                    # some experiment controller.start()

                # checking if key "T" was pressed
                if event.key == pygame.K_t:
                    print("Key T has been pressed")
                    sim.takeImage(0, 0)

                # p for next point on path
                if event.key == pygame.K_p:
                    sim.go_to_next_pose()

                # a for adding point to path
                if event.key == pygame.K_a:
                    pathapi.add_to_path(gamelogic)

                if event.key == pygame.K_o:
                    print("Path saved as JSON file")
                    pathapi.save_path_to_json()

                if event.key == pygame.K_l:
                    pathapi.load_path_from_json(gamelogic)

                if event.key == pygame.K_SPACE:
                    sim.abort_automation()


    # def add_to_path(self, sim):
    #     list_of_path.append(sim.get_position())
    #     list_of_vectors.append(sim.get_position_vector())
    #
    #     # this will deleta trace - not good
    #     # client.simFlushPersistentMarkers()
    #
    #     sim.client.simPlotPoints(points=list_of_vectors,
    #                          color_rgba=[1.0, 0.0, 0.0, 0.2], size=25, duration=1000, is_persistent=False)
    #
    #     sim.client.simPlotLineStrip(
    #         points=list_of_vectors,
    #         color_rgba=[1.0, 1.0, 0.0, 0.02], thickness=5, duration=300.0, is_persistent=False)
    #
    #     print("point added")

    # Saves multipul jsons
    def save_path_to_json(self):
        # with open('movePath.json', 'w', encoding='utf-8') as f:
        #     json.dump(list_of_path, f, ensure_ascii=False, indent=4)

        ts = time.time()
        str_timestamp = str(ts)
        with open("SavedPaths/" + str_timestamp[0:9]+".json", 'w', encoding='utf-8') as f:
            json.dump(list_of_path, f)

    def load_path_from_json(self, sim):
        global list_of_path
        global list_of_vectors
        global list_of_vectors_noised
        global target_on_path
        path = easygui.fileopenbox()
        with open(path) as data_file:
            data_loaded = json.load(data_file)
            print("data_loaded", data_loaded)
            list_of_path = data_loaded
        print(len(list_of_path))
        for i in range(len(list_of_path)):
            list_of_vectors.append(sim.air_sim.Vector3r(list_of_path[i][0], list_of_path[i][1], list_of_path[i][2]))
            list_of_vectors_noised.append(sim.air_sim.Vector3r(
                list_of_path[i][0] + round(random.uniform(-movement_noise, movement_noise), 3),
                list_of_path[i][1] + round(random.uniform(-movement_noise, movement_noise), 3),
                list_of_path[i][2] + round(random.uniform(-movement_noise, movement_noise), 3),
            ))

        # clean and redraw path
        sim.client.simFlushPersistentMarkers()
        target_on_path = list_of_vectors[0]
        self.update_visible_path(sim)

    def update_visible_path(self, sim):
        global target_on_path_index
        global target_on_path

        if len(list_of_vectors) == 0:
            return

            # track our movement on path

        pose = sim.client.simGetVehiclePose(vehicle_name="Drone0")
        dist = pose.position.distance_to(target_on_path)

        # print(target_on_path.x_val)
        if dist < EPSILON and target_on_path_index + 1 < len(list_of_vectors):
            target_on_path_index = target_on_path_index + 1
            target_on_path = list_of_vectors[target_on_path_index]

        # print("dist to target:", dist)

        sublist_of_vectors = list_of_vectors[target_on_path_index]
        sublist_of_vectors_noised = list_of_vectors_noised[target_on_path_index:]
        sim.client.simPlotPoints(points=sublist_of_vectors,
                             color_rgba=[1.0, 0.0, 0.0, 1.0], size=25, duration=0.5, is_persistent=False)

        sim.client.simPlotLineStrip(
            points=sublist_of_vectors,
            color_rgba=[1.0, 1.0, 0.0, 1.0], thickness=5, duration=0.5, is_persistent=False)

        if debug_mode:
            sim.client.simPlotPoints(points=sublist_of_vectors_noised,
                                 color_rgba=[0.0, 0.0, 1.0, 1.0], size=25, duration=0.1, is_persistent=False)

            sim.client.simPlotLineStrip(
                points=sublist_of_vectors_noised,
                color_rgba=[0.0, 0.0, 1.0, 0.0], thickness=5, duration=0.1, is_persistent=False)

