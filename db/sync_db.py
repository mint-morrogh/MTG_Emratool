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
    main_cards = []
    new_collection = []

    for line in lines:
        line = line.strip()
        
        if line.startswith("Deck:"):
            if deck_name:
                process_deck(deck_name, commander, main_cards, existing_collection, new_collection, collected_status)
            deck_name = line.split(":")[1].strip()
            main_cards = []
            # Remove all cards from the deck in Forge if converting to Paper
            if collected_status.startswith('Paper'):
                existing_collection = [card for card in existing_collection if not (card['Deck'] == deck_name and card['Collected'].startswith('Forge'))]
            print(f"Processing deck: {deck_name}") 
        
        elif line.startswith("Commander:"):
            if "1 " in line:
                commander = line.split("1 ", 1)[1].strip()
            else:
                commander = line.split(":")[1].strip()
            print(f"Commander: {commander}") 
        
        elif line.startswith("Main:"):
            continue
        
        elif line.startswith("Sideboard:"):
            continue  
        
        elif line:
            if line[0].isdigit():
                quantity, card_name = line.split(" ", 1)
                quantity = int(quantity)
            else:
                quantity = 1
                card_name = line.strip()
            
            main_cards.append((card_name, quantity))
            print(f"Added card: {card_name} x{quantity}") 
    
    if deck_name:
        process_deck(deck_name, commander, main_cards, existing_collection, new_collection, collected_status)
    
    # Check for sold Paper cards
    collected_totals = defaultdict(int)
    for card in new_collection:
        if card['Collected'].startswith('Paper'):
            collected_totals[card['Card Name']] += int(card['Quantity'])
    
    for card in new_collection:
        if card['Card Name'] in collected_totals and card['Collected'].startswith('Paper'):
            card['Collected Quantity'] = collected_totals[card['Card Name']]
    
    new_collection.extend(existing_collection)  # Add remaining cards

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Collected', 'Deck', 'Commander', 'Card Name', 'Card Type', 'Subtype', 'Mana Cost', 'CMC', 'Colors', 'Oracle Text', 'Power', 'Toughness', 'Rarity', 'Set Name', 'Set Code', 'Collector Number', 'Artist', 'Quantity', 'Collected Quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for card in new_collection:
            card['Quantity'] = str(card['Quantity'])
            card['Collected Quantity'] = str(card['Collected Quantity'])
            writer.writerow(card)
    print(f"Updated CSV: {csv_path}") 

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("")
    print(f"Cleared contents of {file_path}")

def process_deck(deck_name, commander, main_cards, existing_collection, new_collection, collected_status):
    removed_cards = {card['Card Name'] for card in existing_collection if card['Deck'] == deck_name and card['Collected'] == collected_status}
    
    for card_name, quantity in main_cards:
        card_info = fetch_card_info(card_name)
        if card_info:
            card_type, subtype = parse_type_line(card_info['type_line'])
            for card in existing_collection:
                if card['Card Name'] == card_name and card['Deck'] == deck_name:
                    if card['Collected'].startswith('Forge') and collected_status.startswith('Paper'):
                        card['Collected'] = collected_status
                        card['Quantity'] = int(card['Quantity']) + quantity
                        if card_name in removed_cards:
                            removed_cards.remove(card_name)
                        new_collection.append(card)
                        break
                    elif card['Collected'].startswith('Paper'):
                        card['Quantity'] = int(card['Quantity']) + quantity
                        if card_name in removed_cards:
                            removed_cards.remove(card_name)
                        new_collection.append(card)
                        break
            else:
                new_entry = {
                    'Collected': collected_status,
                    'Deck': deck_name,
                    'Commander': commander,
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
                if card_name in removed_cards:
                    removed_cards.remove(card_name)
            print(f"Processed card: {card_name} x{quantity} for {deck_name}") 

if __name__ == "__main__":
    update_collection('forge_list.txt', 'mtg_collection.csv', 'Forge')
    update_collection('paper_list.txt', 'mtg_collection.csv', 'Paper')
