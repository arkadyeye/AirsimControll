import pygame
#import AirSimControllerDualStick as sim
from OperationsFacade import OperationsFacade
from AirSimFacade import AirSimFacade
from AirSimCarFacade import AirSimCarFacade
from GameLogic import GameLogic
from YokeController import YokeController
from RedWheelController import RedWheelController
# from HotasXControllerOhad import HotasXController
from PathApi import PathApi
from HotasXController import HotasXController
from LogitechRacingController import LogitechRacingController
from LogitechDualAction import LogitechDualAction





import time

connected_joystick = None
image = None


# Define some colors
darkgrey = (40, 40, 40)
lightgrey = (150, 150, 150)


# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:

    global yoke_joystick

    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, lightgrey)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()

# Set the width and height of the screen [width,height]
size = [500, 980]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Joystick")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# init airsim
sim = AirSimFacade("Drone0")
#sim = AirSimCarFacade("PhysXCar")
gameLogic = GameLogic(sim)
pathApi = PathApi()
# Pathapi.load_path_file("SavedPaths\\167290525.json", gamelogic)

# training path
#
#pathApi.load_path_file("SavedPaths\\167299251.json", gameLogic)

# real path
#pathApi.load_path_file("SavedPaths\\167299362.json", gameLogic)

# Initialize the joysticks
pygame.joystick.init()

# here , check what joystick is connected, and init its class
joystick_count = pygame.joystick.get_count()

joysticks_list = []
# For each joystick:
for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    name = joystick.get_name()
    print("joystick name", name)

    if name == "TCA YOKE BOEING":
        joysticks_list.append(YokeController(sim))

    if name == "PS(R) Gamepad Adaptor":
        joysticks_list.append(RedWheelController(sim))

    if name == "T.Flight Hotas X":
        joysticks_list.append(HotasXController(sim))

    if name == "Logitech Racing Wheel":
        joysticks_list.append(LogitechRacingController(sim))

    if name == "Logitech Dual Action":
        joysticks_list.append(LogitechDualAction(sim))




# Get ready to print
textPrint = TextPrint()


#sim.init()


OperationsFacade = OperationsFacade()

#init results analyzer



# -------- Main Program Loop -----------
time_a = 0
time_b = 0
while done == False:

    time_a = time.time()

    # for event in pygame.event.get():  # User did something
    #     if event.type == pygame.QUIT:  # If user clicked close
    #         break  # breaks the loop so the gui can be closed
    #
    #     # checking if keydown event happened or not
    #     if event.type == pygame.KEYDOWN:
    #         print ("event.key",event.key)
    #
    #         if event.key == pygame.K_1:
    #             sim.teleportTo(-12, -12, -3, "Get to the palace")
    #
    #         # if event.key == pygame.K_s:
    #         #     sim.start_recording()
    #         # if event.key == pygame.K_x:
    #         #     sim.stop_recording()

    # why the path maker is in the loop !!!!!!!!!!
    # ---------------A N S W E R------------------
    # Has to be here, else would not be able to press buttons,
    # everything in class was in the current while loop
    OperationsFacade.start_path(pygame, sim, pathApi, gameLogic)


    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(darkgrey)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # for i in range(joystick_count):

    joystick1 = pygame.joystick.Joystick(0)
    joystick1.init()
    # print ("joy 1 axis",joystick1.get_axis(0))

    if joystick_count > 1:
        joystick2 = pygame.joystick.Joystick(1)
        joystick2.init()
    # print("joy 2 axis", joystick2.get_axis(0))



    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        # joystick.init()
        # print("joy "+str(i)+" axis"+str(joystick.get_axis(0)))

        textPrint.print(screen, "Joystick {}".format(i))
        textPrint.indent()

        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.print(screen, "Joystick name: {}".format(name))

        # if name == "TCA YOKE BOEING":

        for j in range(len(joysticks_list)):
            joysticks_list[j].update(joystick)


        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.print(screen, "Number of axes: {}".format(axes))
        textPrint.indent()

        for i in range(axes):
            axis = joystick.get_axis(i)
            # if i == 0:  # means X
            #     sim.add_rotation(axis)
            # if i == 1: # means Y
            #     sim.set_speed(axis)
            # if i == 2:
            #     sim.set_horizontal_speed(axis)
            # if i == 3:
            #     sim.add_vertical_position(axis)

            textPrint.print(screen, "Axis {} value: {:>6.0f}".format(i, axis))
        textPrint.unindent()

        buttons = joystick.get_numbuttons()
        textPrint.print(screen, "Number of buttons: {}".format(buttons))
        textPrint.indent()

        buttons_list = []
        for i in range(buttons):
            button = joystick.get_button(i)
            textPrint.print(screen, "Button {:>2} value: {}".format(i, button))
            buttons_list.append(button)

            if button == 1:
                print("button pressed: ", i)  # because buttons numbered from 0 in system, but from 1 on remote
        textPrint.unindent()
        #sim.update_buttons(buttons_list)

        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        textPrint.print(screen, "Number of hats: {}".format(hats))
        textPrint.indent()

        for i in range(hats):
            hat = joystick.get_hat(i)
            textPrint.print(screen, "Hat {} value: {}".format(i, str(hat)))
        textPrint.unindent()

        textPrint.unindent()

        textPrint.print(screen, "--------------------------------")
        pose = sim.get_position()

        textPrint.print(screen, "Drone position: [ " + str(pose) + " ]")
        gameLogic.update()


    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # update drone position
    sim.update_loop()

    time_b = time.time()
    delta_time = round((time_b - time_a)*1000)
    if delta_time > 20:
        print ("loop_time: "+str(delta_time) + " ms")

    # Limit to 30 frames per second
    clock.tick(30)



# Close the window and quit.

# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
