'''

this class should interact with air sim,and provide much simplier api to upper classes

'''
import os
import time

import airsim
import math

import json

# const vars of joystick

# logitech chep wheel
UP = 3
DOWN = 1
DRIFT_LEFT = 0
DRIFT_RIGHT = 2
HOVER = 6

#HOTAS STICK
# UP = 14
# DOWN = 16
# DRIFT_LEFT = 15
# DRIFT_RIGHT = 17

# local vars, the state of the drone
drone_speed = 0
drone_speed_coef = 5

vertical_position = 0
vertical_position_coef = 0.05

horizontal_speed = 0
horizontal_speed_coef = 0.5

camera_heading = 0
camera_heading_coef = 1.5
delta_camera_heading = 0

hover_event = False


client = None
image_num = 0
prev_image = None

list_of_path = []
pose_index = 0


def init():
    global client
    client = airsim.MultirotorClient()  # connect to the simulator
    client.confirmConnection()
    client.reset()

    client.simSetTimeOfDay(True, start_datetime="2018-06-06 22:00:00", is_start_datetime_dst=False,
                           celestial_clock_speed=1,
                           update_interval_secs=60, move_sun=True)

    client.enableApiControl(True, vehicle_name="Drone0")  # enable API control on Drone0
    client.armDisarm(True, vehicle_name="Drone0")  # arm Drone0

    client.takeoffAsync(vehicle_name="Drone0").join()  # let Drone0 take-off
    client.moveToPositionAsync(0, 0, -2.5, 1, vehicle_name="Drone0").join()

    client.hoverAsync(vehicle_name="Drone0").join()

    # use this to imidiate move
    # pose = airsim.Pose(airsim.Vector3r(0, 0, -300), airsim.to_quaternion(0, 0, 0))  # PRY in radians
    # client.simSetVehiclePose(pose,True)

    print("AirSim Ready")


def update_rotation(heading):
    global camera_heading
    global delta_camera_heading
    global drone_speed

    new_camera_heading = (camera_heading + heading) % 360

    # if drone_speed >= 0:
    #     new_camera_heading = (camera_heading + heading) % 360
    # else:
    #     new_camera_heading = (camera_heading - heading) % 360

    delta_camera_heading = camera_heading - new_camera_heading
    camera_heading = new_camera_heading


def update_speed(speed):
    global drone_speed
    drone_speed = -speed * drone_speed_coef
    drone_speed = round(drone_speed,1)
    # print("joystick speed", drone_speed)


def update_buttons(buttons_list):
    global vertical_position
    global horizontal_speed
    global hover_event


    # horizontal speed is drifrint left/gright
    if buttons_list[DRIFT_RIGHT] == 1:
        # horizontal_speed = horizontal_speed - horizontal_speed_coef
        # horizontal_speed = min(horizontal_speed, 6)

        horizontal_speed = - horizontal_speed_coef

    if buttons_list[DRIFT_LEFT] == 1:
        # horizontal_speed = horizontal_speed + horizontal_speed_coef
        # horizontal_speed = max(horizontal_speed, -6)

        horizontal_speed = horizontal_speed_coef
    if buttons_list[DRIFT_RIGHT] == 0 and buttons_list[DRIFT_LEFT] == 0:
        horizontal_speed = 0

    # vertical speed is moving up/down
    if buttons_list[UP] == 1:
        vertical_position = vertical_position - vertical_position_coef
    if buttons_list[DOWN] == 1:
        vertical_position = vertical_position + vertical_position_coef

    if buttons_list[HOVER] == 1:
        hover_event = True



    # if buttons_list[0] == 0 and buttons_list[3] == 0:
    #     delta_vertical_speed = 0


def update_drone():
    global vertical_position
    global horizontal_speed
    global camera_heading
    global drone_speed
    global client

    if hover_event:
        client.hoverAsync().join()
        return

    yaw_drone = airsim.to_eularian_angles(client.getMultirotorState().kinematics_estimated.orientation)[2]
    vx = drone_speed * math.cos(yaw_drone) + horizontal_speed * math.sin(yaw_drone)
    vy = drone_speed * math.sin(yaw_drone) + horizontal_speed * -math.cos(yaw_drone)


    high_drone = client.simGetVehiclePose(vehicle_name="Drone0").position.z_val
    if abs(vertical_position - high_drone) < 0.2:
        vertical_position_changed = False

    # round to 2 decimal points
    vx = round(vx, 2)
    vy = round(vy, 2)

    # if vx > 0.1 or vy > 0.1 or delta_camera_heading != 0 or vertical_position_changed:
    client.moveByVelocityZAsync(vx, vy, vertical_position, 1, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                airsim.YawMode(False, camera_heading), vehicle_name="Drone0")

    # if speed > 0:
    #     speed = speed - 0.5  # speed should decrease if not activate
    # if speed < 0:
    #     speed = speed + 0.5  # speed should decrease if not activated


