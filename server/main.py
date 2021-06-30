import socket
from lane_detection.advanced_lane_detection import main as advanced_lane
from lane_detection.settings import utils
from lane_detection.settings import keys

querySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
querySocket.connect(("8.1.8.3", 80))
HOST = querySocket.getsockname()[0]
querySocket.close()

BUFF_SIZE = 8096

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)

conn = None
arr = bytearray(20)
settings = utils.getSettingsJsonObject()
forwardMotorSpeed = int(settings[keys.keyForwardMotorSpeed])
turnMotorSpeed = int(settings[keys.keyTurnMotorSpeed])


def startServer():

    try:
        port = int(input('Enter port number (default = 65432): '))
    except:
        port = 65432

    s.bind((HOST, port))
    print(f'started server {HOST}@{port}')
    s.listen()
    global conn
    conn, addr = s.accept()
    advanced_lane.startAdvanced(0, settings, callback)


def callback(angle):
    print(f'angle from server {angle}')
    arr[0], arr[1] = steer(angle)
    conn.sendall(arr)


def steer(angle):

    if angle == 90:
        return forwardMotorSpeed, forwardMotorSpeed
    elif angle < 90:
        return turnMotorSpeed, forwardMotorSpeed
    else:
        return forwardMotorSpeed, turnMotorSpeed
