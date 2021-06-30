from cv2 import cv2
import numpy as np
import frames_util as util
import lane_detection_utils as laneUtils

straightThreshold = 0.4
slopeLimit = 100

horizentalIndent = 400
verticalIndent = -50

gaussianMatrixSize = 5
minCannyThreshold = 50
maxCannyThreshold = 150

angleLimit = 5
currentAngle = 0


# the smaller the values the more percission for lines
laneHoughSettings = laneUtils.HoughSettings(
    rho=2, theta=np.pi/180, minVotes=60, minLength=10, maxGap=30)


# tokyo road
roadOffsets = laneUtils.RoadOffsets(
    bottomLeft=0.2, bottomRight=0.1, topRight=0.15, topLeft=0.25, interestingHeight=0.8)


roadHoughSettings = laneUtils.HoughSettings(
    rho=2, theta=np.pi/180, minVotes=100, minLength=40, maxGap=20
)


def detectLaneBoundries(imgg, debugging=False, scale=1.0):
    laneImage = np.copy(imgg)

    cannyImage = laneUtils.canny(
        laneImage, gaussianMatrixSize, minCannyThreshold, maxCannyThreshold)

    roadRegionMask, roadRegionImage = laneUtils.lanesRegionImage(
        cannyImage, roadOffsets)

    roadRegionLines = laneUtils.extractLinesPrams(
        roadRegionImage, roadHoughSettings, straightThreshold, slopeLimit)

    image = laneUtils.displayLinesImage(laneImage, roadRegionLines.allLines)

    if roadRegionLines.avgedStraightLines is None:
        return False, None

    straightRoadLines = laneUtils.makeLinesFromPrams(
        laneImage.shape[0], roadRegionLines.straightLines)

    straightLinesImage = laneUtils.displayLinesImage(
        laneImage, straightRoadLines)

    isFound, offsets = laneUtils.returnLaneOffsets(
        laneImage.shape[1], laneImage.shape[0], straightRoadLines, horizentalIndent, verticalIndent)

    if True:

        if debugging:
            cv2.imshow('roadAllLines', util.rescaleFrame(image, scale))
            cv2.imshow('roadRegionMask', util.rescaleFrame(
                roadRegionMask, scale))
            cv2.imshow('roadRegionImage', util.rescaleFrame(
                roadRegionImage, scale))
            cv2.imshow('straightRoadRegionLines',
                       util.rescaleFrame(straightLinesImage, scale))

            try:
                laneRegionMask, laneRegionImage = laneUtils.lanesRegionImage(
                    cannyImage, offsets)
                cv2.imshow('laneRegionMask', util.rescaleFrame(
                    laneRegionMask, scale))
                cv2.imshow('laneRegionImage', util.rescaleFrame(
                    laneRegionImage, scale))

            except:
                pass

    return isFound, offsets


def detectLanes(originalImage, offsets, debugging=False, scale=1.0):

    angle = 0

    laneImage = np.copy(originalImage)

    cannyImage = laneUtils.canny(
        laneImage, gaussianMatrixSize, minCannyThreshold, maxCannyThreshold)

    _, laneRegionImage = laneUtils.lanesRegionImage(
        cannyImage, offsets)

    laneRegionLines = laneUtils.extractLinesPrams(
        laneRegionImage, laneHoughSettings, straightThreshold, slopeLimit)

    straightLaneLines = laneUtils.makeLinesFromPrams(
        laneImage.shape[0], laneRegionLines.avgedStraightLines)

    straightLinesImage = laneUtils.displayLinesImage(
        laneImage, straightLaneLines)

    xOffset = 0
    yOffset = 0

    if len(straightLaneLines) == 2:
        try:
            if len(straightLaneLines[0]) == 0 or len(straightLaneLines[1]) == 0:
                xOffset, yOffset = laneUtils.getMidLineOneLane(
                    straightLaneLines[0] if len(straightLaneLines[1]) == 0 else straightLaneLines[1])
                angle = laneUtils.steeringAngle(xOffset, yOffset)
                straightLinesImage = laneUtils.displayHeadingLine(
                    straightLinesImage, angle, abs(xOffset), yOffset)
                print('angle: ', angle)

            else:
                xOffset, yOffset, x1 = laneUtils.getMidLineTwoLanes(
                    straightLaneLines[1], straightLaneLines[0])
                angle = laneUtils.steeringAngle(xOffset, yOffset)
                straightLinesImage = laneUtils.displayHeadingLine(
                    straightLinesImage, angle, x1, yOffset)
                print('angle: ', angle)
        except:
            pass

    if debugging:
        # cv2.imshow('straighLines', util.rescaleFrame(image, scale))
        cv2.imshow('laneRegionImage', util.rescaleFrame(
            laneRegionImage, scale))
        cv2.imshow('straightAvgedLanes',
                   util.rescaleFrame(straightLinesImage, scale))

    return angle


cap = cv2.VideoCapture('../assets/videos/tokyo_road.mp4')

frame = cv2.imread('../assets/pictures/tokyo_road.png')
cv2.imshow('Original frame', frame)
cv2.waitKey(0)
isOk, offsets = detectLaneBoundries(frame, True, 0.50)

cv2.waitKey(0)
cv2.destroyAllWindows()


delayTime = 1

while True:
    _, frame = cap.read()

    # detectLanes(cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE),
    #            offests, True, 0.50)

    detectLanes(frame, offsets, True, 0.5)

    if cv2.waitKey(delayTime) & 0xFF == ord('q'):
        break
    elif cv2.waitKey(delayTime) & 0xFF == ord('d'):
        cv2.waitKey(0)
        print('breakPoint')
