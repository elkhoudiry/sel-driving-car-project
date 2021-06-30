import frames_util as util
from pathlib import Path
import urllib.request as urllib2

from cv2 import cv2
import numpy as np
import math

lastLine = np.ndarray([])


def rotation(image, angleInDegrees):
    h, w = image.shape[:2]
    img_c = (w / 2, h / 2)

    rot = cv2.getRotationMatrix2D(img_c, angleInDegrees, 1)

    rad = math.radians(angleInDegrees)
    sin = math.sin(rad)
    cos = math.cos(rad)
    b_w = int((h * abs(sin)) + (w * abs(cos)))
    b_h = int((h * abs(cos)) + (w * abs(sin)))

    rot[0, 2] += ((b_w / 2) - img_c[0])
    rot[1, 2] += ((b_h / 2) - img_c[1])

    outImg = cv2.warpAffine(image, rot, (b_w, b_h), flags=cv2.INTER_LINEAR)
    return outImg


def canny(img):
    if img is None:
        cap.release()
        cv2.destroyAllWindows()
        exit()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = 1
    blur = cv2.GaussianBlur(gray, (kernel, kernel), 0)
    canny = cv2.Canny(blur, 125, 175)
    cv2.imshow("canny", util.rescaleFrame(canny, 0.5))
    return canny


def region_of_interest(canny):
    height = canny.shape[0]
    width = canny.shape[1]
    mask = np.zeros_like(canny)
    bottom_left = (0, height)
    bottom_right = (width - 100, height)
    top_right = (width - 100, 1000)
    top_left = (150, 1000)
    triangle = np.array([[
        bottom_left,
        bottom_right,
        top_right, top_left, ]], np.int32)
    cv2.fillPoly(mask, triangle, 255)
    # cv2.imshow("mask", util.rescaleFrame(mask, 0.5))
    masked_image = cv2.bitwise_and(canny, mask)
    cv2.imshow("masked", util.rescaleFrame(masked_image, 0.5))
    return masked_image


def houghLines(cropped_canny):
    return cv2.HoughLinesP(cropped_canny, 1, np.pi/180, 100,
                           np.array([]), minLineLength=80, maxLineGap=5)


def addWeighted(frame, line_image):
    return cv2.addWeighted(frame, 0.8, line_image, 1, 1)


def display_lines(img, lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            try:
                for x1, y1, x2, y2 in line:
                    print('x,x y,y', x1, x2, y1, y2)
                    cv2.line(line_image, (x1, y1), (x2, y2), (0, 0, 255), 10)
                    if(len(line.shape) == 2):
                        lastLine = line
            except:
                x1, x2, y1, y2 = lastLine.reshape(4)
                cv2.line(line_image, (x1, y1),
                         (x2, y2), (0, 0, 255), 10)
                print('STOOOOOOOOOOOOP')

    return line_image


def make_points(image, line):
    slope, intercept = line

    y1 = int(image.shape[0])
    y2 = int(y1*3/5)
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)
    return [[x1, y1, x2, y2]]


def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    if lines is None:
        print('returned none')
        return None
    for line in lines:
        for x1, y1, x2, y2 in line:
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                left_fit.append((slope, intercept))
            else:
                right_fit.append((slope, intercept))
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)
    # TODO last left/right_fit_average
    left_line = make_points(image, left_fit_average)
    right_line = make_points(image, right_fit_average)
    return np.array([left_line, right_line])


cap = cv2.VideoCapture("assets/videos/test.mp4")
while(cap.isOpened()):
    _, frame1 = cap.read()
    frame = rotation(frame1, 270)
    canny_image = canny(frame)

    cropped_canny = region_of_interest(canny_image)

    # try:
    lines = houghLines(cropped_canny)
    #averaged_lines = average_slope_intercept(frame, lines)
    line_image = display_lines(frame, lines)
    combo_image = addWeighted(frame, line_image)
    scaled = util.rescaleFrame(combo_image, 0.5)

    cv2.imshow("result", scaled)

    # except:
    #    cv2.imshow("result", util.rescaleFrame(frame, 0.5))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
