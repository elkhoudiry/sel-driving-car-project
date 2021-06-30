import cv2
import numpy as np
from lane_detection.settings import keys
from lane_detection.settings import utils


class CannySettings:
    def __init__(self, kernel, thresh1, thresh2):
        self.kernel = kernel
        self.thresh1 = thresh1
        self.thresh2 = thresh2


class RegionOffsets:
    def __init__(self, bottomLeft, bottomRight, topRight, topLeft, interestingHeight):
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
        self.topRight = topRight
        self.topLeft = topLeft
        self.interestingHeight = interestingHeight


class HoughSettings:
    def __init__(self, rho, theta, minVotes, minLength, maxGap):
        self.rho = rho
        self.theta = theta
        self.minVotes = minVotes
        self.minLength = minLength
        self.maxGap = maxGap


def canny(img, cannySettings):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.GaussianBlur(gray, (cannySettings.kernel, cannySettings.kernel), 0)
    canny = cv2.Canny(gray, cannySettings.thresh1, cannySettings.thresh2)
    return canny


def maskedRegion(canny, roadRegion):
    mask = np.zeros_like(canny)
    region = np.array(
        [[roadRegion[0], roadRegion[1], roadRegion[2], roadRegion[3]]])
    cv2.fillPoly(mask, region, 255)
    return cv2.bitwise_and(canny, mask)


def houghLines(cropped_canny, houghSettings):
    return cv2.HoughLinesP(cropped_canny, houghSettings.rho, houghSettings.theta, houghSettings.minVotes,
                           np.array([]), minLineLength=houghSettings.minLength, maxLineGap=houghSettings.maxGap)


def addWeighted(frame, line_image):
    return cv2.addWeighted(frame, 0.8, line_image, 1, 1)


def displayLines(img, lines):
    line_image = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 0, 255), 10)
    return line_image


def makePoints(image, line, interestingHeight):
    slope, intercept = line
    y1 = int(image.shape[0])
    y2 = int(y1*interestingHeight)
    x1 = int((y1 - intercept)/slope)
    x2 = int((y2 - intercept)/slope)

    if x1 > 2147483646:
        x1 = 2147483646
    elif x1 < -2147483647:
        x1 = -2147483647

    if x2 > 2147483647:
        x2 = 2147483647
    elif x2 < -2147483647:
        x2 = -2147483647

    return [[x1, y1, x2, y2]]


def avgSlopeInterceptFit(lines):
    left_fit = []
    right_fit = []
    if lines is None:
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

    leftFitAvg = np.average(left_fit, axis=0)
    rightFitAvg = np.average(right_fit, axis=0)

    return leftFitAvg, rightFitAvg


def avgSlopeIntercept(image, leftFitAvg, rightFitAvg, interestingHeight):
    left_line = makePoints(image, leftFitAvg, interestingHeight)
    right_line = makePoints(image, rightFitAvg, interestingHeight)
    averaged_lines = [left_line, right_line]
    return averaged_lines


def getCannySettings(settings):
    kernel = int(settings[keys.keyBasicCannyKernel])
    thresh1 = int(settings[keys.keyBasicCannyThreshold1])
    thresh2 = int(settings[keys.keyBasicCannyThreshold2])

    return CannySettings(kernel, thresh1, thresh2)


def getLaneOffsets(settings):
    bottomLeft = settings[keys.keyLaneBottomLeftOffset]
    bottomRight = settings[keys.keyLaneBottomRightOffset]
    topRight = settings[keys.keyLaneTopRightOffset]
    topleft = settings[keys.keyLaneTopLeftOffset]
    interestingHeight = settings[keys.keyLaneInterestingHeight]

    return RegionOffsets(bottomLeft, bottomRight, topRight, topleft, interestingHeight)


def getLaneRegion(image, laneOffsets):
    height = image.shape[0]
    width = image.shape[1]

    bottomLeft = (int(width * laneOffsets.bottomLeft), height)
    bottomRight = (int(width - width * laneOffsets.bottomRight), height)
    topRight = (int(width - width * laneOffsets.topRight),
                int(height * laneOffsets.interestingHeight))
    topLeft = (int(width * laneOffsets.topLeft),
               int(height * laneOffsets.interestingHeight))

    return [bottomLeft, bottomRight, topRight, topLeft]


def getLaneOffsetFromPoints(image, xs, ys):
    height = image.shape[0]
    width = image.shape[1]

    percentage = 0.05

    x1 = (xs[0] - percentage * width) / width
    x2 = 1 - ((xs[1] + percentage * width) / width)
    x3 = 1 - ((xs[2] + percentage * width) / width)
    x4 = (xs[3] - percentage * width) / width

    h = ys[3] / height

    return RegionOffsets(x1, x2, x3, x4, h)


def saveLaneOffsets(settings, laneOffsets):
    settings[keys.keyLaneBottomLeftOffset] = laneOffsets.bottomLeft
    settings[keys.keyLaneBottomRightOffset] = laneOffsets.bottomRight
    settings[keys.keyLaneTopRightOffset] = laneOffsets.topRight
    settings[keys.keyLaneTopLeftOffset] = laneOffsets.topLeft
    settings[keys.keyLaneInterestingHeight] = laneOffsets.interestingHeight

    utils.setSettingsJsonObject(settings)


def getHoughSettings(settings):
    rho = settings[keys.keyBasicHoughRho]
    theta = settings[keys.keyBasicHoughTheta]
    threshold = settings[keys.keyBasicHoughThreshold]
    minLength = settings[keys.keyBasicHoughMinLength]
    maxGap = settings[keys.keyBasicHoughMaxGap]

    return HoughSettings(rho, theta, threshold, minLength, maxGap)
