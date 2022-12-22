import pygame
import AirSimControllerDualStick as sim

"""
This class controls the path adding:

    Paths: 
        'A' - Save a point in a track
        'P' - Go to next saved path
        'K' - Save a path to JSON file
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

class PathMaker():

    def start_path(self, pygame, sim):
        # EVENT PROCESSING STEP
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                break # breaks the loop so the gui can be closed

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

                # checking if key "J" was pressed
                if event.key == pygame.K_n:
                    print("Key N has been pressed")
                    sim.scan_map(-920, -1000)

                # checking if key "T" was pressed
                if event.key == pygame.K_t:
                    print("Key T has been pressed")
                    sim.takeImage(0, 0)

                # p for next point on path
                if event.key == pygame.K_p:
                    sim.go_to_next_pose()

                # a for adding point to path
                if event.key == pygame.K_a:
                    sim.add_to_path()

                if event.key == pygame.K_o:
                    sim.save_path_to_json()

                if event.key == pygame.K_l:
                    sim.load_path_from_json()

                if event.key == pygame.K_SPACE:
                    sim.abort_automation()



