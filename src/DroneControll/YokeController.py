'''

this class maps yoke boeng game controller, to functions in drone
note that sensitivity settings is defined here

the drone should get simple movement commands, like :
yaw, forward speed, vertical speed,horizontal speed

'''

'''
yoke remote description:

number of axis = 6
axis 0 - wheel rotation ( left = negative)
axis 1 - wheel depth movement ( deep = forward = negative)
axis 2 - center right bar ( up = negative, center = 0)
axis 3 - right hand mini joystick horizontal (left = negative)
axis 4 - right hand mini joystick vertical (down = negative)
axis 5 - center left bar ( up = negative, center = 0)

interesting buttons
right hand:
triger = 11
but_A = left = 6, right = 7
but_B = left = 8, right = 9
but = 10

left hand
triger = 0
but_X = up = 2, down = 3
but_Y = up = 4, down = 5
but = 1
hat - TDB

menu buttons = 13,14,15
but_xbox = 16

right hand switch = 17 (up = 1)




'''

class YokeController:
    drone_controller = None

    def __init__(self,  drone_controller):
        print ("yoke created")
        self.drone_controller = drone_controller

    def update(self,joystick):

        # deal with axis

        # pass yaw
        value = joystick.get_axis(0)
        self.drone_controller.add_rotation(value)

        # pass speed
        left_bar_value = (-1 * round(joystick.get_axis(5),2))
        # depth_value = (-1 * round(joystick.get_axis(1), 2)) + 1
        # speed = left_bar_value * depth_value
        # self.drone_controller.set_speed(speed)

        self.drone_controller.set_speed(left_bar_value*5)

        # deal with buttons

        # horizontal movement
        btn_left = joystick.get_button(6)
        btn_right = -1* joystick.get_button(7)
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

