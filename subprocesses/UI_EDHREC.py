import PySimpleGUI as sg
import subprocess
import json
from io import BytesIO
from PIL import Image
import requests
import time
import os

sg.theme('DarkBlue2')


#######################################

# Function to update the themes dropdown
def update_themes_dropdown(window):
    # Load themes from edhrec_themes.json
    with open('resources/EDHScraper/edhrec_themes.json', 'r') as f:
        data = json.load(f)
        themes = data['themes']

    # Load the selected theme from selected_theme.json
    with open('resources/EDHScraper/selected_theme.json', 'r') as f:
        selected_data = json.load(f)
        selected_theme = selected_data.get('selected_theme', '')

    # Extract theme names
    theme_names = [theme['theme'].replace('/', '') for theme in themes]

    # Debug: Print the themes and the selected theme
    print(f"Available themes: {theme_names}")
    print(f"Selected theme: {selected_theme}")

    # Update the dropdown with the list of themes
    window['-THEME-'].update(values=theme_names)

    # Set the current value of the dropdown to the selected theme

    window['-THEME-'].update(value=selected_theme)

# Create a dictionary to store cached image bytes, with card names as keys and image bytes as values
image_cache = {}

def get_card_image(card_ID):
    # Check if the image bytes for the card name are already in the cache
    if card_ID in image_cache:
        print('Retrieving cached image for card:', card_ID)  # Debug statement
        return image_cache[card_ID]

    # Send a GET request to the Skryfall API with the card name as a query parameter
    response = requests.get(f'https://api.scryfall.com/cards/named?exact={card_ID}')

    # Parse the JSON response to extract the image URL
    json_data = response.json()
    if 'image_uris' not in json_data:
        print('ERROR: No image found for card:', card_ID)  # Debug statement
        return None  # Return None if no image was found
    image_url = json_data['image_uris']['normal']
    print('Fetching image for card:', card_ID)  # Debug statement

    # Use the image URL to download the image
    response = requests.get(image_url)

    # Load the image into a PIL Image object
    image = Image.open(BytesIO(response.content))

    # Resize the image to fit in the PySimpleGUI window
    max_size = (470, 470)
    image.thumbnail(max_size)

    # Convert the PIL image to a bytes buffer
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()

    # Cache the image bytes for the card name for 60 seconds
    image_cache[card_ID] = image_bytes
    time.sleep(0.1)  # Introduce a short delay to avoid hitting the API too frequently
    return image_bytes

def read_new_deck(file_path):
    with open(file_path, 'r') as file:
        deck_cards = set()
        for line in file.readlines():
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split(' ', 1)
                if len(parts) > 1:
                    deck_cards.add(parts[1].strip().lower())
                else:
                    deck_cards.add(parts[0].strip().lower())
        return deck_cards

def update_listbox_color(window, key, deck_cards, color):
    listbox_widget = window[key].Widget
    for i in range(listbox_widget.size()):
        card_name = listbox_widget.get(i).strip().lower()
        if card_name not in deck_cards:
            listbox_widget.itemconfig(i, {'fg': color})
        else:
            listbox_widget.itemconfig(i, {'fg': 'white'})

#######################################



# Initialize the selected_options and previous_selections lists
selected_options = []
previous_selections = []

# clear selected theme
with open('resources/EDHScraper/selected_theme.json', 'w') as f:
    json.dump({}, f)