def get_stage():
    return client.getMultirotorState(vehicle_name="Drone0")


def get_position():
    pose = client.simGetVehiclePose(vehicle_name="Drone0")
    x = round(pose.position.x_val, 3)
    y = round(pose.position.y_val, 3)
    z = round(pose.position.z_val, 3)
    yaw = round(math.degrees(airsim.to_eularian_angles(pose.orientation)[2]), 3)
    return x, y, z, yaw


# path
def add_to_path():
    list_of_path.append(get_position())
    print("point added")

def go_to_next_pose():
    z = - 35
    result = client.moveOnPathAsync([airsim.Vector3r(-16,40,z),
                                airsim.Vector3r(-45,40,z),
                                airsim.Vector3r(-51,37,z),
                                airsim.Vector3r(-52,22,z)],
                        5, 120,
                        airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False,0), 20, 1)


def go_to_next_pose_old():
    global pose_index
    global vertical_speed
    global horizontal_speed
    global camera_heading
    global list_of_path

    pose_index = pose_index + 1
    if pose_index >= len(list_of_path):
        pose_index = 0
    pose = list_of_path[pose_index]
    print("pose", pose)

    client.moveToPositionAsync(pose[0], pose[1], pose[2], 10, vehicle_name='Drone0').join()
    client.rotateToYawAsync(pose[3], vehicle_name='Drone0').join()

    vertical_speed = pose[2]
    camera_heading = pose[3]

    client.hoverAsync().join()


def save_path_to_json():
    with open('path.json', 'w', encoding='utf-8') as f:
        json.dump(list_of_path, f, ensure_ascii=False, indent=4)


def load_path_from_json():
    global list_of_path
    with open('path.json') as data_file:
        data_loaded = json.load(data_file)
        print("data_loaded", data_loaded)
        list_of_path = data_loaded

# recording
def start_recording():
    global client
    client.startRecording()


def stop_recording():
    global client
    client.stopRecording()
    # client.armDisarm(False, vehicle_name="Drone0")  # disarm Drone0
    # client.reset()  # reset the simulation
    # client.enableApiControl(False, vehicle_name="Drone0")  # disable API control of Drone0


# experimental
def scan_map(init_x, init_y):
    pose = airsim.Pose(airsim.Vector3r(init_x, init_y, -200), airsim.to_quaternion(0, 0, 0))  # PRY in radians
    client.simSetVehiclePose(pose, True)

    x = init_x
    y = init_y

    while y < 300:
        while x < 434:
            pose = airsim.Pose(airsim.Vector3r(x, y, -200), airsim.to_quaternion(0, 0, 0))  # PRY in radians
            client.simSetVehiclePose(pose, True)
            client.moveByVelocityAsync(0, 0, 0, 0.25, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                       airsim.YawMode(False, camera_heading), vehicle_name="Drone0").join()
            # moveToPoint(x,y)
            # client.hoverAsync(vehicle_name="Drone0").join()
            ans = takeImage(x, y)
            client.moveByVelocityAsync(0, 0, 0, 0.25, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                       airsim.YawMode(False, camera_heading), vehicle_name="Drone0").join()
            # time.sleep(0.1)
            if ans:
                x = x + 20
        y = y + 20
        x = init_x


def moveToPoint(x, y):
    inner_speed = 1
    inner_z = -200
    client.moveToPositionAsync(x, y, inner_z, inner_speed).join()


from PIL import ImageChops
from PIL import Image
import numpy as np


def takeImage(x, y):
    global image_num
    global prev_image
    image_num = image_num + 1
    responses = client.simGetImages([airsim.ImageRequest("bottom_center", airsim.ImageType.Scene, False, False)])
    response = responses[0]

    img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
    img_rgb = img1d.reshape(response.height, response.width, 3)
    # img_rgb = np.flipud(img_rgb)
    img1 = Image.fromarray(img_rgb, 'RGB')

    #
    # if prev_image != None:
    #     diff = ImageChops.difference(img1, prev_image)
    #     diff.save("pics/diff_Drone0_" + str(image_num) + "_" + str(x) + "_" + str(y) + ".png")
    #     print ("diff",diff.getbbox())
    #
    # if prev_image == response:
    #     return False

    # f = open("pics/Drone0_" + str(image_num) + "_" + str(x) + "_" + str(y) + ".png", "wb")
    # f.write(img1)  # save the image as a PNG file
    # f.close()

    airsim.write_png(os.path.normpath("pics/Drone0_" + str(image_num) + "_" + str(x) + "_" + str(y) + '.png'), img_rgb)

    prev_image = img1
    return True
