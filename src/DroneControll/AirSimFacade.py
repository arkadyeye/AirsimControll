'''

this class make an interface to airsim api, and manages drone position
also, some game logic can be here

'''
import airsim
import math


class AirSimFacade:
    client = None
    drone_name = "Drone0"
    automatic_mode = False
    air_sim = airsim

    # local vars, the state of the drone
    drone_speed = 0
    vertical_position = 0
    horizontal_speed = 0

    camera_heading = 180

    prev_collision_id = None
    prev_collision_name = None
    collision_counter = 0

    def __init__(self, drone_name):
        self.path_api = None
        self.drone_name = drone_name
        self.client = self.air_sim.MultirotorClient()  # connect to the simulator
        self.client.confirmConnection()
        self.client.reset()

        self.client.enableApiControl(True, vehicle_name=self.drone_name)  # enable API control on Drone0
        self.client.armDisarm(True, vehicle_name=self.drone_name)  # arm Drone0

        self.client.takeoffAsync(vehicle_name=self.drone_name).join()  # let Drone0 take-off

        # client.moveToPositionAsync(0, 0, -2.5, 1, vehicle_name=self.drone_name).join()
        # client.rotateToYawAsync(180,vehicle_name=self.drone_name).join()
        # client.simSetTraceLine([0.0, 1.0, 0.0, 0.8], 10,vehicle_name=self.drone_name)

        print("AirSim Ready")

    # path api. add curent position to path
    def add_path_api(self, path_api):
        self.path_api = path_api

    def add_position_to_path(self):
        self.path_api.add_position_to_path(self.get_position())



    # ########## up to here
    def add_rotation(self, heading):
        self.camera_heading = (self.camera_heading + heading) % 360

    def set_speed(self, speed):
        self.drone_speed = speed
        self.drone_speed = round(self.drone_speed, 1)

    def add_speed(self, speed):
        self.drone_speed += speed
        self.drone_speed = round(self.drone_speed, 1)

    def set_horizontal_movement(self, speed):
        self.horizontal_speed = round(speed, 1)

    def set_vertical_movement(self, vertical_increment):
        if vertical_increment == 0:
            # set desired position to current position
            pose = self.client.simGetVehiclePose(vehicle_name=self.drone_name)
            self.vertical_position = round(pose.position.z_val, 3)
        else:
            self.vertical_position = self.vertical_position - vertical_increment

        if self.vertical_position < -30:
            self.vertical_position = -30
        if self.vertical_position > 1:
            self.vertical_position = 1

    def land(self):

        self.automatic_mode = True

        self.drone_speed = 0
        self.vertical_position = 0
        self.horizontal_speed = 0

        #self.client.moveByVelocityZAsync(0, 0, 0, 1,
        #                                 self.air_sim.DrivetrainType.MaxDegreeOfFreedom,
        #                                 self.air_sim.YawMode(False, self.camera_heading), vehicle_name=self.drone_name).join()

        #self.client.landAsync().join()
        self.client.reset()

        self.client.enableApiControl(True, vehicle_name=self.drone_name)  # enable API control on Drone0
        self.client.armDisarm(True, vehicle_name=self.drone_name)  # arm Drone0

        self.client.takeoffAsync(vehicle_name=self.drone_name).join()  # let Drone0 take-off

    def restart_training(self):

        self.collision_counter = 0
        self.prev_collision_name = None

        pose_drone = self.client.simGetVehiclePose(vehicle_name=self.drone_name)
        yaw = self.air_sim.to_eularian_angles(pose_drone.orientation)[2]

        print("drone yaw ", yaw)
        pose = airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0, 0, 0))  # PRY in radians
        self.client.simSetVehiclePose(pose, True)
        self.camera_heading = 180
        self.client.rotateToYawAsync(180, vehicle_name=self.drone_name).join()
        self.automatic_mode = False

    def update_loop(self):


        # we should always track location on path. both in hand and automated mode

        if self.automatic_mode:
            return



        yaw_drone = self.air_sim.to_eularian_angles(self.client.getMultirotorState().kinematics_estimated.orientation)[
            2]
        vx = self.drone_speed * math.cos(yaw_drone) + self.horizontal_speed * math.sin(yaw_drone)
        vy = self.drone_speed * math.sin(yaw_drone) + self.horizontal_speed * -math.cos(yaw_drone)


        #print ("yaw drone: ",math.degrees(yaw_drone))
        #print ("camera heading",self.camera_heading)

        # high_drone = client.simGetVehiclePose(vehicle_name="Drone0").position.z_val
        # if abs(vertical_position - high_drone) < 0.2:
        #    vertical_position_changed = False

        # round to 2 decimal points
        vx = round(vx, 2)
        vy = round(vy, 2)

        # if vx > 0.1 or vy > 0.1 or delta_camera_heading != 0 or vertical_position_changed:
        self.client.moveByVelocityZAsync(vx, vy, self.vertical_position, 1,
                                         self.air_sim.DrivetrainType.MaxDegreeOfFreedom,
                                         self.air_sim.YawMode(False, self.camera_heading), vehicle_name=self.drone_name)

        # if speed > 0:
        #     speed = speed - 0.5  # speed should decrease if not activate
        # if speed < 0:
        #     speed = speed + 0.5  # speed should decrease if not activated

    def get_raw_position(self):
        return self.client.simGetVehiclePose(vehicle_name=self.drone_name)

    def get_position(self):
        pose = self.client.simGetVehiclePose(vehicle_name=self.drone_name)
        x = round(pose.position.x_val, 3)
        y = round(pose.position.y_val, 3)
        z = round(pose.position.z_val, 3)
        yaw = round(math.degrees(self.air_sim.to_eularian_angles(pose.orientation)[2]), 3)
        return x, y, z, yaw

    def get_position_by_pose(self, pose):
        x = round(pose.position.x_val, 3)
        y = round(pose.position.y_val, 3)
        z = round(pose.position.z_val, 3)
        yaw = round(math.degrees(self.air_sim.to_eularian_angles(pose.orientation)[2]), 3)
        return x, y, z, yaw

    def get_position_vector(self):
        pose = self.client.simGetVehiclePose(vehicle_name="Drone0")
        x = round(pose.position.x_val, 3)
        y = round(pose.position.y_val, 3)
        z = round(pose.position.z_val, 3)
        return self.air_sim.Vector3r(x, y, z)

    def get_colisons_counter(self):
        info = self.client.simGetCollisionInfo(vehicle_name="Drone0")
        obj_id = info.object_id
        obj_name = info.object_name
        if info.has_collided:
            # print ("obj id",obj_id)
            # print("obj id", obj_name)

            if obj_name != self.prev_collision_name:
                self.collision_counter += 1
                self.prev_collision_name = obj_name

        else:
            self.prev_collision_name = None
        return self.collision_counter

    def teleport_to(self, x, y, z, text=None):
        #pose_drone = self.client.simGetVehiclePose(vehicle_name=self.drone_name)
        #yaw = self.air_sim.to_eularian_angles(pose_drone.orientation)[2]
        # pose = airsim.Pose(airsim.Vector3r(x*math.cos(yaw)*5, y*5*math.sin(yaw), z), airsim.to_quaternion(0, 0, yaw))  # PRY in radians

        self.camera_heading = 180

        pose = self.air_sim.Pose(self.air_sim.Vector3r(x, y, z),
                                 self.air_sim.to_quaternion(0, 0, 0))  # PRY in radians
        self.client.simSetVehiclePose(pose, True)
        self.client.rotateToYawAsync(180, vehicle_name=self.drone_name).join()
        if text:
            self.client.simPlotStrings(strings=[text], positions=[self.air_sim.Vector3r(x + 1, y, z)],
                                       scale=10, color_rgba=[1.0, 0.0, 1.0, 1.0], duration=10.0)
    def teleport_to(self, v):
        pose_drone = self.client.simGetVehiclePose(vehicle_name=self.drone_name)
        yaw = self.air_sim.to_eularian_angles(pose_drone.orientation)[2]
        # pose = airsim.Pose(airsim.Vector3r(x*math.cos(yaw)*5, y*5*math.sin(yaw), z), airsim.to_quaternion(0, 0, yaw))  # PRY in radians
        pose = self.air_sim.Pose(v,self.air_sim.to_quaternion(0, 0, yaw))  # PRY in radians
        self.client.simSetVehiclePose(pose, True)


    def draw_path(self, sublist_of_vectors, style=""):

        if len(sublist_of_vectors) == 0:
            return

        self.client.simFlushPersistentMarkers()

        if style == "free":
            self.client.simPlotPoints(points=sublist_of_vectors,
                                      color_rgba=[0.0, 0.0, 1.0, 1.0], size=75, duration=-1, is_persistent=True)
            return

        if style == "path":
            self.client.simPlotPoints(points=sublist_of_vectors,
                                      color_rgba=[0.0, 0.0, 1.0, 1.0], size=50, duration=-1, is_persistent=True)
            self.client.simPlotLineStrip(points=sublist_of_vectors,
                                         color_rgba=[1.0, 1.0, 0.0, 1.0], thickness=5, duration=-1, is_persistent=True)

    def flush_persistent_markers(self):
        self.client.simFlushPersistentMarkers()

    # recording
    def start_recording(self):
        self.client.startRecording()

    def stop_recording(self):
        self.client.stopRecording()
