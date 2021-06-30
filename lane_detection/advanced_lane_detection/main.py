import cv2
from lane_detection.basic_lane_detection import basic_utils as basic_utils
from lane_detection.advanced_lane_detection import advanced_utils as utils


img = None
xs = []
ys = []

straightThreshold = 0.4
slopeLimit = 999999999999999


def startAdvanced(path, settings, callback):
    cap = cv2.VideoCapture(path)
    _, frame = cap.read()

    global img
    img = frame

    if frame is None:
        cap.release()
        cv2.destroyAllWindows()
        exit()

    cv2.namedWindow("SelectWindow")
    cv2.setMouseCallback("SelectWindow", on_EVENT_LBUTTONDOWN)

    cv2.imshow("SelectWindow", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(xs) == 0:
        laneOffests = basic_utils.getLaneOffsets(settings)
        laneRegion = basic_utils.getLaneRegion(frame, laneOffests)
    else:
        laneOffests = basic_utils.getLaneOffsetFromPoints(frame, xs, ys)
        basic_utils.saveLaneOffsets(settings, laneOffests)
        laneRegion = basic_utils.getLaneRegion(frame, laneOffests)

    cannySettings = basic_utils.getCannySettings(settings)
    houghSettings = basic_utils.getHoughSettings(settings)

    while(cap.isOpened()):
        _, frame = cap.read()
        if frame is None:
            cap.release()
            cv2.destroyAllWindows()
            exit()

        angle, straightLinesImage = processFrameToAngle(
            frame, cannySettings, laneRegion, houghSettings)

        callback(angle)
        cv2.imshow("result", straightLinesImage)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def processFrameToAngle(frame, cannySettings, laneRegion, houghSettings):
    canny_image = basic_utils.canny(frame, cannySettings)
    cropped_canny = basic_utils.maskedRegion(canny_image, laneRegion)
    laneRegionLines = utils.extractLinesPrams(
        cropped_canny, houghSettings, straightThreshold, slopeLimit)

    straightLaneLines = utils.makeLinesFromPrams(
        frame.shape[0], laneRegionLines.avgedStraightLines)

    if len(straightLaneLines) == 2:
        return utils.steeringLine(frame, straightLaneLines)

    return 90, frame


def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        cv2.circle(img, (x, y), 1, (0, 0, 255), thickness=-1)
        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    1.0, (0, 0, 0), thickness=1)
        cv2.imshow("SelectWindow", img)
        xs.append(x)
        ys.append(y)
