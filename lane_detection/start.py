from lane_detection.basic_lane_detection import main as basic
from lane_detection.advanced_lane_detection import main as advanced
from server import main as server
import lane_detection.setSettingsScript as setSettingsScript
from lane_detection.settings import utils


def callback(angle):
    print(angle)


def start():

    running = True
    counter = 4

    while running:

        settings = utils.getSettingsJsonObject()

        print('For basic detection press: 1')
        print('For advanced detection press: 2')
        print('For starting server and advanced detection press: 3')

        for key in settings.keys():
            print(f'For editting {key} ({settings[key]}) press: {counter}')
            counter += 1

        print(f'For exiting press: {counter}')
        strChoice = input('What is your choice ? ')

        try:
            choice = int(strChoice)

            if choice == 1:
                basic.startBasic("road2.mp4", utils.getSettingsJsonObject())
                running = False
            elif choice == 2:
                advanced.startAdvanced(
                    f'tokyo_road.mp4', utils.getSettingsJsonObject(), callback)
                running = False
            elif choice == 3:
                server.startServer(65432)
                running = False
            elif choice < counter:
                key = list(settings.keys())[choice - 4]
                value = settings[key]
                setSettingsScript.setSettings(key, value)
            elif choice == counter:
                exit()
            else:
                print('wrong choice repeating')

        except Exception as ex:
            print('wrong choice repeating\n', ex)

        print()
        counter = 4


start()
