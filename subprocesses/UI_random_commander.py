import PySimpleGUI as sg
import subprocess
import json
from io import BytesIO
from PIL import Image
import requests
import time
import os
import pyperclip

sg.theme('DarkBlue2')

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


# Load the default image and convert it to bytes
default_image = Image.open('images/blank_card.png').convert('RGB')
default_image.thumbnail((470, 470))
buffer = BytesIO()
default_image.save(buffer, format='PNG')
default_image_bytes = buffer.getvalue()

# Define the layout of the PySimpleGUI window
layout = [
    [sg.Button('Random Commander', size=(20, 3), font=('Helvetica', 12), button_color=('white', '#007F5F'), pad=((0, 0), 10))],
    [sg.Image(key='-IMAGE-', data=default_image_bytes, size=(None, None), pad=(0, (0, 10)), background_color='white')],
    [sg.Button('Copy', size=(10, 2), font=('Helvetica', 12), pad=((0, 0), (10, 30)), button_color=('black', '#fff'))]
]

# Create the PySimpleGUI window
window = sg.Window('Random Commander', layout, element_justification='c', size=(300, 200), finalize=True)

# Update the window size to fit the default image
window.TKroot.geometry(f"{max(300, default_image.width + 50)}x{max(300, default_image.height + 200)}")

# Run the PySimpleGUI event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Random Commander':
        subprocess.run(['python', 'subprocesses/random_commander.py'])
        with open('resources/EDHScraper/commander_id.json', 'r') as f:
            commander = json.load(f)['commander']
        ### Pull images
        card_ID = commander

        # Get the image bytes for the entered card name
        image_bytes = get_card_image(card_ID)

        # Update the image element with the fetched image (if there is one)
        if image_bytes is not None:
            window['-IMAGE-'].update(data=image_bytes)
            # Get the size of the image
            image = Image.open(BytesIO(image_bytes))
            width, height = image.size
            # Set the size of the window to fit the image
            window.TKroot.geometry(f"{max(300, width + 50)}x{max(300, height + 200)}")
    elif event == 'Copy':
        commander = json.load(open('resources/EDHScraper/commander_id.json', 'r'))['commander']
        pyperclip.copy(commander)

# Close the PySimpleGUI window
window.close()

