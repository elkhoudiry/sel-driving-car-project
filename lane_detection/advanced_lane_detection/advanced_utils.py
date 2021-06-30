import cv2
import numpy as np
import math


class ImageLines:
    def __init__(self, lines, allPoints, straightThresh, slopeThreshold):

        self.allLines = []

        self.straightLines = []
        self.HorizentalLines = []

        self.linesOnLeft = []
        self.linesOnRight = []

        self.leftStraightLines = []
        self.rightStraightLines = []

        self.leftHorizentalLines = []
        self.rightHorizentalLines = []

        for i in range(0, len(lines)):
            line = lines[i]

            if(line[0] > slopeThreshold or line[0] < -1 * slopeThreshold):
                continue

            if line[0] > straightThresh:
                self.straightLines.append(line)
                self.rightStraightLines.append(line)
                self.linesOnRight.append(allPoints[i])
            elif line[0] < -1 * straightThresh:
                self.straightLines.append(line)
                self.leftStraightLines.append(line)
                self.linesOnLeft.append(allPoints[i])
            elif line[0] > 0 and lines[i][0] < straightThresh:
                self.HorizentalLines.append(line)
                self.rightHorizentalLines.append(line)
                self.linesOnRight.append(allPoints[i])
            elif line[0] < 0 and lines[i][0] > - 1 * straightThresh:
                self.HorizentalLines.append(line)
                self.leftHorizentalLines.append(line)
                self.linesOnLeft.append(allPoints[i])

        for points in allPoints:
            for point in points:
                self.allLines.append(point)

        self.allLines = np.array(self.allLines)

        self.straightLines = np.array(self.straightLines)
        self.HorizentalLines = np.array(self.HorizentalLines)

        self.linesOnLeft = np.array(self.linesOnLeft)
        self.linesOnRight = np.array(self.linesOnRight)

        self.leftStraightLines = np.array(self.leftStraightLines)
        self.rightStraightLines = np.array(self.rightStraightLines)

        self.leftHorizentalLines = np.array(self.leftHorizentalLines)
        self.rightHorizentalLines = np.array(self.rightHorizentalLines)

        leftFit = []
        rightFit = []

        for i in range(0, len(self.straightLines)):
            straightLine = self.straightLines[i]
            if straightLine[0] >= straightThresh and straightLine[0] < slopeThreshold:
                rightFit.append(straightLine)
            elif straightLine[0] <= - 1 * straightThresh and straightLine[0] > -1 * slopeThreshold:
                leftFit.append(straightLine)

        self.avgedStraightLines = np.array(
            [np.average(leftFit, axis=0), np.average(rightFit, axis=0)])


def extractLinesPrams(image, houghSettings, straightThreshold, slopeLimit):
    allLines = cv2.HoughLinesP(image, houghSettings.rho, houghSettings.theta, houghSettings.minVotes, np.array(
        []), minLineLength=houghSettings.minLength, maxLineGap=houghSettings.maxGap)
    points, lines = rectifyLines(allLines, image.shape[1])
    return ImageLines(lines, points, straightThreshold, slopeLimit)


def makeLinesFromPrams(height, linesPrams):
    lines = []
    for prams in linesPrams:
        if prams is not None:
            try:
                lines.append(makeCoordinates(height, prams))
            except:
                lines.append(np.array([]))

    return lines


def makeCoordinates(height, lineParams):
    slope, intercept = lineParams
    y1 = height
    y2 = int(y1 * 4.25 / 5)
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)

    if x1 > 2147483646:
        x1 = 2147483646
    elif x1 < -2147483647:
        x1 = -2147483647

    if x2 > 2147483647:
        x2 = 2147483647
    elif x2 < -2147483647:
        x2 = -2147483647

    return np.array([x1, y1, x2, y2])


def calculateDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def rectifyLines(lines, width):

    arrayOfSlopes = []
    arrayOfSlopesRepeation = []
    arrayOfLines = []
    arrayOfPoints = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            params = np.polyfit((x1, x2), (y1, y2), 1)

            slope = round(params[0], 2)
            intercept = round(params[1], 2)

            if slope < 0 and x1 > (width * 1.5 / 3):
                continue
            elif slope > 0 and x1 < (width * 1.5 / 3):
                continue

            result = math.floor(slope)
            floor = result

            try:
                index = arrayOfSlopes.index(floor)
                arrayOfSlopesRepeation[index] += 1
                avged = arrayOfLines[index]
                newAvged = [(avged[0] + slope),
                            (avged[1] + intercept)]
                arrayOfLines[index] = newAvged
                arrayOfPoints[index].append([x1, y1, x2, y2])

            except:
                arrayOfSlopes.append(floor)
                arrayOfSlopesRepeation.append(1)
                arrayOfLines.append([slope, intercept])
                arrayOfPoints.append([[x1, y1, x2, y2]])

    for i in range(0, len(arrayOfSlopesRepeation)):
        repeat = arrayOfSlopesRepeation[i]
        cal = round(arrayOfLines[i][0] / repeat, 2)
        slope = cal

        if cal != 0.0 and cal != -0.0:
            slope = cal
        elif cal == 0.0:
            slope = 0.1
        elif cal == -0.0:
            slope = -0.1

        arrayOfLines[i] = [slope, round(arrayOfLines[i][1] / repeat, 2)]

    return arrayOfPoints, arrayOfLines


def displayLinesImage(image, lines):
    laneImage = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            if len(line) == 2:
                x1, y1, x2, y2 = makeCoordinates(laneImage.shape[0], line)
                cv2.line(laneImage, (x1, y1), (x2, y2), (255, 0, 0), 4)
            elif len(line) == 4:
                x1, y1, x2, y2 = line.reshape(4)
                cv2.line(laneImage, (x1, y1), (x2, y2), (255, 0, 0), 4)

    return cv2.addWeighted(
        image, 0.8, laneImage, 1, 1)


def getMidLineTwoLanes(firstLine, secondLine):
    x1, _, left_x2, y1 = firstLine
    x2, _, right_x2, y2 = secondLine
    mid = int((x1 + x2) / 2)
    x_offset = (left_x2 + right_x2) / 2 - mid
    y_offset = int((y1 + y2) / 2)

    return x_offset, y_offset, mid


def getMidLineOneLane(firstLine):
    x1, y1, x2, y2 = firstLine

    if x1 < x2:
        x_offset = int((x1 + x2) / 2)
    else:
        x_offset = int(x2 - x1)

    y_offset = int((y1 + y2) / 2)

    return x_offset, y_offset


def steeringAngle(x_offset, y_offset):
    angle_to_mid_radian = math.atan(x_offset / y_offset)
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)
    steering_angle = angle_to_mid_deg + 90
    return steering_angle


def steeringLine(frame, straightLaneLines,):
    xOffset = 0
    yOffset = 0
    try:
        straightLinesImage = frame
        angle = 0
        if len(straightLaneLines[0]) == 0 or len(straightLaneLines[1]) == 0:
            xOffset, yOffset = getMidLineOneLane(
                straightLaneLines[0] if len(straightLaneLines[1]) == 0 else straightLaneLines[1])
            angle = steeringAngle(xOffset, yOffset)
            straightLinesImage = displayHeadingLine(
                frame, straightLaneLines, angle, abs(xOffset), yOffset)
        else:
            xOffset, yOffset, x1 = getMidLineTwoLanes(
                straightLaneLines[1], straightLaneLines[0])
            angle = steeringAngle(xOffset, yOffset)
            straightLinesImage = displayHeadingLine(
                frame, straightLaneLines, angle, x1, yOffset)

        return angle, straightLinesImage

    except:
        return 90, frame


def displayHeadingLine(original, lines, steering_angle, x1, y2):

    frame = displayLinesImage(original, lines)

    heading_image = np.zeros_like(frame)
    height, _, _ = frame.shape

    steering_angle_radian = steering_angle / 180.0 * math.pi
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))

    cv2.line(heading_image, (x1, y1), (x2, y2), (0, 0, 255), 5)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image
