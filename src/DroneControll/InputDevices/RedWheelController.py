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


class RedWheelController:
    drone_controller = None


    def __init__(self, drone_controller):
        print("Red Wheel created")
        self.drone_controller = drone_controller

    def update(self, joystick):

        # deal with axis

        # pass yaw
        value = joystick.get_axis(0)
        self.drone_controller.add_rotation(value)

        # deal with buttons

        # pass speed
        btn_speed_up = joystick.get_button(2)
        btn_speed_down = -1 * joystick.get_button(3)

        speed = 0.25 * (btn_speed_up + btn_speed_down)
        self.drone_controller.add_speed(speed)

        # horizontal movement
        btn_left = joystick.get_button(15)
        btn_right = -1 * joystick.get_button(13)
        self.drone_controller.set_horizontal_movement((btn_left + btn_right) * 5)

        # vertical movement
        btn_up = joystick.get_button(12)
        btn_down = joystick.get_button(14)
        if btn_up == 1:
            self.drone_controller.set_vertical_movement(1)
        if btn_down == 1:
            self.drone_controller.set_vertical_movement(-1)

        if btn_up == 0 and btn_down == 0:
            self.drone_controller.set_vertical_movement(0)

        # self.drone_controller.set_vertical_movement(btn_up+btn_down)

