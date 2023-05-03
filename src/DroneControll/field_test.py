import airsim
import math
import random
import time
import easygui
from datetime import datetime
from pynput import keyboard

from pynput import keyboard
from pynput.keyboard import Key

from pathlib import Path

csv_file = None
folder_name = None

in_exp = False

# current keys activated
current = set()

bar_orientation = 0
box_orientation = 0

take_counter = 0
max_take_counter = 20

def move_bar(bar_orientation_deg):
    pose = client.simGetObjectPose('Sphere_23')
   
    q = airsim.to_quaternion(0, math.radians(bar_orientation), 0)  # pitch,roll,yaw
    pose.orientation = q

    isMoved = client.simSetObjectPose('Sphere_23',pose)
    print(" moved:", isMoved)
    
    
def init_position():
    global box_orientation
    global bar_orientation
    # rotate teh box
    box_orientation = 0;
    rnd = random.randint(15, 20)
    rnd_sign = random.randint(0, 1)
    print("random number is:",rnd)
    print("random sign is:",rnd_sign)
    box_orientation = rnd
    if rnd_sign == 0:
        box_orientation = -1 * box_orientation

    pose = client.simGetObjectPose('Cube3_20')
    q = airsim.to_quaternion(math.radians(0), math.radians(box_orientation), math.radians(0))  # pitch,roll,yaw
    pose.orientation = q

    isMoved = client.simSetObjectPose('Cube3_20',pose)
    print("Box moved:", isMoved)


    rnd = random.randint(15, 20)
    rnd_sign = random.randint(0, 1)
    print("random number is:",rnd)
    print("random sign is:",rnd_sign)
    bar_orientation = rnd
    if rnd_sign == 0:
        bar_orientation = -1 * bar_orientation
    move_bar(rnd)

# keys listener
def on_press(key):
    global current
    global bar_orientation
    global csv_file
    global folder_name
    global take_counter
    global max_take_counter
    global in_exp

    try:
        key = key.char  # single-char keys
    except:
        key = key.name  # other keys

    print ("key",key)
    
    
    if key == 'q':
        listener.stop()
        
        client.armDisarm(False, vehicle_name="Drone0")  # disarm Drone0
        client.reset()  # reset the simulation
        client.enableApiControl(False, vehicle_name="Drone0")  # disable API control of Drone0
        
    if key == 'left':
        bar_orientation = bar_orientation - 1
        move_bar(bar_orientation)
        print ("bar position",bar_orientation)
        if in_exp:
            csv_file.write(str(round(time.time()*1000))+",left,"+str(bar_orientation)+",\n")
       
    if key == 'right':
        bar_orientation = bar_orientation + 1
        move_bar(bar_orientation)
        print ("bar position",bar_orientation)
        if in_exp:
            csv_file.write(str(round(time.time()*1000))+",right,"+str(bar_orientation)+",\n")
        
    if key == 'n':
        if csv_file is not None:
            csv_file.close()
            
        user_name = easygui.enterbox("Enter is your ID", "New Experiment setup")
        folder_name = "Results//" + user_name + "_" +"{:%Y_%m_%d_%H_%M_%S}".format(datetime.now())
        path = Path(folder_name)
        path.mkdir(parents=True, exist_ok=True)
        print("Directory '%s' created" % folder_name)
        
        take_counter = 0
        
        csv_file = open(folder_name + '//fieldTest_'+str(round(time.time()*1000))+'.csv', 'w')
        init_position()
        csv_file.write("init position,"+str(box_orientation)+","+str(bar_orientation)+",\n")
        
        in_exp = True
        
        
    if key == 'space':
        #space for new data
        init_position()
        
        if not in_exp:
            return
    
        if csv_file is not None:
            csv_file.close()
            take_counter = take_counter + 1
        
        if take_counter < max_take_counter :
            if folder_name is not None:
                csv_file = open(folder_name + '//fieldTest_'+str(round(time.time()*1000))+'.csv', 'w')
            
            if csv_file is not None:
                csv_file.write("init position,"+str(box_orientation)+","+str(bar_orientation)+",\n")
        else:
            easygui.msgbox("Thank you for your time \nPlease advice to next station", "Task completed")
            csv_file.close()
            csv_file = None
            take_counter = 0
            in_exp = False
            
        
                

    current.add(key)
    # if key == keyboard.Key.esc:




def on_release(key):
    try:
        key = key.char  # single-char keys
    except:
        key = key.name  # other keys

    try:
        current.remove(key)
    except KeyError:
        pass


# init airsim and drones
client = airsim.MultirotorClient()  # connect to the simulator
client.confirmConnection()
client.reset()


init_position()
#csv_file = open('fieldTest_'+str(round(time.time()*1000))+'.csv', 'w')
#csv_file.write("init position,"+str(box_orientation)+","+str(bar_orientation)+",\n")



print ("Ready")
'''
# init update timer
rt = RepeatedTimer.RepeatedTimer(timer_duration_sec, on_timer_tick)
camera_timer = RepeatedTimer.RepeatedTimer(0.1, on_frame_tick)
'''

# init key listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# tear down

