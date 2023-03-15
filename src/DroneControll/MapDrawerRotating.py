'''
this class should be run independently from the controll module
because combining them makes control jitter

draw a map from

'''


#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

from PIL import Image, ImageDraw,ImageOps

# plt.ion()
# fig, ax = plt.subplots()
#
# plt.imshow(mpimg.imread('../1000_map.png'))
# circle = plt.Circle((500, 500), 5, color='r')
# #ax.add_patch(circle)


img = Image.open('../1000_map.png')
#
# drone_name = "Drone0"
# client = airsim.MultirotorClient()  # connect to the simulator
# client.confirmConnection()
#
# while True:
#     pose = client.simGetVehiclePose(vehicle_name=drone_name)
#     px = round(pose.position.x_val, 3)
#     py = round(pose.position.y_val, 3)
#     print("px",px)
#     print("py",py)
#
#     img.show()

    # ppx = 500 + px*500/127
    # ppy = 500 + py*500/127
    #
    # #circle.center = (500 + px*100, 500 + py*100)
    # circle = plt.Circle((ppx, ppy), 10, color='r')
    # ax.add_patch(circle)
    # fig.canvas.draw()
    # fig.canvas.flush_events()
    # plt.pause(0.5)



import pygame
import math
import airsim


map_size = 400

pygame.init()
screen = pygame.display.set_mode([map_size, map_size])
pygame.display.set_caption('Rotating image example')
clock = pygame.time.Clock()

# img = pygame.image.load('../1000_map.png').convert()

drone_name = "Drone0"
client = airsim.MultirotorClient()  # connect to the simulator
client.confirmConnection()

# img_rect = img.get_rect(center = screen.get_rect().center)


ellipse_size = 10
done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # get data from airsim
    pose = client.simGetVehiclePose(vehicle_name=drone_name)
    px = round(pose.position.x_val, 3)
    py = round(pose.position.y_val, 3)
    yaw = round(math.degrees(airsim.to_eularian_angles(pose.orientation)[2]), 3)
    # print("px",px)
    # print("py",py)

    ppx = 500 + px*500/127
    ppy = 500 + py*500/127

    draw = ImageDraw.Draw(img)
    draw.ellipse((ppx-ellipse_size, ppy-ellipse_size, ppx+ellipse_size, ppy+ellipse_size), fill = 'blue', outline ='blue')
    img2 = img.rotate(0+90, center=(ppx, ppy))
    img2 = img2.crop((ppx-map_size/2, ppy - map_size/2, ppx+map_size/2, ppy+map_size/2))
    img2 = ImageOps.pad(img2, (map_size, map_size))

    # pygame.draw.circle(surface, (255, 255, 0), (ppx,ppy), 15)

    # cropped = pygame.Surface((400, 400))
    # cropped.blit(surface, (0, 0), (ppx - 200, ppy - 200, 400, 400))

    # cropped = pygame.transform.rotate(cropped, yaw)
    # width = abs((400 / (math.cos(math.radians(yaw%90)))))
    # dx = (566-width)/2
    # print ("width",width)
    # print("dx", dx)



    # rotate image
    # offset = pygame.math.Vector2(0,0)
    # rot_img = rotate(img,180,(500-ppx,500-ppy),offset)

    # rot_img = pygame.transform.rotate(img, 0)

    # img_rect = img.get_rect(center = cropped.center)

    # copy image to screen
    screen.fill((0, 0, 0))
    # screen.blit(rot_img[0], (ppy,ppx))

    # screen.blit(img, (-ppx, -ppy))
    # screen.blit(cropped,(dx,dx))
    raw_str = img2.tobytes("raw", 'RGBA')
    surface = pygame.image.fromstring(raw_str, img2.size, 'RGBA')
    # print(img2.size)
    screen.blit(surface, (0,0))

    # screen.blit(pygame.transform.rotate(screen, yaw), (0, 0))

    # pygame.draw.circle(screen, (0, 255, 0), img_rect.center, 5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()