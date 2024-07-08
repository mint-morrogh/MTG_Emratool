import subprocess
import requests
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import json
from io import BytesIO
from PIL import Image

sg.theme('DarkBlue2')


def get_card_image(card_name):
    # Send a GET request to the Skryfall API with the card name as a query parameter
    response = requests.get(f'https://api.scryfall.com/cards/named?exact={card_name}')

    # Parse the JSON response to extract the image URL
    json_data = response.json()
    if 'image_uris' not in json_data:
        print('ERROR: No image found for card:', card_name)  # Debug statement
        return None  # Return None if no image was found
    image_url = json_data['image_uris']['normal']
    print('Fetching image for card:', card_name)  # Debug statement

    # Use the image URL to download the image
    response = requests.get(image_url)

    # Load the image into a PIL Image object
    image = Image.open(BytesIO(response.content))

    # Resize the image to fit in the PySimpleGUI window
    max_size = (500, 500)
    image.thumbnail(max_size)

    # Convert the PIL image to a bytes buffer
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()

    return image_bytes



# Define the PySimpleGUI layout
layout = [
    [sg.Text('Deck List:', font=('Helvetica', 12, 'bold'))],
    [sg.Multiline(size=(100, 20), key='-DECK-', font=('Helvetica', 12), pad=(0, 10))],
    [sg.Button('Analyze', bind_return_key=True, size=(10, 2), button_color=('white', '#007F5F'), pad=((0, 0), 10))],
    [sg.Text('Mana Information:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
    ## graph goes here
    [
        sg.Column([
            [
                sg.Image('images/colorless_mana.png', size=(30, 30)),
                sg.Text('Number of occurrences in Deck'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-COLORLESS_MANA-'),
                sg.Text('Percentage'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_COLORLESS-')
            ],
            [
                sg.Image('images/white_mana.png', size=(30, 30)),
                sg.Text('Number of occurrences in Deck'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-WHITE_MANA-'),
                sg.Text('Percentage'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_WHITE-')
            ],
            [
                sg.Image('images/blue_mana.png', size=(30, 30)),
                sg.Text('Number of occurrences in Deck'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-BLUE_MANA-'),
                sg.Text('Percentage'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_BLUE-')
            ],
            [
                sg.Image('images/black_mana.png', size=(30, 30)),
                sg.Text('Number of occurrences in Deck'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-BLACK_MANA-'),
                sg.Text('Percentage'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_BLACK-')
            ],
            [
                sg.Image('images/red_mana.png', size=(30, 30)),
                sg.Text('Number of occurrences in Deck'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-RED_MANA-'),
                sg.Text('Percentage'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_RED-')
            ],
            [
                sg.Image('images/green_mana.png', size=(30, 30)),
                sg.Text('Number of occurrences in Deck'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-GREEN_MANA-'),
                sg.Text('Percentage'),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_GREEN-')
            ]
        ], element_justification='c'),

    ],
    [sg.Text('Spell Information:', font=('Helvetica', 12, 'bold'), pad=(0, 10))],

    [
        
        sg.Column([
            [
                sg.Image('images/mtg_info.png', size=(30, 30)),
                sg.Text('Enchantments', size=(23, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-ENCHANTMENTS-'),
                sg.Text('Percentage', size=(8, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_ENCHANTMENTS-')
            ],
            [
                sg.Image('images/mtg_info.png', size=(30, 30)),
                sg.Text('Artifacts', size=(23, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-ARTIFACTS-'),
                sg.Text('Percentage', size=(8, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_ARTIFACTS-')
            ],
            [
                sg.Image('images/mtg_info.png', size=(30, 30)),
                sg.Text('Creatures', size=(23, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-CREATURES-'),
                sg.Text('Percentage', size=(8, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_CREATURES-')
            ],
            [
                sg.Image('images/mtg_info.png', size=(30, 30)),
                sg.Text('Instants', size=(23, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-INSTANTS-'),
                sg.Text('Percentage', size=(8, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_INSTANTS-')
            ],
            [
                sg.Image('images/mtg_info.png', size=(30, 30)),
                sg.Text('Sorceries', size=(23, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-SORCERIES-'),
                sg.Text('Percentage', size=(8, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_SORCERIES-')
            ],
            [
                sg.Image('images/mtg_info.png', size=(30, 30)),
                sg.Text('Planeswalkers', size=(23, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PLANESWALKERS-'),
                sg.Text('Percentage', size=(8, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_PLANESWALKERS-')
            ],
            [
                sg.Image('images/mtg_info_legend.png', size=(30, 30)),
                sg.Text('Legendaries', size=(23, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-LEGENDARIES-'),
                sg.Text('Percentage', size=(8, 1)),
                sg.InputText(size=(10, 1), font=('Helvetica', 12), disabled=True, disabled_readonly_background_color='#335267', key='-PERCENT_LEGENDARIES-')
            ]
        ], element_justification='c')
    ],

        [sg.Text('Number of Creature Subtypes: (Tribal Descending Order)', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Multiline(size=(80, 5), disabled=True, key='-TRIBAL-', font=('Helvetica', 12), pad=(0, 10))],

        [sg.Text('Best Possible Lands: (Descending Order)', font=('Helvetica', 12, 'bold'), pad=(0, 10))],
        [sg.Multiline(size=(80, 20), disabled=True, key='-LANDS-', font=('Helvetica', 12), pad=(0, 10))],
        [sg.Button('<<', key='-PREV-', size=(10, 2), button_color=('white', '#007F5F'), pad=((0, 0), 10)), sg.Button('Fetch Land Images', key='-FETCH-', size=(15, 2), button_color=('white', '#007F5F'), pad=((0, 0), 10)), sg.Button('>>', key='-NEXT-', size=(10, 2), button_color=('white', '#007F5F'), pad=((0, 0), 10))],
        [sg.Image(key='-IMAGE-', size=(100, 500), )]
]



# Create the PySimpleGUI window
window = sg.Window('Deck Comparison Tool', layout=[[sg.Column(layout, size=(1300, 800), scrollable=True, vertical_scroll_only=True)]], finalize=True)


# Initialize variables for the image carousel
image_bytes_list = []
current_image_index = 0

# Run the PySimpleGUI event loop
while True:
    event, values = window.read()
    
    # If the user closes the window or clicks the "Exit" button, exit
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
    # If the user clicks the "Analyze" button
    if event == 'Analyze':
        # Write the contents of the Deck List textbox to a file
        with open('resources/new_deck.txt', 'w') as f:
            f.write(values['-DECK-'])
        
        # Call the deck_compare.py script
        subprocess.run(['python', 'subprocesses/deck_compare.py'])
        
        # Call the card_info.py script
        subprocess.run(['python', 'subprocesses/card_info.py'])



        # Read the JSON data from the file
        with open('resources/deck_mana_costs.json', 'r') as f:
            data = json.load(f)

        # Get the values for pip counts
        C = data['C']
        W = data['W']
        U = data['U']
        B = data['B']
        R = data['R']
        G = data['G']

        # Update the InputText elements with the mana costs
        window['-COLORLESS_MANA-'].update(str(C))
        window['-WHITE_MANA-'].update(str(W))
        window['-BLUE_MANA-'].update(str(U))
        window['-BLACK_MANA-'].update(str(B))
        window['-RED_MANA-'].update(str(R))
        window['-GREEN_MANA-'].update(str(G))

        

        # Read the output from deck_mana_percentages.json file
        with open('resources/deck_mana_percentages.json', 'r') as f:
            contents = json.load(f)

        # Get the value for pip percentages
        C = contents['C'].replace('%', '')
        W = contents['W'].replace('%', '')
        U = contents['U'].replace('%', '')
        B = contents['B'].replace('%', '')
        R = contents['R'].replace('%', '')
        G = contents['G'].replace('%', '')        

        # Update the InputText element with the percent value
        window['-PERCENT_COLORLESS-'].update('%.2f%%' % (float(C)))
        window['-PERCENT_WHITE-'].update('%.2f%%' % (float(W)))
        window['-PERCENT_BLUE-'].update('%.2f%%' % (float(U)))
        window['-PERCENT_BLACK-'].update('%.2f%%' % (float(B)))
        window['-PERCENT_RED-'].update('%.2f%%' % (float(R)))
        window['-PERCENT_GREEN-'].update('%.2f%%' % (float(G)))




        # Read the output of card_info.py from the card_types.json file
        with open('resources/card_types.json', 'r') as f:
            card_types = json.load(f)

        # Update the InputText elements with the values from the JSON file
        window['-ENCHANTMENTS-'].update(str(card_types["Enchantments"]))
        window['-ARTIFACTS-'].update(str(card_types["Artifacts"]))
        window['-CREATURES-'].update(str(card_types["Creatures"]))
        window['-INSTANTS-'].update(str(card_types["Instants"]))
        window['-SORCERIES-'].update(str(card_types["Sorceries"]))
        window['-PLANESWALKERS-'].update(str(card_types["Planeswalkers"]))
        window['-LEGENDARIES-'].update(str(card_types["Legendaries"]))



        # Read the output of card_info.py from the card_types_percentages.json file
        with open('resources/card_type_percentages.json', 'r') as f:
            contents = json.load(f)

        # Update the InputText elements with the values from the JSON file
        window['-PERCENT_ENCHANTMENTS-'].update(str(contents["Enchantments"]) + "%")
        window['-PERCENT_ARTIFACTS-'].update(str(contents["Artifacts"]) + "%")
        window['-PERCENT_CREATURES-'].update(str(contents["Creatures"]) + "%")
        window['-PERCENT_INSTANTS-'].update(str(contents["Instants"]) + "%")
        window['-PERCENT_SORCERIES-'].update(str(contents["Sorceries"]) + "%")
        window['-PERCENT_PLANESWALKERS-'].update(str(contents["Planeswalkers"]) + "%")
        window['-PERCENT_LEGENDARIES-'].update(str(contents["Legendaries"]) + "%")




        # Read the output of card_info.py from the creature_subtypes.txt file
        with open('resources/creature_subtypes.json', 'r') as f:
            land_suggestions = json.load(f)

        # Create a string representation of the list
        land_suggestions_str = '\n'.join([f"{subtype}: {count}" for subtype, count in land_suggestions])

        # Update with creature subtype descending list
        window['-TRIBAL-'].update(land_suggestions_str)

        # Read the output of card_info.py from the land_suggestions.txt file
        with open('resources/land_suggestions.txt', 'r') as f:
            land_suggestions = f.read()
        
        # Update the Best Possible Lands textbox with the land suggestions
        window['-LANDS-'].update(land_suggestions)

    # If the 'Fetch' button is clicked
    if event == '-FETCH-':
        card_names = values['-LANDS-'].strip().split('\n')
        card_names = [card.split(' ', 1)[-1] if card.split(' ', 1)[0].isdigit() else card for card in card_names]
        print('Fetching images for cards:', card_names)  # Debug statement


        # Get the image bytes for each entered card name and store them in a list
        image_bytes_list = []
        for card_name in card_names:
            image_bytes = get_card_image(card_name)
            if image_bytes is not None:
                image_bytes_list.append(image_bytes)
        
        # Display the first image in the list (if there is one)
        current_image_index = 0
        if image_bytes_list:
            window['-IMAGE-'].update(data=image_bytes_list[0])

    # If the 'Previous' button is clicked
    elif event == '-PREV-':
        if current_image_index > 0:
            current_image_index -= 1
            window['-IMAGE-'].update(data=image_bytes_list[current_image_index])

    # If the 'Next' button is clicked
    elif event == '-NEXT-':
        if current_image_index < len(image_bytes_list) - 1:
            current_image_index += 1
            window['-IMAGE-'].update(data=image_bytes_list[current_image_index])


# Close the PySimpleGUI window
window.close()
