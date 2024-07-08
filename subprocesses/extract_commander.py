import re
import json


def extract_commander_id(file_path, output_file):
    # Open and read the text file
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find the line with the Commander and extract the name
    for i in range(len(lines)):
        if lines[i].startswith('Commander:'):
            commander_name = lines[i+1].replace('1', '').replace("'", "").replace(
                ",", "").replace(":", "").replace("  ", " ").strip().lower().replace(" ", "-")
            break

    # Create a dictionary with the formatted commander name
    commander_dict = {"commander_id": commander_name}

    # Write the dictionary to a JSON file
    with open(output_file, 'w') as f:
        json.dump(commander_dict, f)


extract_commander_id('resources/new_deck.txt',
                     'resources/EDHScraper/commander_id.json')
