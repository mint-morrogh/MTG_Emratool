import requests
import csv

def fetch_card_info(card_name):
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching info for {card_name}")
        return None

def update_collection(file_path, csv_path):
    # Load existing collection from CSV
    existing_collection = []
    with open(csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            existing_collection.append(row)
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    deck_name = None
    commander = None
    main_cards = []
    
    for line in lines:
        line = line.strip()
        if line.startswith("Deck Name:"):
            deck_name = line.split(":")[1].strip()
        elif line.startswith("Commander:"):
            commander = line.split(":")[1].strip()
        elif line.startswith("Main:"):
            continue
        else:
            main_cards.append(line)
    
    # Update the collection
    new_collection = []
    deck_cards = {card['Card Name'] for card in existing_collection if card['Deck'] == deck_name}
    removed_cards = deck_cards.copy()

    for card_name in main_cards:
        card_info = fetch_card_info(card_name)
        if card_info:
            new_entry = {
                'Deck': deck_name,
                'Commander': commander,
                'Card Name': card_info['name'],
                'Card Type': card_info['type_line'],
                'Quantity': 1  # Adjust if tracking multiples
            }
            new_collection.append(new_entry)
            if card_name in removed_cards:
                removed_cards.remove(card_name)
    
    # Keep cards not in this deck but in the collection
    for card in existing_collection:
        if card['Deck'] != deck_name or card['Card Name'] in removed_cards:
            card['Deck'] = ''  # Unassign deck
            new_collection.append(card)
    
    # Write the updated collection back to CSV
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['Deck', 'Commander', 'Card Name', 'Card Type', 'Quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_collection)

if __name__ == "__main__":
    update_collection('deck_list.txt', 'mtg_collection.csv')
