from lane_detection.settings import utils
from lane_detection.settings import keys as keys


def setSettings(keyName, default):
    file = utils.getSettingsJsonObject()
    file[keyName] = utils.setValue(file, keyName, default)
    utils.setSettingsJsonObject(file)
