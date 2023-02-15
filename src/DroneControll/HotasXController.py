'''

this class maps HOTAS Joystick controller, to functions in drone
note that sensitivity settings is defined here

the drone should get simple movement commands, like :
yaw, forward speed, vertical speed,horizontal speed

'''

'''
Hotas X Controller description:

number of axis = 6
axis 0 - right/left tilt rotation ( left = -1, right = 1)
axis 1 - depth movement ( -1 = up, 1 = down)
axis 2 - left hand speed stick ( up = -1, center = 0, down = 1)
axis 3 - two buttons at the hand of the left stick

Right joystick -
pulling toward -> going up
pushing forward -> going down
turning left -> moving horizontal left
turning right -> moving horizontal right
pushing left -> turning left
pushing right -> turning right

Left joystick -
Pushing forward -> increasing speed
Pulling toward -> decreasing speed & reverse  




'''

class HotasXController:
    drone_controller = None
    joystick_name =  "T.Flight Hotas X"
    speed_activated = False
    vertical_speed_activated = False
    horizontal_speed_activated = False

    def __init__(self,  drone_controller):
        print("hotas X created")
        self.drone_controller = drone_controller

    def update(self, joystick):

        if self.joystick_name != joystick.get_name():
            return

        # deal with axis

        # pass yaw
        value = joystick.get_axis(3)
        if round(value, 1) != 0:
            self.drone_controller.add_rotation(value)

        # pass speed

        stick_depth = -1 * (round(joystick.get_axis(1), 2))
        if round(stick_depth, 1) != 0:
            self.speed_activated = True
            self.drone_controller.set_speed(stick_depth * 7.5)
        else:
            if self.speed_activated:
                self.drone_controller.set_speed(0)
                self.speed_activated = False

        # horizontal movement
        stick_horizontal = (-1 * round(joystick.get_axis(0), 2))
        if round(stick_horizontal, 1) != 0:
            self.drone_controller.set_horizontal_movement(stick_horizontal * 4)
            self.horizontal_speed_activated = True
        else:
            if self.horizontal_speed_activated:
                self.drone_controller.set_horizontal_movement(stick_horizontal * 4)
                self.horizontal_speed_activated = False;


        #vertical speed
        depth_value = (round(joystick.get_axis(2), 2)) * 0.1
        if round(depth_value, 1) != 0:
            self.drone_controller.set_vertical_movement(depth_value)
            self.vertical_speed_activated = True
        else:
            if self.vertical_speed_activated:
                self.drone_controller.set_vertical_movement(0)
                self.vertical_speed_activated = False
