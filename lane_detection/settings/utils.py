import json
import pathlib

settingsPath = f'{pathlib.Path().absolute()}/lane_detection/settings/settings.json'


def setValue(json, key, default):
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


def setSettingsJsonObject(settings):
    dumb = json.dumps(settings)
    file = open(settingsPath, 'w')
    file.write(dumb)
    file.close()


def getSettingsJsonObject():
    print()
    file = open(settingsPath)
    bounds = json.load(file)
    file.close()
    return bounds
