import time
import requests
import csv
from collections import defaultdict

def fetch_card_info(card_name):
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    response = requests.get(url)
    time.sleep(0.1)  # Add a 100 ms delay between requests
    if response.status_code == 200:
        print(f"Fetched info for {card_name}")  # Debugging
        card_info = response.json()
        # Replace problematic characters
        for key in card_info:
            if isinstance(card_info[key], str):
                card_info[key] = card_info[key].replace('�', '-')
        return card_info
    else:
        print(f"Error fetching info for {card_name}: {response.status_code}")
        return None

def parse_type_line(type_line):
    type_parts = type_line.split(' — ')
    card_type = type_parts[0] if len(type_parts) > 0 else ""
    subtype = type_parts[1] if len(type_parts) > 1 else ""
    return card_type, subtype

def update_collection(file_path, csv_path, collected_type):
    if collected_type == 'Forge':
        collected_status = 'Forge - Ready For Order'
    elif collected_type == 'Unassigned':
        collected_status = 'Unassigned'
    else:
        collected_status = 'Paper - Owned Card'
    
    existing_collection = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_collection.append(row)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    if not lines:
        print(f"No data found in {file_path}. Skipping...")
        return

    deck_name = None
    commander = None
    card_count = defaultdict(int)  # To track quantity of each card
    new_collection = existing_collection[:]  # Start with existing collection
    unassigned_cards = []
    
    if collected_type == 'Unassigned':
        for line in lines:
            card_name = line.strip()
            if card_name:
                card_count[card_name] += 1
        # Process unassigned cards directly
        for card_name, quantity in card_count.items():
            process_card(card_name, quantity, 'Unassigned', '', '', existing_collection, new_collection, unassigned_cards)
    else:
        for line in lines:
            line = line.strip()
            
            if line.startswith("Deck:"):
                if deck_name:
                    # Remove the old version of the deck from new_collection before processing the new one
                    new_collection = [card for card in new_collection if not (card['Deck'] == deck_name and card['Collected'] == collected_status)]
                    process_deck(deck_name, commander, card_count, existing_collection, new_collection, unassigned_cards, collected_status)
                deck_name = line.split(":")[1].strip()
                card_count = defaultdict(int)
                print(f"Processing deck: {deck_name}") 
        
            elif line.startswith("Commander:"):
                commander = line.split("1 ", 1)[1].strip() if "1 " in line else line.split(":")[1].strip()
                print(f"Commander: {commander}") 
            
            elif line.startswith("Main:"):
                continue
            
            elif line.startswith("Sideboard:"):
                continue  # Skip sideboard cards
            
            elif line:
                quantity, card_name = (int(line.split(" ", 1)[0]), line.split(" ", 1)[1]) if line[0].isdigit() else (1, line.strip())
                card_count[card_name] += quantity
                print(f"Added card: {card_name} x{quantity}") 
    
        if deck_name:
            # If uploading a Forge deck, check if there's an existing Paper deck with the same name
            if collected_type == 'Forge':
                paper_deck_cards = {
                    card['Card Name']: int(card['Quantity'])
                    for card in new_collection
                    if card['Deck'] == deck_name and card['Collected'] == 'Paper - Owned Card'
                }
                # Only add new cards that are not already in the paper deck
                card_count = {
                    card_name: quantity
                    for card_name, quantity in card_count.items()
                    if card_name not in paper_deck_cards or quantity > paper_deck_cards[card_name]
                }

            # Remove any existing Forge deck with the same name before adding the new Forge deck
            new_collection = [card for card in new_collection if not (card['Deck'] == deck_name and card['Collected'] == 'Forge - Ready For Order')]
            # Now remove the old version of the Paper deck
            new_collection = [card for card in new_collection if not (card['Deck'] == deck_name and card['Collected'] == collected_status)]
            process_deck(deck_name, commander, card_count, existing_collection, new_collection, unassigned_cards, collected_status)
    
    update_collected_quantities(new_collection + unassigned_cards)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Collected', 'Deck', 'Commander', 'Card Name', 'Card Type', 'Subtype', 'Mana Cost', 'CMC', 'Colors', 'Oracle Text', 'Power', 'Toughness', 'Rarity', 'Set Name', 'Set Code', 'Collector Number', 'Artist', 'Quantity', 'Collected Quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_collection + unassigned_cards)
    print(f"Updated CSV: {csv_path}") 

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("")
    print(f"Cleared contents of {file_path}")

def process_card(card_name, quantity, collected_status, deck_name, commander, existing_collection, new_collection, unassigned_cards):
    card_info = fetch_card_info(card_name)
    if card_info:
        card_type, subtype = parse_type_line(card_info['type_line'])
        existing_card = next((card for card in new_collection if card['Card Name'] == card_name and card['Collected'] == collected_status and card['Deck'] == deck_name), None)
        if existing_card:
            existing_card['Quantity'] += quantity
        else:
            new_entry = {
                'Collected': collected_status,
                'Deck': deck_name if collected_status != 'Unassigned' else '',
                'Commander': commander if collected_status != 'Unassigned' else '',
                'Card Name': card_info['name'],
                'Card Type': card_type,
                'Subtype': subtype,
                'Mana Cost': card_info.get('mana_cost', ''),
                'CMC': card_info.get('cmc', ''),
                'Colors': ', '.join(card_info.get('colors', [])),
                'Oracle Text': card_info.get('oracle_text', ''),
                'Power': card_info.get('power', ''),
                'Toughness': card_info.get('toughness', ''),
                'Rarity': card_info.get('rarity', ''),
                'Set Name': card_info.get('set_name', ''),
                'Set Code': card_info.get('set', ''),
                'Collector Number': card_info.get('collector_number', ''),
                'Artist': card_info.get('artist', ''),
                'Quantity': quantity,
                'Collected Quantity': 0
            }
            new_collection.append(new_entry)
        print(f"Processed card: {card_name} x{quantity} for {collected_status if collected_status != 'Unassigned' else 'Unassigned'}")

def process_deck(deck_name, commander, card_count, existing_collection, new_collection, unassigned_cards, collected_status):
    current_deck_cards = {card['Card Name']: card for card in existing_collection if card['Deck'] == deck_name and card['Collected'] == collected_status}

    for card_name, quantity in card_count.items():
        process_card(card_name, quantity, collected_status, deck_name, commander, existing_collection, new_collection, unassigned_cards)
    
    # For Forge decks, simply remove the old version without unassigning cards
    if collected_status.startswith('Forge'):
        return

    for card in current_deck_cards.values():
        if card['Card Name'] not in card_count:
            card['Collected'] = 'Unassigned'
            card['Deck'] = ''
            unassigned_cards.append(card)
            print(f"Unassigned card: {card['Card Name']}")

def update_collected_quantities(collection):
    """Update the 'Collected Quantity' for each card based on the total across all 'Paper' decks and unassigned cards."""
    collected_totals = defaultdict(int)

    for card in collection:
        if card['Collected'] == 'Paper - Owned Card' or card['Collected'] == 'Unassigned':
            collected_totals[card['Card Name']] += int(card['Quantity'])

    for card in collection:
        if card['Card Name'] in collected_totals and (card['Collected'] == 'Paper - Owned Card' or card['Collected'] == 'Unassigned'):
            card['Collected Quantity'] = collected_totals[card['Card Name']]

if __name__ == "__main__":
    update_collection('forge_list.txt', 'mtg_collection.csv', 'Forge')
    update_collection('paper_list.txt', 'mtg_collection.csv', 'Paper')
    update_collection('unassigned_list.txt', 'mtg_collection.csv', 'Unassigned')
