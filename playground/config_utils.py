import json
import numpy as np
from lane_detection_utils import HoughSettings, RoadOffsets

keyRoadBottomLeftOffset = 'roadBottomLeftOffset'
keyRoadBottomRightOffset = 'roadBottomRightOffset'
keyRoadTopRightOffset = 'roadTopRightOffset'
keyRoadTopLeftOffset = 'roadTopLeftOffset'
keyRoadInterestingHeight = 'roadInterestingHeight'

keyRoadHoughRho = 'roadHoughRho'
keyRoadHoughTheta = 'roadHoughTheta'
keyRoadHoughMinVotes = 'roadHoughMinVotes'
keyRoadHoughMinLength = 'roadHoughMinLength'
keyRoadHoughMaxGap = 'roadHoughMaxGap'


def optionsMenu():
    print("Select your option: ")
    print("1- run with default configs")
    print("2- change road boundries")
    print("3- change lane hough settings")
    print("4- change general settings")


def setRoadHough():
    settings = getSettingsJsonObject()

    settings[keyRoadHoughRho] = _setValue(settings, keyRoadHoughRho, 2)
    settings[keyRoadHoughTheta] = _setValue(
        settings, keyRoadHoughTheta, np.pi / 180)
    settings[keyRoadHoughMinVotes] = _setValue(
        settings, keyRoadHoughMinVotes, 100)
    settings[keyRoadHoughMinLength] = _setValue(
        settings, keyRoadHoughMinLength, 40)
    settings[keyRoadHoughMaxGap] = _setValue(settings, keyRoadHoughMaxGap, 20)

    setSettingsJsonObject(json.dumps(settings))


def getRoadHough():
    settings = getSettingsJsonObject()
    return HoughSettings(rho=settings[keyRoadHoughRho], theta=settings[keyRoadHoughTheta], minVotes=settings[keyRoadHoughMinVotes], minLength=settings[keyRoadHoughMinLength], maxGap=settings[keyRoadHoughMaxGap])


def setRoadBoundries():

    settings = getSettingsJsonObject()

    settings[keyRoadBottomLeftOffset] = _setValue(
        settings, keyRoadBottomLeftOffset, 0.0)
    settings[keyRoadBottomRightOffset] = _setValue(
        settings, keyRoadBottomRightOffset, 0.0)
    settings[keyRoadTopRightOffset] = _setValue(
        settings, keyRoadTopRightOffset, 0.0)
    settings[keyRoadTopLeftOffset] = _setValue(
        settings, keyRoadTopLeftOffset,  0.0)
    settings[keyRoadInterestingHeight] = _setValue(
        settings, keyRoadInterestingHeight, 0.0)

    setSettingsJsonObject(json.dumps(settings))


def getRoadBoundries():
    settings = getSettingsJsonObject()
    return RoadOffsets(bottomLeft=settings[keyRoadBottomLeftOffset], bottomRight=settings[keyRoadBottomRightOffset], topRight=settings[keyRoadTopRightOffset], topLeft=settings[keyRoadTopLeftOffset], interestingHeight=settings[keyRoadInterestingHeight])


def _setValue(json, key, default):
    currentValue = _readKey(json, key, default)
    tempValue = input("enter {} ({}) : ".format(key, currentValue))
    return _readTemp(tempValue, currentValue)


def _readTemp(temp, current):
    if temp.strip() == '':
        return current
    else:
        return float(temp.strip())


def _readKey(json, key, default):
    try:
        return json[key]
    except:
        return default


def setSettingsJsonObject(dumb):
    file = open('settings.json', 'w')
    file.write(dumb)
    file.close()


def getSettingsJsonObject():
    file = open('settings.json')
    bounds = json.load(file)
    file.close()
    return bounds
