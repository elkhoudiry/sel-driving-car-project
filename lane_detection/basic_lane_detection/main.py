import cv2
from lane_detection.basic_lane_detection.basic_utils import *


img = None
xs = []
ys = []


def startBasic(path, settings):
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
        laneOffests = getLaneOffsets(settings)
        laneRegion = getLaneRegion(frame, laneOffests)
    else:
        laneOffests = getLaneOffsetFromPoints(frame, xs, ys)
        saveLaneOffsets(settings, laneOffests)
        laneRegion = getLaneRegion(frame, laneOffests)

    cannySettings = getCannySettings(settings)
    houghSettings = getHoughSettings(settings)

    while(cap.isOpened()):
        _, frame = cap.read()
        if frame is None:
            cap.release()
            cv2.destroyAllWindows()
            exit()
        canny_image = canny(frame, cannySettings)
        cropped_canny = maskedRegion(canny_image, laneRegion)
        lines = houghLines(cropped_canny, houghSettings)

        try:
            avgedFitLeft, avgedFitRight = avgSlopeInterceptFit(lines)
            averaged_lines = avgSlopeIntercept(
                frame, avgedFitLeft, avgedFitRight, laneOffests.interestingHeight)
        except:
            continue

        line_image = displayLines(frame, averaged_lines)
        combo_image = addWeighted(frame, line_image)
        cv2.imshow("result", combo_image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        cv2.circle(img, (x, y), 1, (0, 0, 255), thickness=-1)
        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    1.0, (0, 0, 0), thickness=1)
        cv2.imshow("SelectWindow", img)
        xs.append(x)
        ys.append(y)
