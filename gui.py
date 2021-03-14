import PySimpleGUI as sg
import time

def splash_gui():
    sg.theme('dark blue ')
    # Define the window's contents
    menu_def = [['File', ['Preferences']],
                ['Help', 'About...']]

    layout = [[sg.Image(filename="carefree.png", size=(256, 64))],  # Part 2 - The Layout
             #  [sg.Menu(menu_def, tearoff=False)],
              [sg.Text('Delay', size=(10, 1)), sg.Input(default_text='3.5', size=(8, 10), background_color='SteelBlue4'), sg.Button('Apply', button_color='SteelBlue4')],
              [sg.Text('Tolerance', size=(10, 1)), sg.Input(default_text='0', size=(8, 10), background_color='SteelBlue4'), sg.Button('Apply', button_color='SteelBlue4')],
              [sg.Text('Frequency', size=(10, 1)), sg.Input(default_text='60', size=(8, 10), background_color='SteelBlue4'), sg.Button('Apply', button_color='SteelBlue4')],
              [sg.Button('Run', size=(8, 1), button_color='SteelBlue4'), sg.Button('Pause', size=(8, 1), button_color='SteelBlue4'), sg.Button('Stop', size=(8, 1), button_color='SteelBlue4')],
              [sg.Text('Status :', size=(15, 1)), sg.Text('Initializing Driver ...')],
              [sg.Text('Available Raffles :', size=(15, 1)), sg.Text('210')],
              [sg.Text('Joined Raffles :', size=(15, 1)), sg.Text('10')]
              ]

    # Create the window
    window = sg.Window('Carefree', layout, resizable=False, icon='carefree.ico', use_default_focus=True, no_titlebar=False,
                   border_depth=0, grab_anywhere=True,).read()  # Part 3 - Window Defintion

    # Finish up by removing from the screen


splash_gui()