'''
this class should be run independently from the controll module
because combining them makes control jitter

draw a map from

'''

import airsim
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

plt.ion()
fig, ax = plt.subplots()

plt.imshow(mpimg.imread('../1000_map.png'))
circle = plt.Circle((500, 500), 5, color='r')
#ax.add_patch(circle)

drone_name = "Drone0"
client = airsim.MultirotorClient()  # connect to the simulator
client.confirmConnection()

while True:
    pose = client.simGetVehiclePose(vehicle_name=drone_name)
    px = round(pose.position.x_val, 3)
    py = round(pose.position.y_val, 3)
    print("px",px)
    print("py",py)

    ppx = 500 + px*500/127
    ppy = 500 + py*500/127

    #circle.center = (500 + px*100, 500 + py*100)
    circle = plt.Circle((ppx, ppy), 10, color='r')
    ax.add_patch(circle)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.5)
