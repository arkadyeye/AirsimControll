'''

this class maps Logitech dual action (dual stick) Joystick controller, to functions in drone


the drone should get simple movement commands, like :
yaw, forward speed, vertical speed,horizontal speed

'''

'''
Hotas X Controller description:

number of axis = 4
axis 0 - left stick : left/right (-1 = left, 1 = right)
axis 1 - left stick : up/down (up = -1, down = 1)
axis 2 - rith stick: left/right (-1 = left, 1 = right)
axis 3 - left stick : up/down (up = -1, down = 1)


'''


class LogitechDualAction:
    drone_controller = None
    joystick_name = "Logitech Dual Action"
    csv_name = "d_stick"
    speed_activated = False
    vertical_speed_activated = False
    horizontal_speed_activated = False

    def __init__(self,  drone_controller):
        self.btn_add_poit_activated = False
        print("Logitech dual action created")
        self.drone_controller = drone_controller



    def getCsvHeader(self):
        # logitec dual stick joystik has 4 axis, 12 buttons, and one hat
        # so it means 18 places
        return "d_stick,yaw,v_speed,h_speed,speed,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,hat_x,hat_y"

    def getCsvState(self, joystick):
        ans = self.csv_name
        axes = joystick.get_numaxes()

        for i in range(axes):
            axis = joystick.get_axis(i)
            ans = ans + ","+str(round(axis, 3))

        buttons = joystick.get_numbuttons()
        for i in range(buttons):
            button = joystick.get_button(i)
            ans = ans + "," + str(button)

        hats = joystick.get_numhats()
        for i in range(hats):
            hat = joystick.get_hat(i)
            ans = ans + "," + str(hat[0])
            ans = ans + "," + str(hat[1])

        return ans


    def update(self, joystick):

        if self.joystick_name != joystick.get_name():
            return

        # deal with axis

        # pass yaw
        value = joystick.get_axis(0)
        if round(value, 1) != 0:
            self.drone_controller.add_rotation(value)

        # pass speed
        stick_depth = -1 * (round(joystick.get_axis(3), 2))
        if round(stick_depth, 1) != 0:
            self.speed_activated = True
            self.drone_controller.set_speed(stick_depth * 7.5)
        else:
            if self.speed_activated:
                self.drone_controller.set_speed(0)
                self.speed_activated = False

        # horizontal movement
        stick_horizontal = (-1 * round(joystick.get_axis(2), 2))
        if round(stick_horizontal, 1) != 0:
            self.drone_controller.set_horizontal_movement(stick_horizontal * 5)
            self.horizontal_speed_activated = True
        else:
            if self.horizontal_speed_activated:
                self.drone_controller.set_horizontal_movement(stick_horizontal * 5)
                self.horizontal_speed_activated = False;


        # vertical speed
        depth_value = -1 * (round(joystick.get_axis(1), 2)) * 0.1
        if round(depth_value, 1) != 0:
            self.drone_controller.set_vertical_movement(depth_value)
            self.vertical_speed_activated = True
        else:
            if self.vertical_speed_activated:
                self.drone_controller.set_vertical_movement(0)
                self.vertical_speed_activated = False

        # check if btn 7 pressed. used to build a new path
        btn_add_poit = joystick.get_button(6)
        if btn_add_poit == 1:
            if not self.btn_add_poit_activated:
                self.btn_add_poit_activated = True
                self.drone_controller.add_position_to_path()
        else:
            self.btn_add_poit_activated = False

