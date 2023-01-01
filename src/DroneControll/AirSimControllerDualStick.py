'''

this class should interact with air sim,and provide much simplier api to upper classes

'''
import os
import random
import time

import airsim
import math

import json

debug_mode = True

# local vars, the state of the drone
drone_speed = 0
drone_speed_coef = 5

vertical_position = 0
vertical_position_coef = 0.05

horizontal_speed = 0
horizontal_speed_coef = 0.9

camera_heading = 180
camera_heading_coef = 3.5
delta_camera_heading = 0

client = None
image_num = 0
prev_image = None

list_of_path = []
list_of_vectors = []
list_of_vectors_noised = []
pose_index = 0

automatic_mode = False
target_on_path = None
EPSILON = 1
target_on_path_index = 0

movement_noise = 0.5


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
    client.rotateToYawAsync(180, vehicle_name="Drone0").join()
    client.simSetTraceLine([0.0, 1.0, 0.0, 0.8], 10, vehicle_name="Drone0")

    # client.enableApiControl(True, vehicle_name="Drone1")  # enable API control on Drone0
    # client.armDisarm(True, vehicle_name="Drone1")  # arm Drone0
    #
    # client.takeoffAsync(vehicle_name="Drone1").join()  # let Drone0 take-off
    # # client.moveToPositionAsync(0, 0, -4.5, 1, vehicle_name="Drone1").join()
    # client.hoverAsync(vehicle_name="Drone1").join()

    # use this to imidiate move
    # pose = airsim.Pose(airsim.Vector3r(0, 0, -300), airsim.to_quaternion(0, 0, 0))  # PRY in radians
    # client.simSetVehiclePose(pose,True)

    print("AirSim Ready")


def update_rotation(heading):
    global camera_heading
    global delta_camera_heading
    global drone_speed

    new_camera_heading = (camera_heading + heading * camera_heading_coef) % 360

    # if drone_speed >= 0:
    #     new_camera_heading = (camera_heading + heading) % 360
    # else:
    #     new_camera_heading = (camera_heading - heading) % 360

    delta_camera_heading = camera_heading - new_camera_heading
    camera_heading = new_camera_heading


def update_speed(speed):
    global drone_speed
    drone_speed = -speed * drone_speed_coef
    drone_speed = round(drone_speed, 1)
    # print("joystick speed", drone_speed)


def update_vertical_speed(speed):
    pass
    # global vertical_position
    # vertical_position = vertical_position + (speed * drone_speed_coef)
    # vertical_position = round(vertical_position,1)
    # print("joystick speed", drone_speed)


def update_horizontal_speed(speed):
    global horizontal_speed
    horizontal_speed = -speed * drone_speed_coef
    horizontal_speed = round(horizontal_speed, 1)
    # print("joystick speed", drone_speed)


def update_buttons(buttons_list):
    global vertical_position
    global horizontal_speed

    # # horizontal speed is drifrint left/gright
    # if buttons_list[15] == 1:
    #     horizontal_speed = horizontal_speed - horizontal_speed_coef
    #     horizontal_speed = min(horizontal_speed, 6)
    # if buttons_list[17] == 1:
    #     horizontal_speed = horizontal_speed + horizontal_speed_coef
    #     horizontal_speed = max(horizontal_speed, -6)
    # if buttons_list[15] == 0 and buttons_list[17] == 0:
    #     horizontal_speed = 0
    #
    # if buttons_list[15] == 1:
    #     horizontal_speed = horizontal_speed - horizontal_speed_coef
    #     horizontal_speed = min(horizontal_speed, 6)
    # if buttons_list[17] == 1:
    #     horizontal_speed = horizontal_speed + horizontal_speed_coef
    #     horizontal_speed = max(horizontal_speed, -6)
    # if buttons_list[15] == 0 and buttons_list[17] == 0:
    #     horizontal_speed = 0
    #
    # # vertical speed is moving up/down
    if buttons_list[3] == 1:
        vertical_position = vertical_position - vertical_position_coef
    if buttons_list[1] == 1:
        vertical_position = vertical_position + vertical_position_coef
    # if buttons_list[0] == 0 and buttons_list[3] == 0:
    #     delta_vertical_speed = 0


def abort_automation():
    global vertical_position
    global automatic_mode
    global camera_heading

    pose = client.simGetVehiclePose(vehicle_name="Drone0")
    camera_heading = round(math.degrees(airsim.to_eularian_angles(pose.orientation)[2]), 3)

    vertical_position = round(pose.position.z_val, 3)

    # client.rotateToYawAsync(yaw, vehicle_name="Drone0").join()

    client.hoverAsync().join()
    client.moveByVelocityZAsync(0, 0, vertical_position, 2, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                airsim.YawMode(False, camera_heading), vehicle_name="Drone0").join()
    automatic_mode = False


def update_drone():
    global client

    # not sure that this function call should be here
    # but it's like in a big update loop
    update_visible_path()

    # skip drone update on automatic motion
    global automatic_mode
    global target_on_path_index
    global target_on_path

    # we should always track location on path. both in hand and automated mode

    if automatic_mode:
        return

    global vertical_position
    global horizontal_speed
    global camera_heading
    global drone_speed

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