layout = [
    [sg.Text('Deck List:', font=('Helvetica', 12, 'bold'))],
    [sg.Multiline(size=(100, 20), key='-DECK-', font=('Helvetica', 12), pad=(0, 10), autoscroll=True)],
    [sg.Button('Analyze', bind_return_key=True, size=(10, 2), button_color=('white', '#007F5F'), pad=((0, 0), 10))],
    [sg.Text('Select a Theme:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
    [sg.DropDown(values=[], key='-THEME-', font=('Helvetica', 12), size=(30, 1), pad=(0, 10), readonly=True)],
    [sg.Column([

        [sg.Text('High Synergy Cards:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='high_synergy_cards_output', enable_events=True), 
        sg.Image(key='-IMAGE1-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED1-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy1'), sg.Button('Clear', key='Clear1', pad=((10, 0), 0))],

        [sg.Text('New Cards:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='new_cards_output', enable_events=True), 
        sg.Image(key='-IMAGE2-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED2-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy2'), sg.Button('Clear', key='Clear2', pad=((10, 0), 0))],

        [sg.Text('Top Cards:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='top_cards_output', enable_events=True), 
        sg.Image(key='-IMAGE3-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED3-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy3'), sg.Button('Clear', key='Clear3', pad=((10, 0), 0))],

        [sg.Text('Creatures:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='creatures_output', enable_events=True), 
        sg.Image(key='-IMAGE4-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED4-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy4'), sg.Button('Clear', key='Clear4', pad=((10, 0), 0))],

        [sg.Text('Enchantments:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='enchantments_output', enable_events=True), 
        sg.Image(key='-IMAGE12-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED12-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy12'), sg.Button('Clear', key='Clear12', pad=((10, 0), 0))],

        [sg.Text('Planeswalkers:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='planeswalkers_output', enable_events=True), 
        sg.Image(key='-IMAGE5-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED5-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy5'), sg.Button('Clear', key='Clear5', pad=((10, 0), 0))],

        [sg.Text('Instants:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='instants_output', enable_events=True), 
        sg.Image(key='-IMAGE6-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED6-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy6'), sg.Button('Clear', key='Clear6', pad=((10, 0), 0))],

        [sg.Text('Sorceries:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='sorceries_output', enable_events=True), 
        sg.Image(key='-IMAGE7-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED7-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy7'), sg.Button('Clear', key='Clear7', pad=((10, 0), 0))],

        [sg.Text('Utility Artifacts:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='utility_artifacts_output', enable_events=True), 
        sg.Image(key='-IMAGE8-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED8-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy8'), sg.Button('Clear', key='Clear8', pad=((10, 0), 0))],

        [sg.Text('Mana Artifacts:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='mana_artifacts_output', enable_events=True), 
        sg.Image(key='-IMAGE9-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED9-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy9'), sg.Button('Clear', key='Clear9', pad=((10, 0), 0))],

        [sg.Text('Utility Lands:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='utility_lands_output', enable_events=True), 
        sg.Image(key='-IMAGE10-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED10-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy10'), sg.Button('Clear', key='Clear10', pad=((10, 0), 0))],

        [sg.Text('Lands:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='lands_output', enable_events=True), 
        sg.Image(key='-IMAGE11-', size=(100, 100), pad=(20, 0))],
        [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED11-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
        [sg.Button('Copy', key='Copy11'), sg.Button('Clear', key='Clear11', pad=((10, 0), 0))]

    ])]
]
layout = [[sg.Column(layout, scrollable=True, size=(1300, 1000))]]

window = sg.Window('EDHREC Fetcher', layout, size=(1300, 800), resizable=False, element_padding=(0, 5), font=('Helvetica', 12))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    ########################### Listbox stuff ###########################

    ######### High Synergy ##########
    elif event == 'Copy1':
        selected_str = "\n".join(values['high_synergy_cards_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear1':
        listbox = window['high_synergy_cards_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED1-'].update('')
        previous_selections = []
    elif event == 'high_synergy_cards_output':
        # Get the selected options
        new_options = values['high_synergy_cards_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED1-'].update(selected_option)
        else:
            window['-SELECTED1-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE1-'].update(data=image_bytes)

    ######### New Cards ##########
    elif event == 'Copy2':
        selected_str = "\n".join(values['new_cards_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear2':
        listbox = window['new_cards_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED2-'].update('')
        previous_selections = []
    elif event == 'new_cards_output':
        # Get the selected options
        new_options = values['new_cards_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED2-'].update(selected_option)
        else:
            window['-SELECTED2-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE2-'].update(data=image_bytes)

    ######### Top Cards ##########
    elif event == 'Copy3':
        selected_str = "\n".join(values['top_cards_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear3':
        listbox = window['top_cards_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED3-'].update('')
        previous_selections = []
    elif event == 'top_cards_output':
        # Get the selected options
        new_options = values['top_cards_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED3-'].update(selected_option)
        else:
            window['-SELECTED3-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE3-'].update(data=image_bytes)

    ######### Creature Cards ##########
    elif event == 'Copy4':
        selected_str = "\n".join(values['creatures_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear4':
        listbox = window['creatures_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED4-'].update('')
        previous_selections = []
    elif event == 'creatures_output':
        # Get the selected options
        new_options = values['creatures_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED4-'].update(selected_option)
        else:
            window['-SELECTED4-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE4-'].update(data=image_bytes)

    ######### Enchantment Cards ##########
    elif event == 'Copy12':
        selected_str = "\n".join(values['enchantments_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear12':
        listbox = window['enchantments_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED12-'].update('')
        previous_selections = []
    elif event == 'enchantments_output':
        # Get the selected options
        new_options = values['enchantments_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED12-'].update(selected_option)
        else:
            window['-SELECTED12-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE12-'].update(data=image_bytes)

    ######### Planeswalker Cards ##########
    elif event == 'Copy5':
        selected_str = "\n".join(values['planeswalkers_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear5':
        listbox = window['planeswalkers_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED5-'].update('')
        previous_selections = []
    elif event == 'planeswalkers_output':
        # Get the selected options
        new_options = values['planeswalkers_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED5-'].update(selected_option)
        else:
            window['-SELECTED5-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE5-'].update(data=image_bytes)

    ######### Instant Cards ##########
    elif event == 'Copy6':
        selected_str = "\n".join(values['instants_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear6':
        listbox = window['instants_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED6-'].update('')
        previous_selections = []
    elif event == 'instants_output':
        # Get the selected options
        new_options = values['instants_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED6-'].update(selected_option)
        else:
            window['-SELECTED6-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE6-'].update(data=image_bytes)

    ######### Sorceries Cards ##########
    elif event == 'Copy7':
        selected_str = "\n".join(values['sorceries_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear7':
        listbox = window['sorceries_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED7-'].update('')
        previous_selections = []
    elif event == 'sorceries_output':
        # Get the selected options
        new_options = values['sorceries_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED7-'].update(selected_option)
        else:
            window['-SELECTED7-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE7-'].update(data=image_bytes)

    ######### Utility Artifact Cards ##########
    elif event == 'Copy8':
        selected_str = "\n".join(values['utility_artifacts_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear8':
        listbox = window['utility_artifacts_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED8-'].update('')
        previous_selections = []
    elif event == 'utility_artifacts_output':
        # Get the selected options
        new_options = values['utility_artifacts_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED8-'].update(selected_option)
        else:
            window['-SELECTED8-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE8-'].update(data=image_bytes)
            
    ######### Mana Artifact Cards ##########
    elif event == 'Copy9':
        selected_str = "\n".join(values['mana_artifacts_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear9':
        listbox = window['mana_artifacts_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED9-'].update('')
        previous_selections = []
    elif event == 'mana_artifacts_output':
        # Get the selected options
        new_options = values['mana_artifacts_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED9-'].update(selected_option)
        else:
            window['-SELECTED9-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE9-'].update(data=image_bytes)

    ######### Utility Land Cards ##########
    elif event == 'Copy10':
        selected_str = "\n".join(values['utility_lands_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear10':
        listbox = window['utility_lands_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED10-'].update('')
        previous_selections = []
    elif event == 'utility_lands_output':
        # Get the selected options
        new_options = values['utility_lands_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED10-'].update(selected_option)
        else:
            window['-SELECTED10-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE10-'].update(data=image_bytes)

    ######### Land Cards ##########
    elif event == 'Copy11':
        selected_str = "\n".join(values['lands_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear11':
        listbox = window['lands_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED11-'].update('')
        previous_selections = []
    elif event == 'lands_output':
        # Get the selected options
        new_options = values['lands_output']
        # Add new options to the selected_options list
        for option in new_options:
            if option not in selected_options:
                selected_options.append(option)
        # Remove deselected options from the selected_options list
        for option in previous_selections:
            if option not in new_options:
                selected_options.remove(option)
        # Update the currently selected option
        if selected_options:
            selected_option = selected_options[-1]
            window['-SELECTED11-'].update(selected_option)
        else:
            window['-SELECTED11-'].update('')
        # Update the previous_selections list
        previous_selections = new_options

        ### Pull images
        card_ID = selected_option

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE11-'].update(data=image_bytes)



    ############################################
    if event == 'Analyze':
        # grab all the info from EDHREC
        deck_text = values['-DECK-']
        new_deck = read_new_deck('resources/new_deck.txt')
        with open('resources/new_deck.txt', 'w') as f:
            f.write(deck_text)
        subprocess.run(['python', 'subprocesses/extract_commander.py'])
        # get selected theme
        selected_theme = window['-THEME-'].get()
        # save selected_theme to a JSON file
        with open('resources/EDHScraper/selected_theme.json', 'w') as f:
            json.dump({'selected_theme': selected_theme}, f)
        subprocess.run(['python', 'subprocesses/edhscraper.py'])
        ########## write out all the info ############

        ##############################
        # read the highsynergycards json file
        with open('resources/EDHScraper/edhrec_highsynergy.json', 'r') as f:
            high_synergy_data = json.load(f)['highsynergy']

        high_synergy_cards = []
        lines = high_synergy_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                high_synergy_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['high_synergy_cards_output'].update(values=high_synergy_cards)
        update_listbox_color(window, 'high_synergy_cards_output', new_deck, '#00FF00')

        #############################
        # read the new cards json file
        with open('resources/EDHScraper/edhrec_newcards.json', 'r') as f:
            new_cards_data = json.load(f)['newcards']

        new_cards = []
        lines = new_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                new_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['new_cards_output'].update(values=new_cards)
        update_listbox_color(window, 'new_cards_output', new_deck, '#00FF00')

        #############################
        # read the top cards json file
        with open('resources/EDHScraper/edhrec_topcards.json', 'r') as f:
            top_cards_data = json.load(f)['topcards']

        top_cards = []
        lines = top_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                top_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['top_cards_output'].update(values=top_cards)
        update_listbox_color(window, 'top_cards_output', new_deck, '#00FF00')

        #############################
        # read the creature cards json file
        with open('resources/EDHScraper/edhrec_creatures.json', 'r') as f:
            creature_cards_data = json.load(f)['creatures']

        creature_cards = []
        lines = creature_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                creature_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['creatures_output'].update(values=creature_cards)
        update_listbox_color(window, 'creatures_output', new_deck, '#00FF00')

        #############################
        # read the enchantments cards json file
        with open('resources/EDHScraper/edhrec_enchantments.json', 'r') as f:
            enchantments_cards_data = json.load(f)['enchantments']

        enchantments_cards = []
        lines = enchantments_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                enchantments_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['enchantments_output'].update(values=enchantments_cards)
        update_listbox_color(window, 'enchantments_output', new_deck, '#00FF00')

        #############################
        # read the planeswalkers cards json file
        with open('resources/EDHScraper/edhrec_planeswalkers.json', 'r') as f:
            planeswalkers_cards_data = json.load(f)['planeswalkers']

        planeswalkers_cards = []
        lines = planeswalkers_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                planeswalkers_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['planeswalkers_output'].update(values=planeswalkers_cards)
        update_listbox_color(window, 'planeswalkers_output', new_deck, '#00FF00')

        #############################
        # read the instant cards json file
        with open('resources/EDHScraper/edhrec_instants.json', 'r') as f:
            instants_cards_data = json.load(f)['instants']

        instants_cards = []
        lines = instants_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                instants_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['instants_output'].update(values=instants_cards)
        update_listbox_color(window, 'instants_output', new_deck, '#00FF00')

        #############################
        # read the sorceries cards json file
        with open('resources/EDHScraper/edhrec_sorceries.json', 'r') as f:
            sorceries_cards_data = json.load(f)['sorceries']

        sorceries_cards = []
        lines = sorceries_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                sorceries_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['sorceries_output'].update(values=sorceries_cards)
        update_listbox_color(window, 'sorceries_output', new_deck, '#00FF00')

        #############################
        # read the utility artifact cards json file
        with open('resources/EDHScraper/edhrec_utilityartifacts.json', 'r') as f:
            utilityartifacts_cards_data = json.load(f)['utilityartifacts']

        utilityartifacts_cards = []
        lines = utilityartifacts_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                utilityartifacts_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['utility_artifacts_output'].update(values=utilityartifacts_cards)
        update_listbox_color(window, 'utility_artifacts_output', new_deck, '#00FF00')

        #############################
        # read the mana artifact cards json file
        with open('resources/EDHScraper/edhrec_manaartifacts.json', 'r') as f:
            manaartifacts_cards_data = json.load(f)['manaartifacts']

        manaartifacts_cards = []
        lines = manaartifacts_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                manaartifacts_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['mana_artifacts_output'].update(values=manaartifacts_cards)
        update_listbox_color(window, 'mana_artifacts_output', new_deck, '#00FF00')

        #############################
        # read the utility land cards json file
        with open('resources/EDHScraper/edhrec_utilitylands.json', 'r') as f:
            utilitylands_cards_data = json.load(f)['utilitylands']

        utilitylands_cards = []
        lines = utilitylands_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                utilitylands_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['utility_lands_output'].update(values=utilitylands_cards)
        update_listbox_color(window, 'utility_lands_output', new_deck, '#00FF00')

        #############################
        # read the land cards json file
        with open('resources/EDHScraper/edhrec_lands.json', 'r') as f:
            lands_cards_data = json.load(f)['lands']

        lands_cards = []
        lines = lands_cards_data.split('\n')
        for i in range(1, len(lines)):
            line = lines[i]
            if 'of' in line and 'decks' in line:
                # get the card name from the previous line
                card_name = lines[i-1].strip()
                lands_cards.append(card_name)

        # update the high_synergy_cards_output element
        window['lands_output'].update(values=lands_cards)
        update_listbox_color(window, 'lands_output', new_deck, '#00FF00')

        #############################
        # themes dropdown
        update_themes_dropdown(window)  # Update the themes dropdown after analysis
        
        

window.close()
