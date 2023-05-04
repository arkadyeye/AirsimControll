'''
Providede by Denis and Ohad, for their final B.Sc project

'''


import cv2
import mediapipe as mp
import numpy as np
import time

import math
import socket


RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]

debug_mode = True


def dist(point, point1):
    x, y = point
    x1, y1 = point1
    distance = math.sqrt((x1 - x) ** 2 + (y1 - y) ** 2)
    return distance


# Blinking Ratio
def blink_ratio(img, landmarks, right_indices, left_indices):
    # Right eyes
    # horizontal line
    rh_right = landmarks[right_indices[0]]
    rh_left = landmarks[right_indices[8]]
    # vertical line
    rv_top = landmarks[right_indices[12]]
    rv_bottom = landmarks[right_indices[4]]

    # LEFT_EYE
    # horizontal line
    lh_right = landmarks[left_indices[0]]
    lh_left = landmarks[left_indices[8]]

    # vertical line
    lv_top = landmarks[left_indices[12]]
    lv_bottom = landmarks[left_indices[4]]

    rhDistance = dist(rh_right, rh_left)
    rvDistance = dist(rv_top, rv_bottom)

    lvDistance = dist(lv_top, lv_bottom)
    lhDistance = dist(lh_right, lh_left)

    reRatio = rhDistance / rvDistance
    leRatio = lhDistance / lvDistance

    ratio = (reRatio + leRatio) / 2

    return ratio


def blink_detector(image, results):
    if results.multi_face_landmarks:
        #reformat results to list
        img_height, img_width = image.shape[:2]
        # list[(x,y), (x,y)....]
        mesh_coords = [(int(point.x * img_width), int(point.y * img_height)) for point in
                      results.multi_face_landmarks[0].landmark]

        ratio = blink_ratio(image, mesh_coords, RIGHT_EYE, LEFT_EYE)
        if ratio > 3.9:
            # cv2.putText(image, "BLINKED: ", (500, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return True
    return False


def head_movement(image):
    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []
    # print('results.multi_face_landmarks = ', results.multi_face_landmarks)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, Im in enumerate(face_landmarks.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                    if idx == 1:
                        nose_2d = (Im.x * img_w, Im.y * img_h)
                        nose_3d = (Im.x * img_w, Im.y * img_h, Im.z * 3000)

                    x, y = int(Im.x * img_w), int(Im.y * img_h)

                    face_2d.append([x, y])
                    face_3d.append([x, y, Im.z])

            face_2d = np.array(face_2d, dtype=np.float64)
            face_3d = np.array(face_3d, dtype=np.float64)

            focal_length = 1 * img_w

            cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                   [0, focal_length, img_w / 2],
                                   [0, 0, 1]])
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
            rmat, jac = cv2.Rodrigues(rot_vec)

            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            x = angles[0] * 360
            y = angles[1] * 360
            z = angles[2] * 360

            if debug_mode:

                if y < -10:
                    text = "Looking Left"
                elif y > 10:
                    text = "Looking Right"
                elif x < -10:
                    text = "Looking Down"
                elif x > 10:
                    text = "Looking Up"
                else:
                    text = "Forward"
                # nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

                p1 = (int(nose_2d[0]), int(nose_2d[1]))
                p2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))

                cv2.line(image, p1, p2, (255, 0, 0), 3)

                cv2.putText(image, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.putText(image, "x: " + str(np.round(x, 2)), (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(image, "y: " + str(np.round(y, 2)), (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(image, "z: " + str(np.round(z, 2)), (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)

            return x, y, z

    return None


head_x = 0
head_y = 0
head_z = 0
is_blink = False

# init udp socket
UDP_IP = "127.0.0.1"
UDP_PORT = 42544
#MESSAGE = "Hello, World!"

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
#print("message: %s" % MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

cap = cv2.VideoCapture(0)

while cap.isOpened():

    success, image = cap.read()

    start = time.time()

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = face_mesh.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    head_pose = head_movement(image)
    if head_pose is not None:
        is_blink = blink_detector(image, results)
        # HP for HeadPose
        msg = "HP:"+str(round(head_pose[0],3))+","+str(round(head_pose[1],3))+","+str(round(head_pose[2],3))+","+str(round(is_blink,3))

        if debug_mode:
            print("status: "+msg)
        sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

    cv2.imshow('Head Pose Estimation', image)

    end = time.time()
    d_t = end - start
    #print("d_time: ", round(d_t*1000))

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()









