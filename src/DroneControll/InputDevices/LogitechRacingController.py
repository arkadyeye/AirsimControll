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
    csv_name = "b_wheel"
    speed = 0
    speed_activated = False
    vertical_speed_activated = False
    horizontal_speed_activated = False

    def __init__(self, drone_controller):
        print("Logitech Racing created")
        self.drone_controller = drone_controller

    def getCsvHeader(self):
        # logitec dual stick joystik has 4 axis, 12 buttons, and one hat
        # so it means 18 places
        return "name,yaw,speed,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,btn,hat_x,hat_y"


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

        #check for fast mode
        btn_fast = joystick.get_button(3)

        horizontal_value = 0
        # deal with axis

        # pass yaw
        value = joystick.get_axis(0)
        if round(value, 1) != 0:
            self.drone_controller.add_rotation(value)

        # pass speed
        value_speed = joystick.get_axis(1)
        
        if btn_fast == 1:
            value_speed = value_speed * 2
        
        if round(value_speed, 1) != 0:
            self.drone_controller.set_speed(-1 * value_speed * 7.5)
            self.speed_activated = True           
            
        else:
            if self.speed_activated:
                self.speed_activated = False
                self.drone_controller.set_speed(0)

        # add drift for turning
        if round(value_speed, 1) != 0 and round(value, 1) != 0:
            horizontal_value = 7.5 *value * value_speed

        # deal with buttons
        x, y = joystick.get_hat(0)
        if x != 0 or horizontal_value != 0:
            horizontal_value = horizontal_value + x * (-4)
            
            self.drone_controller.set_horizontal_movement(horizontal_value)
            
            self.horizontal_speed_activated = True
        else:
            if self.horizontal_speed_activated:
                self.horizontal_speed_activated = False
                self.drone_controller.set_horizontal_movement(0)

        if y != 0:
            self.drone_controller.set_vertical_movement(y * 5)
            self.vertical_speed_activated = True
        else:
            if self.vertical_speed_activated:
                self.vertical_speed_activated = False
                self.drone_controller.set_vertical_movement(0)
                

        #looks like the left hat should be enabled for up/down too

        # btn_up = joystick.get_button(3)
        # btn_down = joystick.get_button(1)
        # if btn_up == 1:
        #     self.drone_controller.set_vertical_movement(2)
        #     self.vertical_speed_activated = True
        # if btn_down == 1:
        #     self.drone_controller.set_vertical_movement(-2)
        #     self.vertical_speed_activated = True
        #
        # if btn_up == 0 and btn_down == 0 and self.vertical_speed_activated:
        #     self.drone_controller.set_vertical_movement(0)
        #     self.vertical_speed_activated = False

        #self.drone_controller.set_vertical_movement(btn_up + btn_down)
