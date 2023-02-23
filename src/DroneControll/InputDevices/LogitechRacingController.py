'''

this class maps red wheel ps3 game controller, to functions in drone
note that sensitivity settings is defined here

the drone should get simple movement commands, like :
yaw, forward speed, vertical speed,horizontal speed

'''

'''
yoke remote description:

number of axis = 6
axis 0 - wheel rotation ( left = negative)

interesting buttons
btn 3 - forward
btn 4 - 



'''


class LogitechRacingController:
    drone_controller = None
    joystick_name = "Logitech Racing Wheel"
    speed = 0
    speed_activated = False
    vertical_speed_activated = False
    horizontal_speed_activated = False

    def __init__(self, drone_controller):
        print("Logitech Racing created")
        self.drone_controller = drone_controller

    def update(self, joystick):

        if self.joystick_name != joystick.get_name():
            return

        # deal with axis

        # pass yaw
        value = joystick.get_axis(0)
        if round(value, 1) != 0:
            self.drone_controller.add_rotation(value)

        # pass speed
        value_speed = joystick.get_axis(1)
        if round(value_speed, 1) != 0:
            self.drone_controller.set_speed(-1 * value_speed * 7.5)
            self.speed_activated = True
        else:
            if self.speed_activated:
                self.speed_activated = False
                self.drone_controller.set_speed(0)

        # deal with buttons
        x, y = joystick.get_hat(0)
        if x != 0:
            self.drone_controller.set_horizontal_movement(x * (-5))
            self.horizontal_speed_activated = True
        else:
            if self.horizontal_speed_activated:
                self.horizontal_speed_activated = False
                self.drone_controller.set_horizontal_movement(0)

        #looks like the left hat should be enabled for up/down too

        btn_up = joystick.get_button(3)
        btn_down = joystick.get_button(1)
        if btn_up == 1:
            self.drone_controller.set_vertical_movement(2)
            self.vertical_speed_activated = True
        if btn_down == 1:
            self.drone_controller.set_vertical_movement(-2)
            self.vertical_speed_activated = True

        if btn_up == 0 and btn_down == 0 and self.vertical_speed_activated:
            self.drone_controller.set_vertical_movement(0)
            self.vertical_speed_activated = False

        #self.drone_controller.set_vertical_movement(btn_up + btn_down)
