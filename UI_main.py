import PySimpleGUI as sg
import os
import webbrowser
import subprocess
import threading

sg.theme('DarkBlue9')

version = '0.39'


# EDHREC Fetcher theme dropdown needs a clear button to go back to nothing selected

# wheen bloomburrow releases, three tree city definitly is a tribal staple 

# add battles as a permanent type in edhrec fetcher

# commander spellbook takes ages to load in selenium 

# fix land calc to have images to the right of the list like edhrec fetcher
# lands not in deck should be green as well

# colorless mana is now being checked, can check if artifact deck or Eldrazi deck for colorless? add a colorless cards pool for those?

# Reliquary Tower?

# add a legendaries matter land support. add Plaza of Heroes if legendaries % is above 40%?
# for reference esika is 45%

# ah shit. gotta add support for split cards (and flip cards?)

# in order for pyinstaller to work you're going to have to edit all your path references to relative paths. so have fun with that
# first test file was about 68mb from the dist folder




menu_def = [
    ['File', ['Exit']],
    ['Tools', ['Random Commander', 'Deck Compare', 'EDHREC Fetcher', 'Land Calculator', 'Combo Finder', 'UI Test']],
    ['Help', 'Changelog']
]

# Main window init and add the menu and tab group
main_window_layout = [
    [sg.Menu(menu_def)],
    [sg.Column([[sg.Text('Emratool', font=('Arial', 20, 'bold')),
                sg.Text('version: ' + version, font=('Arial', 10, 'bold'))]],
                justification='center')],
    [sg.Column([[sg.Image('images/emrakul_splash2.png')]],
                justification='center')],
    [sg.Column([[sg.Text('created by mint_mundane', font=('Arial', 10))]],
                justification='center')]
]

def run_subprocess(command):
    def monitor_subprocess(proc):
        proc.wait()
        main_window.write_event_value('SUBPROCESS_COMPLETE', '')

    main_window.minimize()
    process = subprocess.Popen(command, shell=True)
    threading.Thread(target=monitor_subprocess, args=(process,), daemon=True).start()

main_window = sg.Window('Emratool ' + version, main_window_layout, finalize=True)

while True:
    event, values = main_window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    elif event == 'Changelog':
        with open('resources/changelog.txt', 'r') as f:
            contents = f.read()
        sg.popup_scrolled(contents, title='Changelog')
    elif event == 'Deck Compare':
        run_subprocess('python subprocesses/UI_deck_compare.py')
    elif event == 'Land Calculator':
        run_subprocess('python subprocesses/UI_land_calc.py')
    elif event == 'EDHREC Fetcher':
        run_subprocess('python subprocesses/UI_EDHREC.py')
    elif event == 'UI Test':
        run_subprocess('python subprocesses/UI_test.py')
    elif event == 'Combo Finder':
        webbrowser.open_new_tab('https://commanderspellbook.com/find-my-combos/')
    elif event == 'Random Commander':
        run_subprocess('python subprocesses/UI_random_commander.py')
    elif event == 'SUBPROCESS_COMPLETE':
        main_window.normal()
        main_window.bring_to_front()

# Close the window and exit the program
main_window.close()