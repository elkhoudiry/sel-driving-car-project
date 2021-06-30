from cv2 import cv2 as cv
import numpy as np

# displays video feed from VideoCapture object


def displayFeed(capture):
    while True:
        # reading video feed frame by frame
        # returns a frame of the video & boolean if the frame is read correctly
        _, frame = capture.read()

        resizedFrame = rescaleFrame(frame, 0.3)

        # Display the resulting frame
        cv.imshow('Video', frame)
        cv.imshow('Resized 30% video', resizedFrame)

        # if q key is pressed exist the loop
        if cv.waitKey(20) & 0xFF == ord('q'):
            break


def displayFeedScaled(capture, scale):
    while True:
        # reading video feed frame by frame
        # returns a frame of the video & boolean if the frame is read correctly
        _, frame = capture.read()

        resizedFrame = rescaleFrame(frame, scale)
        resizedFrame = cv.cvtColor(resizedFrame, cv.COLOR_BGR2GRAY)
#        resizedFrame = adaptiveInvThreshold(resizedFrame, 255)
        resizedFrame = cv.Canny(resizedFrame, 125, 175)
        # Display the resulting frame
        cv.imshow('Resized video treshed', resizedFrame)

        # if q key is pressed exist the loop
        if cv.waitKey(20) & 0xFF == ord('q'):
            break

# rescales the frame into percentage size
# takes scale from 0.0 to 1.0


def rescaleFrame(frame, scale):

    if scale == 1.0:
        return frame

    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)

    dimns = (width, height)

    return cv.resize(frame, dimns, interpolation=cv.INTER_AREA)

# changes resolution of live video


def changeRes(capture, width, height):

    capture.set(3, width)
    capture.set(4, height)


# Translation
def translate(img, x, y):
    transMat = np.float32([[1, 0, x], [0, 1, y]])
    dimensions = (img.shape[1], img.shape[0])
    return cv.warpAffine(img, transMat, dimensions)

# Rotation


def rotate(img, angle, rotPoint=None):
    (height, width) = img.shape[:2]

    if rotPoint is None:
        rotPoint = (width//2, height//2)

    rotMat = cv.getRotationMatrix2D(rotPoint, angle, 1.0)
    dimensions = (width, height)

    return cv.warpAffine(img, rotMat, dimensions)


# Resizing

def resize(img, width, height, interpolation=cv.INTER_AREA):
    return cv.resize(img, (width, height), interpolation=interpolation)


# Flipping
# directions 0 for vertical, 1 for hori, -1 for both vertical & hori

def flip(img, direction):
    return cv.flip(img, direction)


# Cropping
def crop(img, startRange, endRange):
    return img[startRange, endRange]


# thresholding

def invThreshold(img, thresholdValue, newValue):
    _, threshed = cv.threshold(
        img, thresholdValue, newValue, cv.THRESH_BINARY_INV)
    return threshed


def adaptiveInvThreshold(img, newValue):
    threshed = cv.adaptiveThreshold(
        img, newValue, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 25, 9)
    return threshed
