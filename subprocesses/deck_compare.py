import re


# put your new decklist into new_deck.txt
# if applicable put your old decklist (if you want to compare the two) into old_deck.txt
# difference between the two are saved in diff.txt
# this is tested for forge and moxfield so far 


######################################
def clean_deck_file(filename):
    # open the file in read mode
    with open(filename, 'r') as f:
        # read the contents of the file
        file_contents = f.read()

    # find the start and end indices of the "Main:" section
    start_index = file_contents.find("Main:")
    end_index = file_contents.find("Sideboard:")

    if start_index == -1 or end_index == -1:
        print(f"'Main:' or 'Sideboard:' not found in {filename}. Cleaning up the card list...")
        # remove set code and card number and write to the file
        formatted_list = []
        with open(filename, 'r') as f:
            for line in f:
                # Remove set code and card number
                line = re.sub(r'\s*\([^)]*\)\s*\d*[a-z]*', '', line)
                # Extract quantity and card name
                match = re.match(r'(\d+)\s+(.+)', line)
                if match:
                    quantity = match.group(1)
                    card_name = match.group(2)
                    formatted_list.append(f"{quantity} {card_name}")

        # Write the formatted list back to the file
        with open(filename, 'w') as f:
            for card in formatted_list:
                f.write(card + '\n')
        return

    # extract the "Main:" section
    main_section = file_contents[start_index:end_index]

    # remove the commander from the main section
    commander_index = main_section.index('\n') + 1
    main_section = main_section[commander_index:]

    # open the file in write mode
    with open(filename, 'w') as f:
        # write the "Main:" section back to the file
        f.write(main_section)

    # remove everything but quantity and card name
    # this is important if list is pulled in from moxfield or something
    formatted_list = []
    with open(filename, 'r') as f:
        for line in f:
            # Remove set code and card number
            line = re.sub(r'\s*\([^)]*\)\s*\d*[a-z]*', '', line)
            # Extract quantity and card name
            match = re.match(r'(\d+)\s+(.+)', line)
            if match:
                quantity = match.group(1)
                card_name = match.group(2)
                formatted_list.append(f"{quantity} {card_name}")

    # Write the formatted list back to the file
    with open(filename, 'w') as f:
        for card in formatted_list:
            f.write(card + '\n')

########################################

clean_deck_file('resources/old_deck.txt')
clean_deck_file('resources/new_deck.txt')

with open("resources/old_deck.txt", "r") as f:
    old_deck = [line.strip() for line in f.readlines()]

with open("resources/new_deck.txt", "r") as f:
    new_deck = [line.strip() for line in f.readlines()]

old_dict = {}
new_dict = {}

card_regex = r'^(\d+)\s+(.*)$'

for card in old_deck:
    match = re.match(card_regex, card)
    if match:
        quantity = int(match.group(1))
        name = match.group(2)
        old_dict[name] = quantity

for card in new_deck:
    match = re.match(card_regex, card)
    if match:
        quantity = int(match.group(1))
        name = match.group(2)
        new_dict[name] = quantity

old_only = {}
new_only = {}

total_cut_cards = 0

for name, quantity in old_dict.items():
    if name not in new_dict:
        old_only[name] = quantity
        total_cut_cards += quantity
    elif new_dict[name] < quantity:
        old_only[name] = quantity - new_dict[name]
        total_cut_cards += old_only[name]

for name, quantity in new_dict.items():
    if name not in old_dict:
        new_only[name] = quantity
    elif old_dict[name] < quantity:
        new_only[name] = quantity - old_dict[name]

with open("resources/diff.txt", "w") as f:
    f.write(f"Cards only in old deck ({total_cut_cards} cut cards):\n\n")
    for name, quantity in old_only.items():
        f.write(f"{quantity} {name}\n")

    f.write("\n\nNew cards to get:\n\n")
    for name, quantity in new_only.items():
        f.write(f"{quantity} {name}\n")