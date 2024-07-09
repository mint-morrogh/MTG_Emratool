import PySimpleGUI as sg
import os
import webbrowser

sg.theme('DarkBlue9')

version = '0.34'

#This works! now, when loading a deck by default no themes are selected. this is expected behavior, however, once a theme has been selected, and we analyze the deck again, while it loads the correct URL, in the GUI of this application, we dont see the selected theme displayed. is there an easy way to keep the selected theme shown in the dropdown menu of the GUI?



# have theme also stay in the dropdown when selected

# if the deck is exactly 3 colors, prioritize one cycle tri land

# add battles as a permanent type

# commander spellbook takes ages to load in selenium 

# fix land calc to do the same thing as edhrec fetcher

# colorless mana is now being checked, can check if artifact deck or Eldrazi deck for colorless? add a colorless cards pool for those?

# Reliquary Tower?

# something to check land list for dupes before returning the list

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
        os.system('python subprocesses/UI_deck_compare.py')
    elif event == 'Land Calculator':
        os.system('python subprocesses/UI_land_calc.py')
    elif event == 'EDHREC Fetcher':
        os.system('python subprocesses/UI_EDHREC.py')
    elif event == 'UI Test':
        os.system('python subprocesses/UI_test.py')
    elif event == 'Combo Finder':
        webbrowser.open_new_tab('https://commanderspellbook.com/find-my-combos/')
    elif event == 'Random Commander':
        os.system('python subprocesses/UI_random_commander.py')


# Close the window and exit the program
main_window.close()
