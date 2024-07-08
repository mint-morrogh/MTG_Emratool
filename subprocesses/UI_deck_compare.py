import subprocess
import PySimpleGUI as sg

sg.theme('DarkBlue2')

# Define the PySimpleGUI layout
layout = [[sg.Text('Old Deck List:', font=('Helvetica', 10, 'bold'))],
        [sg.Multiline(size=(80, 20), key='-OLD-', font=('Helvetica', 12), pad=(0, 10))],
        [sg.Text('New Deck List:', font=('Helvetica', 10, 'bold'))],
        [sg.Multiline(size=(80, 20), key='-NEW-', font=('Helvetica', 12), pad=(0, 10))],
        [sg.Button('Compare', bind_return_key=True, size=(10,2), button_color=('white', '#007F5F'), pad=(320, 10))],
        [sg.Text('Deck Difference:', font=('Helvetica', 12, 'bold'), text_color='white', pad=((300, 0), (20, 10)))],
        [sg.Multiline(size=(80, 20), key='-DIFF-', disabled=True, font=('Helvetica', 12))]]

def run_interface():
    # Create a PySimpleGUI window
    window = sg.Window('Text Converter', layout)

    # Display the window
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break
        elif event == 'Compare':
            # Get the input text from the left text box
            old_text = values['-OLD-']
            new_text = values['-NEW-']

            # Write the input text to files
            with open('resources/old_deck.txt', 'w') as f:
                f.write(old_text)
            with open('resources/new_deck.txt', 'w') as f:
                f.write(new_text)

            # Run the deck_compare.py script
            subprocess.run(['python', 'subprocesses/deck_compare.py'])

            # Read the output text from the deck_compare.py script
            with open('resources/diff.txt', 'r') as f:
                diff_text = f.read()

            # Update the difference text box
            window['-DIFF-'].update(diff_text)

    # Close the window
    window.close()

# Run the PySimpleGUI interface
run_interface()
