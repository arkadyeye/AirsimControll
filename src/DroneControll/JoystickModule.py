import pygame
#import AirSimControllerDualStick as sim
from PathMaker import PathMaker
from AirSimFacade import AirSimFacade
from YokeController import YokeController
from RedWheelController import RedWheelController

from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

yoke_joystick = None
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

plt.ion()
img = plt.imread("../full_map.png")
fig, ax = plt.subplots()
ax.imshow(img)
circle = plt.Circle((300, 300), 10, color='r')
ax.add_patch( circle )



# setting title
plt.title("Geeks For Geeks", fontsize=20)

# setting x-axis label and y-axis label
plt.xlabel("X-axis")
plt.ylabel("Y-axis")

update_counter = 0


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

# Initialize the joysticks
pygame.joystick.init()

# here , check what joystick is connected, and init its class
joystick_count = pygame.joystick.get_count()

# For each joystick:
for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    name = joystick.get_name()

    if name == "TCA YOKE BOEING":
        yoke_joystick = YokeController(sim)

    if name == "PS(R) Gamepad Adaptor":
        red_wheel = RedWheelController(sim)




# Get ready to print
textPrint = TextPrint()


#sim.init()

# -------- Main Program Loop -----------
while done == False:

    update_counter = update_counter +1

    # why the path maker is in the loop !!!!!!!!!!
    path_maker = PathMaker()
    path_maker.start_path(pygame, sim)

    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(darkgrey)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        textPrint.print(screen, "Joystick {}".format(i))
        textPrint.indent()

        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.print(screen, "Joystick name: {}".format(name))

        if name == "TCA YOKE BOEING":
            yoke_joystick.update(joystick)

        if name == "PS(R) Gamepad Adaptor":
            red_wheel.update(joystick)


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

        # circle = plt.Circle((300+pose[0], 300+pose[1]), 10, color='r')
        # ax.add_patch( circle )
        if update_counter%30 == 0:
            # # drawing updated values
            circle.center = 300+pose[0], 300+pose[1]
            fig.canvas.draw()
            fig.canvas.flush_events()

        textPrint.print(screen, "Drone position: [ " + str(pose) + " ]")

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # update drone position
    sim.update_loop()

    # Limit to 30 frames per second
    clock.tick(30)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            break  # breaks the loop so the gui can be closed

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
