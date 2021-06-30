import lane_detection as detectLanes
import lane_detection_utils as laneUtils
import socket
from cv2 import cv2 as cv2
from turbojpeg import TurboJPEG

HOST = '192.168.43.191'
PORT = 65432

currentAngle = 90
lastAngle = 90
angleLimit = 5

frame = cv2.imread('../assets/pictures/maket2.png')
frame = cv2.resize(frame, (1200, 900), interpolation=cv2.INTER_CUBIC)
isOk, offsets = detectLanes.detectLaneBoundries(frame, True, 0.50)

cv2.waitKey(0)
cv2.destroyAllWindows()

print('Host: ' + HOST)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8 * 1024 * 1024)

s.bind((HOST, PORT))
s.listen()

conn, addr = s.accept()
with conn:
    print('Connected by', addr)
    bytesArr = bytearray()
    bytesArr.append(1)
    conn.sendall(bytesArr)

    while True:
        data = conn.recv(8 * 1204 * 1024)

        if (len(data) > 0 and data[0] == 128):
            strLengthBuffer = data[1]
            frameStrLength = data[2: 2 + strLengthBuffer].decode('utf-8')
            frameLength = int(frameStrLength)
            frameBytes = bytearray()

            bytesArr = bytearray()
            bytesArr.append(2)
            conn.sendall(bytesArr)

            while len(frameBytes) < frameLength:
                buff = conn.recv(8 * 1024 * 1024)
                frameBytes.extend(buff)

            img = TurboJPEG().decode(frameBytes)
            angle = detectLanes.detectLanes(img, offsets, True, 1.0)

            if angle != 0:

                lastAngle = currentAngle
                currentAngle = laneUtils.angleStablizing(
                    angle, lastAngle, angleLimit)

            bytesArr = bytearray()
            bytesArr.append(3)
            bytesArr.append(currentAngle)
            print('angle: ', currentAngle)
            conn.sendall(bytesArr)

        cv2.waitKey(1)
