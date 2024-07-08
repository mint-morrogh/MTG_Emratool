import PySimpleGUI as sg
import subprocess
import json
from io import BytesIO
from PIL import Image
import requests
import time
import os
sg.theme('DarkBlue2')

selected_options = []
previous_selections = []


#######################################
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
#######################################


# Define the layout of the GUI
layout = [
    [sg.Text('Deck List:', font=('Helvetica', 12, 'bold'))],
    [sg.Multiline(size=(100, 20), key='-DECK-', font=('Helvetica', 12), pad=(0, 10), autoscroll=True)],
    [sg.Button('Find Combos', bind_return_key=True, size=(15, 2), button_color=('white', '#007F5F'), pad=((0, 0), 10))],
    
    [sg.Text('Potential Combos in Decklist:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
    [sg.Listbox(values=[], size=(80, 25), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, key='potential_combos_output', enable_events=True), 
    sg.Image(key='-IMAGE1-', size=(100, 100), pad=(20, 0))],
    [sg.Text('Currently Selected Option:', font=('Helvetica', 10, 'bold')), sg.InputText(key='-SELECTED1-', readonly=True, font=('Helvetica', 10, 'bold'), text_color='#222222')],
    [sg.Button('Copy', key='Copy1'), sg.Button('Clear', key='Clear1', pad=((10, 0), 0))]
]

# Create the GUI window
layout = [[sg.Column(layout, scrollable=True, size=(1300, 1000))]]

window = sg.Window('EDHREC Fetcher', layout, size=(1300, 800), resizable=False, element_padding=(0, 5), font=('Helvetica', 12))








# Event loop to handle GUI events
while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED:
        break
    
######### potential_combos_output listbox stuff ##########
    elif event == 'Copy1':
        selected_str = "\n".join(values['potential_combos_output'])
        window.TKroot.clipboard_clear()
        window.TKroot.clipboard_append(selected_str)
    elif event == 'Clear1':
        listbox = window['potential_combos_output'].Widget
        for index in listbox.curselection():
            listbox.selection_clear(index)
        selected_options = []
        window['-SELECTED1-'].update('')
        previous_selections = []
    elif event == 'potential_combos_output':
        # Get the selected options
        new_options = values['potential_combos_output']
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



    if event == 'Find Combos':
        # grab all the info from EDHREC
        deck_text = values['-DECK-']
        with open('resources/new_deck.txt', 'w') as f:
            f.write(deck_text)
        subprocess.run(['python', 'subprocesses/deck_compare.py'])
        subprocess.run(['python', 'subprocesses/edhscraper_combos.py'])

        # Load combos from JSON file
        with open('resources/EDHScraper/card_combos_multiple.json') as f:
            combos = json.load(f)

        # Update potential_combos_output element
        window['potential_combos_output'].update(values=combos)

# Close the GUI window when the event loop exits
window.close()
