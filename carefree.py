import configparser
import os
import random
import threading
import time
from urllib.request import urlretrieve
from winreg import *

import PySimpleGUI as sg
from msedge.selenium_tools import Edge, EdgeOptions

config = configparser.ConfigParser()


def read_config():
    delay = 3.5
    tolerance = 1
    frequency = 30
    if not os.path.exists('config.ini'):
        with open('config.ini', 'w') as cfg:
            config['SETTINGS'] = {'delay': '3.5', 'tolerance': '1', 'frequency': '30'}
            config.write(cfg)
    else:
        config.read('config.ini')
        settings = config['SETTINGS']
        delay = float(settings['delay'])
        tolerance = int(settings['tolerance'])
        frequency = int(settings['frequency'])

    return delay, tolerance, frequency


def splash_gui():
    delay, tolerance, frequency = read_config()
    sg.theme('dark blue ')
    layout = [[sg.Image(filename="carefree.png", size=(256, 64))],
              [sg.Text('Delay', size=(10, 1)),
               sg.Input(default_text=delay, size=(8, 1), background_color='SteelBlue4', key='-DELAY-IN-'),
               sg.Button('Apply', size=(8, 1), button_color='SteelBlue4')],
              # [sg.Text('Tolerance', size=(10, 1)),sg.Input(default_text=tolerance, size=(8, 1), background_color='SteelBlue4', key='-TOLERANCE-IN-'), sg.Button('Apply', size=(8, 1), button_color='SteelBlue4')],
              [sg.Text('Frequency', size=(10, 1)),
               sg.Input(default_text=frequency, size=(8, 1), background_color='SteelBlue4', key='-FREQUENCY-IN-'),
               sg.Button('Apply', size=(8, 1), button_color='SteelBlue4')],
              [sg.Button('Run', size=(29, 1), button_color='green')],
              [sg.Output(size=(31, 1))],
              [sg.Text('Available Raffles :', size=(15, 1)),
               sg.InputText('-', size=(8, 1), text_color='SteelBlue4', readonly=True, key='-AVAILABLE-')],
              [sg.Text('Joined Raffles :', size=(15, 1)), sg.InputText('-', size=(8, 1), text_color='SteelBlue4', readonly=True, key='-JOINED-')]
              ]
    window = sg.Window('Carefree V2.0', layout, resizable=False, icon='carefree.ico', use_default_focus=True,
                       no_titlebar=False, border_depth=0)

    def initialize():  # Initialize the program
        print('Initializing Engine ...')
        options = EdgeOptions()
        options.use_chromium = True
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        def tutorial():
            layout_error = [[sg.Text('What to do after you downloaded browser engine')],
                            [sg.Text('1. The WebDriver is downloaded in consideration of your browser version and is located at your "Downloads" folder')],
                            [sg.Text('2. To enable the program, the engine "msedgedriver.exe" needs to EXTRACTED and be placed in PATH. If you"re not sure which directory in your system is PATH, put "msedgedriver.exe" to "C:\Windows\System32"')],
                            [sg.Text()],
                            [sg.Text('I understand your worry about doing something with System32, or you could add PATH yourself if you feel uncomfortable')],
                            [sg.Text('Documentation regarding adding folder to path: "https://docs.alfresco.com/4.2/tasks/fot-addpath.html" ')],
                            [sg.Text()],
                            [sg.Text('If you"re wondering why I do not automate adding PATH in this program, I do not want to do system wide changes in your system. Everything that happens here is within your consent.')],
                            [sg.Button('I Understand', button_color='green', key='-CONFIRM-')],
                            ]
            windowe = sg.Window(title='Tutorial', layout=layout_error, grab_anywhere=False, icon='carefree.ico')

            while True:
                event, values = windowe.read()

                if event in (sg.WIN_CLOSED, 'Quit'):  # if user closed the window using X or clicked Quit button
                    break
                elif event == '-CONFIRM-':  # if user closed the window using X or clicked Quit button
                    break
            exit()

        def get_engine():
            with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
                Downloads = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

            keyPath1 = r"Software\Microsoft\Edge\BLBeacon"
            key1 = OpenKey(HKEY_CURRENT_USER, keyPath1, 0, KEY_READ)
            edgeVersion1 = QueryValueEx(key1, "version")[0]
            edgeVersion1 = str(edgeVersion1)

            #  localappdata = os.getenv('LOCALAPPDATA') <- Nick's installation folder
            install_dir = str('C:\\Windows\\System32')
            files_list = os.listdir(install_dir)

            if 'msedgedriver.exe' in files_list:
                pass
            else:
                sg.Popup('Browser engine not found, Downloading browser engine.', no_titlebar=False, grab_anywhere=True, icon='carefree.ico', title=' ')
                ms_site = f'https://msedgedriver.azureedge.net/{edgeVersion1}/edgedriver_win32.zip'
                destination = str(Downloads + '\\edgedriver_win32.zip')
                urlretrieve(ms_site, destination)
                y = 0
                while y < 100:
                    time.sleep(2)
                    y += 10 + random.randint(1, 6)
                    if y > 100:
                        print("\r Download progress :  100 %")
                        break
                    else:
                        print("Download progress :  {}".format(y), '%')
                tutorial()


        get_engine()

        def get_profile():
            print('Getting browser profile ...')
            if 'Auto-raffler' in os.listdir('C:\\Users\\nicho\\AppData\\Local\\Microsoft\\Edge'):
                options.add_argument('user-data-dir=C:\\Users\\nicho\\AppData\\Local\\Microsoft\\Edge\\Auto-raffler')
                options.add_argument('profile-directory=Profile 1')
                options.add_argument("--log-level=OFF")
                options.add_argument('--disable-extensions')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
            else:
                os.mkdir('C:\\Users\\nicho\\AppData\\Local\\Microsoft\\Edge\\Auto-raffler')
                get_profile()

        get_profile()

        driver = Edge(options=options, executable_path='C:\\Windows\\System32\\msedgedriver.exe', service_log_path='NUL')

        def get_stat():
            # Get raffle info
            print('Connecting to Scrap.tf ...')
            driver.get("https://scrap.tf/raffles")
            try:
                stat = driver.find_element_by_tag_name('h1').text
                stat = str(stat)
                stat = stat.split('/')
                entered_count = stat[0]
                entered_count = int(entered_count)
                total_count = stat[-1]
                total_count = int(total_count)
                available_count = total_count - entered_count

                return [entered_count, total_count, available_count]
            except:
                print('Unable to get website data. Are you logged in?')
                driver.find_element_by_class_name('sits-login').click()
                cfm = ''
                while cfm != 'y':
                    print(
                        'Feel free to login or not to login. This program saves its data on your local laptop and is '
                        'not connected to the internet')
                    cfm = str(input('Have you logged in? (Y/N) : '))
                    cfm = cfm.casefold()

        def get_links():  # Collecting raffle links
            stat = get_stat()


            while driver.find_element_by_class_name('panel-body.raffle-pagination-done').text != "That's all, no more!":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            joined_class = driver.find_elements_by_class_name("panel-raffle.raffle-entered [href]")
            joined = [elem.get_attribute('href') for elem in joined_class]
            total_class = driver.find_elements_by_class_name("panel-raffle  [href]")
            total = [elem0.get_attribute('href') for elem0 in total_class]

            for x in joined:
                if 'profile' in x:
                    joined.remove(x)
            for y in total:
                if 'profile' in y:
                    total.remove(y)

            available = list(set(total) - set(joined))
            print('Getting raffle links ...')
            print(f'Collected {len(joined)} links to joined raffles')
            print(f'Collected {len(total)} links to all raffles')
            print(f'Collected {len(available)} links to join-able raffles')
            print('All raffle links collected!')
            return joined, total, available

        def enter_raffle():
            joined, total, available = get_links()
            window.refresh()

            def overwatch():
                print('Entering overwatch ...')
                t = frequency
                while True:
                    stat = get_stat()
                    if stat[0] >= stat[1]:
                        while t != 0:
                            print(f'Refreshing in {t} seconds')
                            time.sleep(1)
                            t -= 1
                        driver.refresh()
                        t = frequency
                    else:
                        get_stat()
                        raffle_joiner()

            if joined == total and len(available) == 0:
                print('No raffles are available to be joined. Entering overwatch mode.')
                print('====================================================')
                overwatch()

            def raffle_joiner():
                print('Entering raffles ...')
                start = time.time()
                start = int(start)
                for raffle in available:
                    joined.append(raffle)
                    available.remove(raffle)
                    print(f"{len(available)} Raffles left.")
                    window['-JOINED-'].Update(value=len(joined))
                    window['-AVAILABLE-'].Update(value=len(available))
                    start = int(start)
                    driver.get(url=raffle)
                    desc = ''
                    try:
                        driver.find_element_by_css_selector(
                            '#pid-viewraffle > div.container > div > div.well.raffle-well > div.row.raffle-opts-row > '
                            'div.col-xs-7.enter-raffle-btns > button:nth-child(3)').click()
                    except:
                        try:
                            desc = driver.find_element_by_class_name('raffle-row-full-width').text
                        except:
                            print('\n[!]Uknown error occured, pleas contact the developer!')
                        if 'raffle ended' in desc:
                            print('\n[!] A raffle has ended and I failed to join it on time!')
                    time.sleep(delay)
                stop = time.time()
                elapsed = stop - start
                print(f'\n[!] All raffles joined. Elapsed time : {round(elapsed):02d} seconds')
                print('====================================================')
                overwatch()

            raffle_joiner()

        enter_raffle()

    def start_init():
        threading.Thread(target=initialize(), daemon=True).start()

    while True:  # The Event Loop
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Quit'):  # if user closed the window using X or clicked Quit button
            break

        if event == 'Apply':
            config.set('SETTINGS', 'delay', values['-DELAY-IN-'])
            with open('config.ini', 'w') as cfg:
                config.write(cfg)
            print(f'New delay set: {values["-DELAY-IN-"]}')

        if event == 'Apply0':
            config.set('SETTINGS', 'tolerance', values['-TOLERANCE-IN-'])
            with open('config.ini', 'w') as cfg:
                config.write(cfg)
            print(f'New tolerance set: {values["-TOLERANCE-IN-"]}')

        if event == 'Apply1':
            config.set('SETTINGS', 'frequency', values['-FREQUENCY-IN-'])
            with open('config.ini', 'w') as cfg:
                config.write(cfg)
            print(f'New frequency set: {values["-FREQUENCY-IN-"]}')

        if event == 'Run':
            start_init()

        elif event == sg.WIN_CLOSED or event == 'Exit':
            break



splash_gui()
