'''

this class maps yoke boeng game controller, to functions in drone
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




'''

class HotasXController:
    drone_controller = None

    def __init__(self,  drone_controller):
        print("hotas X created")
        self.drone_controller = drone_controller

    def update(self, joystick):

        # deal with axis

        # pass yaw
        value = joystick.get_axis(3)
        self.drone_controller.add_rotation(value)

        # pass speed
        left_bar_value = (-1 * round(joystick.get_axis(2), 2))
        # depth_value = (-1 * round(joystick.get_axis(1), 2)) + 1
        # speed = left_bar_value * depth_value
        # self.drone_controller.set_speed(speed)

        self.drone_controller.set_speed(left_bar_value*5)

        # deal with buttons

        # horizontal movement
        btn_left = -1 * joystick.get_axis(0)
        btn_right = joystick.get_axis(0)
        self.drone_controller.set_horizontal_movement((btn_left + btn_right)*5)

        # vertical movement
        # btn_up = joystick.get_button(2) # btn x - up
        # btn_down = joystick.get_button(3)  # btn x - down
        # if btn_up == 1:
        #     self.drone_controller.set_vertical_movement(1)
        # if btn_down == 1:
        #     self.drone_controller.set_vertical_movement(-1)
        #
        # if btn_up == 0 and btn_down == 0:
        #     self.drone_controller.set_vertical_movement(0)

        # self.drone_controller.set_vertical_movement(btn_up+btn_down)

        depth_value = (round(joystick.get_axis(1), 2))*0.1
        self.drone_controller.set_vertical_movement(depth_value)

        '''
        idea by Oded L.M
        make axis 3 and 5 (down bars) for gimble
        make the speed acomulative by button/mini joystick
        '''

