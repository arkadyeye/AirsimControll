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

    # local vars, the state of the drone
    drone_speed = 0
    vertical_position = 0
    horizontal_speed = 0

    camera_heading = 180

    def __init__(self, drone_name):
        self.drone_name = drone_name
        self.client = airsim.MultirotorClient()  # connect to the simulator
        self.client.confirmConnection()
        self.client.reset()

        self.client.enableApiControl(True, vehicle_name=self.drone_name)  # enable API control on Drone0
        self.client.armDisarm(True, vehicle_name=self.drone_name)  # arm Drone0

        self.client.takeoffAsync(vehicle_name=self.drone_name).join()  # let Drone0 take-off

        # client.moveToPositionAsync(0, 0, -2.5, 1, vehicle_name=self.drone_name).join()
        # client.rotateToYawAsync(180,vehicle_name=self.drone_name).join()
        # client.simSetTraceLine([0.0, 1.0, 0.0, 0.8], 10,vehicle_name=self.drone_name)

        print("AirSim Ready")

    def add_rotation(self, heading):
        self.camera_heading = (self.camera_heading + heading) % 360

    def set_speed(self, speed):
        self.drone_speed = speed
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

    def update_loop(self):

        # global client

        # not sure that this function call should be here
        # but it's like in a big update loop
        # update_visible_path()

        # skip drone update on automatic motion
        # global automatic_mode
        # global target_on_path_index
        # global target_on_path

        # we should always track location on path. both in hand and automated mode

        if self.automatic_mode:
            return

        # global vertical_position
        # global horizontal_speed
        # global camera_heading
        # global drone_speed

        yaw_drone = airsim.to_eularian_angles(self.client.getMultirotorState().kinematics_estimated.orientation)[2]
        vx = self.drone_speed * math.cos(yaw_drone) + self.horizontal_speed * math.sin(yaw_drone)
        vy = self.drone_speed * math.sin(yaw_drone) + self.horizontal_speed * -math.cos(yaw_drone)

        # high_drone = client.simGetVehiclePose(vehicle_name="Drone0").position.z_val
        # if abs(vertical_position - high_drone) < 0.2:
        #    vertical_position_changed = False

        # round to 2 decimal points
        vx = round(vx, 2)
        vy = round(vy, 2)

        # if vx > 0.1 or vy > 0.1 or delta_camera_heading != 0 or vertical_position_changed:
        self.client.moveByVelocityZAsync(vx, vy, self.vertical_position, 1, airsim.DrivetrainType.MaxDegreeOfFreedom,
                                         airsim.YawMode(False, self.camera_heading), vehicle_name=self.drone_name)

        # if speed > 0:
        #     speed = speed - 0.5  # speed should decrease if not activate
        # if speed < 0:
        #     speed = speed + 0.5  # speed should decrease if not activated

    def get_position(self):
        pose = self.client.simGetVehiclePose(vehicle_name=self.drone_name)
        x = round(pose.position.x_val, 3)
        y = round(pose.position.y_val, 3)
        z = round(pose.position.z_val, 3)
        yaw = round(math.degrees(airsim.to_eularian_angles(pose.orientation)[2]), 3)
        return x, y, z, yaw
