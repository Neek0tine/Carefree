import os
from winreg import *
import ctypes
import sys
import zipfile
from msedge.selenium_tools import Edge, EdgeOptions
import time
from urllib.request import urlretrieve
import configparser
from threading import Thread
import PySimpleGUI as sg
config = configparser.ConfigParser()

driver = None


def read_config():
    default_delay = 3.5
    default_frequency = 30
    if not os.path.exists('config.ini'):
        with open('config.ini', 'w') as cfg:
            config['SETTINGS'] = {'delay': {default_delay}, 'frequency': {default_frequency}}
            config.write(cfg)
    else:
        config.read('config.ini')
        settings = config['SETTINGS']
        delay = float(settings['delay'])
        frequency = int(settings['frequency'])
        return delay, frequency


def raffler():
    print('[+] Raffler program starting')

    def get_engine():
        print('[!] Engine not found! Proceeding to download automatically!')
        ms_site = f'https://msedgedriver.azureedge.net/{edgeVersion1}/edgedriver_win32.zip'
        destination = str(Downloads + '\\edgedriver_win32.zip')
        print('[+] Downloading engine from Microsoft Website!')
        urlretrieve(ms_site, destination)
        print('[+] Web browser engine downloaded, will try to put it into the windows directory now.')

        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False

        if is_admin():
            print('[+] Admin privileges acquired, installing web engine ')
            with zipfile.ZipFile(destination, 'r') as zip_ref:
                zip_ref.extractall('C:\\WINDOWS\\system32')
            print('[+] Web browser engine successfuly installed! ')
            sys.modules[__name__].__dict__.clear()
        else:
            print('[!] To proceed with installation, please run this program with admin rights')
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
        Downloads = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

    keyPath1 = r"Software\Microsoft\Edge\BLBeacon"
    key1 = OpenKey(HKEY_CURRENT_USER, keyPath1, 0, KEY_READ)
    edgeVersion1 = QueryValueEx(key1, "version")[0]
    edgeVersion1 = str(edgeVersion1)

    install_dir = str('C:\\Windows\\System32')
    files_list = os.listdir(install_dir)

    if 'msedgedriver.exe' in files_list:
        print('[+] Engine found!')
        options = EdgeOptions()
        options.use_chromium = True
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        print('[+] Getting browser profile ...')
        if 'Auto-raffler' in os.listdir('C:\\Users\\nicho\\AppData\\Local\\Microsoft\\Edge'):
            print('[+] Existing browser profile found! ')
            options.add_argument('user-data-dir=C:\\Users\\nicho\\AppData\\Local\\Microsoft\\Edge\\Auto-raffler')
            options.add_argument('profile-directory=Profile 1')
            options.add_argument("--log-level=OFF")
            options.add_argument('--disable-extensions')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])

            try:
                print('[+] Initializing engine')
                global driver
                driver = Edge(options=options, executable_path='C:\\Windows\\System32\\msedgedriver.exe',
                              service_log_path='NUL')
            except:
                print('[!] Failed to launch browser. Is another browser running?')
        else:
            print('[+] Existing browser profile not found! Making new directory ..')
            os.mkdir('C:\\Users\\nicho\\AppData\\Local\\Microsoft\\Edge\\Auto-raffler')
    else:
        get_engine()

    def get_info():
        print('[+] Connecting to Scrap.tf ...')
        driver.get("https://scrap.tf/raffles")
        available_count = []
        entered_count = []
        total_count = []
        try:
            stat = driver.find_element_by_tag_name('h1').text
            stat = str(stat)
            stat = stat.split('/')
            entered_count = int(stat[0])
            total_count = int(stat[-1])
            available_count = int(total_count - entered_count)
            print(
                f'\n[+] Raffle joined: {entered_count}\n[+] Raffle available : {available_count}\n[+] Total raffle : '
                f'{total_count}')
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
                get_info()

        while driver.find_element_by_class_name('panel-body.raffle-pagination-done').text != "That's all, no more!":
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        joined_class = driver.find_elements_by_class_name("panel-raffle.raffle-entered [href]")
        joined = [elem.get_attribute('href') for elem in joined_class if "profile" not in elem.get_attribute('href')]
        total_class = driver.find_elements_by_class_name("panel-raffle  [href]")
        total = [elem0.get_attribute('href') for elem0 in total_class if "profile" not in elem0.get_attribute('href')]

        available = list(set(total) - set(joined))
        print('\n[+] Getting raffle links ...')
        print(f'[+] Collected {len(joined)} links to joined raffles')
        print(f'[+] Collected {len(total)} links to all raffles')
        print(f'[+] Collected {len(available)} links to join-able raffles')
        missmatch = abs((len(available) - available_count) / available_count) * 100
        print(f'\n[+] All raffle links collected!\n[!] Data missmatch : {missmatch}%')

        return available, joined, total, available_count, entered_count, total_count

    def raffling():
        available, joined, total, available_count, entered_count, total_count = get_info()
        print('[+] Joining rafles')
        delay, frequency = read_config()
        for index, link in enumerate(available):
            driver.get(link)
            print(f'[+] Raffle no {index}/{len(available)}')
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
            # window.write_event_value('-THREAD-')
        print(f'\n[!] All raffles joined.')
        print('====================================================')

    raffling()


def gui():
    delay, frequency = read_config()
    sg.theme('dark blue ')
    layout = [[sg.Image(filename="carefree.png", size=(256, 64))],
              [sg.Text('Delay', size=(10, 1)),
               sg.Input(default_text=delay, readonly=True, size=(8, 1), text_color='SteelBlue4',
                        background_color='SteelBlue4', key='-DELAY-IN-')],
              [sg.Text('Frequency', size=(10, 1)),
               sg.Input(default_text=frequency, readonly=True, size=(8, 1), text_color='SteelBlue4',
                        background_color='SteelBlue4', key='-FREQUENCY-IN-')],
              [sg.Button('Run', size=(12, 1), button_color='green', key='-RUN-'), sg.Button('Stop', size=(12, 1), button_color='red', key='-STOP-')],
              # [sg.Output(size=(31, 1))],
              ]

    window = sg.Window('Carefree V2.0', layout, resizable=False, icon='carefree.ico', use_default_focus=True,
                       no_titlebar=False, border_depth=0)

    while True:  # The Event Loop
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Quit'):  # if user closed the window using X or clicked Quit button
            break

        if event == 'Apply':
            config.set('SETTINGS', 'delay', values['-DELAY-IN-'])
            with open('config.ini', 'w') as cfg:
                config.write(cfg)
            print(f'New delay set: {values["-DELAY-IN-"]}')

        if event == 'Apply1':
            config.set('SETTINGS', 'frequency', values['-FREQUENCY-IN-'])
            with open('config.ini', 'w') as cfg:
                config.write(cfg)
            print(f'New frequency set: {values["-FREQUENCY-IN-"]}')
        thread = Thread(target=raffler, daemon=True)
        if event == '-RUN-':
            thread.start()
        if event == '-STOP-':
            try:
                driver.quit()
            except:
                pass


if __name__ == '__main__':
    gui()
    print('Exiting Program')
