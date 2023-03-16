'''
this class should be run independently from the controll module
because combining them makes control jitter

draw a map from

'''
import pygame
import math
import airsim
from PIL import Image, ImageDraw, ImageOps, ImageFilter

img = Image.open('../1000_map.png')
map_size = 400
ellipse_size = 2
rotate_map = True
draw_trace = True


def mask_circle_solid(pil_img, background_color, blur_radius, offset=0):
    background = Image.new(pil_img.mode, pil_img.size, background_color)

    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    return Image.composite(pil_img, background, mask)


pygame.init()
screen = pygame.display.set_mode([map_size, map_size])
pygame.display.set_caption('Rotating map')
clock = pygame.time.Clock()

drone_name = "Drone0"
client = airsim.MultirotorClient()  # connect to the simulator
client.confirmConnection()

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

    ppx = 500 + px * 500 / 127
    ppy = 500 + py * 500 / 127

    draw = ImageDraw.Draw(img)
    if draw_trace:
        draw.ellipse((ppx - ellipse_size, ppy - ellipse_size, ppx + ellipse_size, ppy + ellipse_size), fill='blue',
                     outline='blue')

    img2 = img.crop((ppx - map_size / 2, ppy - map_size / 2, ppx + map_size / 2, ppy + map_size / 2))
    img2 = mask_circle_solid(img2, (98, 108, 83), 4)
    # img2 = ImageOps.pad(img2, (map_size, map_size))
    if rotate_map:
        img2 = img2.rotate(yaw + 90)
    else:
        img2 = img2.rotate(90)

    # copy image to screen
    screen.fill((98, 108, 83))

    raw_str = img2.tobytes("raw", 'RGBA')
    surface = pygame.image.fromstring(raw_str, img2.size, 'RGBA')

    screen.blit(surface, (0, 0))

    pygame.draw.circle(screen, (0, 255, 0), (200, 200), 5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
