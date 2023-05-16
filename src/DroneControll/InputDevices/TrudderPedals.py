'''

this class maps Logitech dual action (dual stick) Joystick controller, to functions in drone


the drone should get simple movement commands, like :
yaw, forward speed, vertical speed,horizontal speed

'''

'''
Hotas X Controller description:

number of axis = 3
axis 0 - left stick : left/right (-1 = left, 1 = right)
axis 1 - left stick : up/down (up = -1, down = 1)
axis 2 - rith stick: left/right (-1 = left, 1 = right)



'''


class TrudderPedals:
    drone_controller = None
    joystick_name = "T-Rudder"
    csv_name = "rudder_pedals"
    speed_activated = False
    vertical_speed_activated = False
    horizontal_speed_activated = False

    def __init__(self,  drone_controller):
        self.btn_add_poit_activated = False
        print("T-Rudder created")
        self.drone_controller = drone_controller

    def getCsvHeader(self):
        # logitec dual stick joystik has 4 axis, 12 buttons, and one hat
        # so it means 18 places
        return "rudder_pedals,gas,break,angle"

    def getCsvState(self, joystick):
        ans = self.csv_name
        axes = joystick.get_numaxes()

        for i in range(axes):
            axis = joystick.get_axis(i)
            ans = ans + ","+str(round(axis, 3))

        return ans

    def update(self, joystick):

        if self.joystick_name != joystick.get_name():
            return

        # deal with axis

        # pass speed
        right_pedal = 1 + (-1 * (round(joystick.get_axis(0), 2)))

        left_pedal = 1 + (-1 * (round(joystick.get_axis(1), 2)))

        if round(right_pedal, 1) != 0 or round(left_pedal, 1) != 0:
            self.speed_activated = True
            self.drone_controller.set_speed((right_pedal-left_pedal) * 3.75) #7.5/2
        else:
            if self.speed_activated:
                self.drone_controller.set_speed(0)
                self.speed_activated = False