def update_visible_path():
    global target_on_path_index
    global target_on_path

    if len(list_of_vectors) == 0:
        return

    # track our movement on path

    pose = client.simGetVehiclePose(vehicle_name="Drone0")
    dist = pose.position.distance_to(target_on_path)

    # print(target_on_path.x_val)
    if dist < EPSILON and target_on_path_index + 1 < len(list_of_vectors):
        target_on_path_index = target_on_path_index + 1
        target_on_path = list_of_vectors[target_on_path_index]

    # print("dist to target:", dist)

    sublist_of_vectors = list_of_vectors[target_on_path_index:]
    sublist_of_vectors_noised = list_of_vectors_noised[target_on_path_index:]
    client.simPlotPoints(points=sublist_of_vectors,
                         color_rgba=[1.0, 0.0, 0.0, 1.0], size=25, duration=0.5, is_persistent=False)

    client.simPlotLineStrip(
        points=sublist_of_vectors,
        color_rgba=[1.0, 1.0, 0.0, 1.0], thickness=5, duration=0.5, is_persistent=False)

    if debug_mode:
        client.simPlotPoints(points=sublist_of_vectors_noised,
                             color_rgba=[0.0, 0.0, 1.0, 1.0], size=25, duration=0.1, is_persistent=False)

        client.simPlotLineStrip(
            points=sublist_of_vectors_noised,
            color_rgba=[0.0, 0.0, 1.0, 0.0], thickness=5, duration=0.1, is_persistent=False)


def get_stage():
    return client.getMultirotorState(vehicle_name="Drone0")


# def get_position():
#     pose = client.simGetVehiclePose(vehicle_name="Drone0")
#     x = round(pose.position.x_val, 3)
#     y = round(pose.position.y_val, 3)
#     z = round(pose.position.z_val, 3)
#     yaw = round(math.degrees(airsim.to_eularian_angles(pose.orientation)[2]), 3)
#     return x, y, z, yaw


# def get_position_vector():
#     pose = client.simGetVehiclePose(vehicle_name="Drone0")
#     x = round(pose.position.x_val, 3)
#     y = round(pose.position.y_val, 3)
#     z = round(pose.position.z_val, 3)
#     return airsim.Vector3r(x, y, z)


# path
# def add_to_path():
#     list_of_path.append(get_position())
#     list_of_vectors.append(get_position_vector())
#
#     # this will deleta trace - not good
#     # client.simFlushPersistentMarkers()
#
#     client.simPlotPoints(points=list_of_vectors,
#                          color_rgba=[1.0, 0.0, 0.0, 0.2], size=25, duration=1000, is_persistent=False)
#
#     client.simPlotLineStrip(
#         points=list_of_vectors,
#         color_rgba=[1.0, 1.0, 0.0, 0.02], thickness=5, duration=300.0, is_persistent=False)
#
#     print("point added")


def go_to_next_pose():
    print("p is pressed")
    global automatic_mode
    global target_on_path
    global target_on_path_index
    automatic_mode = True
    v_name = 'Drone0'

    # z = -4
    # result = client.moveOnPathAsync([airsim.Vector3r(0,0,z),
    #                             airsim.Vector3r(0.315,0.354,z),
    #                             airsim.Vector3r(-13,0,z),
    #                             airsim.Vector3r(-16,0,z)],
    #                                 1, 120,
    #                                 airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False, 0), 20, 1).join()
    sublist_of_vectors = list_of_vectors_noised[target_on_path_index:]

    target_on_path = sublist_of_vectors[0]
    result = client.moveOnPathAsync(sublist_of_vectors, 2, 120,
                                    airsim.DrivetrainType.ForwardOnly, airsim.YawMode(False, 0), -1, 1,
                                    vehicle_name=v_name)

    print(" p is finished")


def go_to_next_pose_old():
    print("p is pressed")
    global automatic_mode
    automatic_mode = True

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


# def save_path_to_json():
#     with open('movePath.json', 'w', encoding='utf-8') as f:
#         json.dump(list_of_path, f, ensure_ascii=False, indent=4)





def load_path_from_json():
    global list_of_path
    global list_of_vectors
    global list_of_vectors_noised
    global target_on_path
    with open('movePath.json') as data_file:
        data_loaded = json.load(data_file)
        print("data_loaded", data_loaded)
        list_of_path = data_loaded

    for i in range(len(list_of_path)):
        list_of_vectors.append(airsim.Vector3r(list_of_path[i][0], list_of_path[i][1], list_of_path[i][2]))
        list_of_vectors_noised.append(airsim.Vector3r(
            list_of_path[i][0] + round(random.uniform(-movement_noise, movement_noise), 3),
            list_of_path[i][1] + round(random.uniform(-movement_noise, movement_noise), 3),
            list_of_path[i][2] + round(random.uniform(-movement_noise, movement_noise), 3),
        ))

    # clean and redraw path
    client.simFlushPersistentMarkers()
    target_on_path = list_of_vectors[0]
    update_visible_path()


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
