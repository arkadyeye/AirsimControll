import pygame
import AirSimControllerDualStick as sim

# Define some colors
darkgrey = (40, 40, 40)
lightgrey = (150, 150, 150)


# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
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

# Initialize the joysticks
pygame.joystick.init()

# Get ready to print
textPrint = TextPrint()

# init airsim
sim.init()

# -------- Main Program Loop -----------
while done == False:

    #------------ TODO 19:41 27.11 -------------
    #   https://github.com/microsoft/AirSim/issues/3348
    #   simPlotStrings(strings, positions, scale=5, color_rgba=[1.0, 0.0, 0.0, 1.0], duration=-1.0)
    #   https://github.com/microsoft/AirSim/blob/main/PythonClient/environment/plot_markers.py
    #   https://microsoft.github.io/AirSim/api_docs/html/#airsim.client.VehicleClient.simPlotStrings
    #      Psuedo Code Functions:
    #      filterCollision :
    #               var temp
    #               general_count = 0 // Counting the collisions amount
    #               count_same = 0 // Counting the amount of the collision of the same objects
    #               temp = vehicle_name // temp is the same as the next collided vehicle
    #               if temp == vehicle_name
    #                       count_same = count_same + 1
    #                       // change the value 2 to the amount you want to hit the same object
    #                       if count_same == 2 --> general_count = general_count + 1
    #               else temp = vehicle_name            // make temp as the new vehicle_name
    #                           general_count = count + 1       // increment general_count
    #
    #
    #       GameOver function idea :
    #       if general_count == X collisions -> use plot.py in the plot_markers.py above to draw Game Over
    #                                                  & the drone has to fall to the ground + if can make the screen
    #                                                               blurry it will be awesome
    #--------------------------------------------
    # EVENT PROCESSING STEP
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

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

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.print(screen, "Number of axes: {}".format(axes))
        textPrint.indent()

        for i in range(axes):
            axis = joystick.get_axis(i)
            if i == 0:  # means X
                sim.update_rotation(axis)
            if i == 1: # means Y
                sim.update_speed(axis)
            if i == 2:
                sim.update_horizontal_speed(axis)
            if i == 3:
                sim.update_vertical_speed(axis)

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
        sim.update_buttons(buttons_list)

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

    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # update drone position
    sim.update_drone()

    # Limit to 30 frames per second
    clock.tick(30)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
