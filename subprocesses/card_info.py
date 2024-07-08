import requests
import json
import random
import sys
import os
from collections import Counter
import re

# Add your list to "new_deck.txt"
# run deck_compare.py to format the list
# run this to get your mana percentages and best lands to add
# lands suggestions are saved in land_suggestions.txt
# this really doesn't work for mono colored or colorless decks

######################################

### Main API Call to Skryfall ###

def get_card_info(card_name):
    api_endpoint = "https://api.scryfall.com/cards/named"
    params = {"exact": card_name}
    response = requests.get(api_endpoint, params=params)
    #if response.status_code == 404:
    #    print(f"API Not reachable or invalid decklist.")
    #    sys.exit()
    card_data = json.loads(response.text)
    if card_data.get("object") != "card":
        print(f"Card not found: {card_name}")
        sys.exit()
    elif "mana_cost" not in card_data:
        return None
    else:
        card_info = {
            "name": card_data["name"],
            "mana_cost": card_data["mana_cost"],
            "colors": card_data["colors"],
            "type": card_data["type_line"]
        }
        return card_info

### /Main API Call to Skryfall ###

### Tribal Detection ###

def get_deck_creature_types_json(decklist_file):
    creature_types = {}
    with open(decklist_file, 'r') as f:
        for line in f:
            if line.strip().isdigit():
                continue  # skip lines that only contain a number (sideboard count)
            line = line.strip().split()
            count = int(line[0])
            name = ' '.join(line[1:])
            card_info = get_card_info(name)
            if card_info is not None and "Creature" in card_info["type"]:
                creature_subtype = card_info["type"].split("Creature")[-1].strip()
                creature_types[creature_subtype] = creature_types.get(creature_subtype, 0) + count

    # Sort creature types by count in descending order
    creature_types = {k: v for k, v in sorted(creature_types.items(), key=lambda item: item[1], reverse=True)}

    # Write to JSON file
    with open("resources/creature_subtypes.json", 'w') as f:
        json.dump(creature_types, f)

    # Read from JSON file
    with open("resources/creature_subtypes.json", 'r') as f:
        creature_types = json.load(f)

    # Format and return dictionary
    creature_types = {k.replace('—', '-').strip(): v for k, v in creature_types.items()}
    return creature_types

def expand_creature_counts_json():
    # Read from JSON file
    with open('resources/creature_subtypes.json', 'r') as f:
        creature_types = json.load(f)

    # Expand creature counts and write to JSON file
    expanded_creatures = []
    for creature_type, count in creature_types.items():
        for i in range(count):
            expanded_creatures.append(creature_type)

    with open('resources/creature_subtypes_count.json', 'w') as out_file:
        json.dump(expanded_creatures, out_file)

    # Delete input file and rename output file
    os.remove('resources/creature_subtypes.json')
    os.rename('resources/creature_subtypes_count.json', 'resources/creature_subtypes.json')

def group_creature_subtypes_by_count_json():
    # Read the creature subtypes from the file
    with open("resources/creature_subtypes.json", "r") as f:
        creature_lines = json.load(f)

    # Split the creature subtypes into individual words and count their occurrence
    word_counts = Counter(word for line in creature_lines for word in line.split())

    # Convert the word counts to a list of lists
    count_list = [[word.capitalize(), count] for word, count in word_counts.items()]

    # Sort the list by count, in descending order
    count_list.sort(key=lambda x: x[1], reverse=True)

    # Write the word counts to a file
    with open("resources/creature_subtypes_count.json", "w") as f:
        json.dump(count_list, f)

    # Delete the original file and rename the new file
    os.remove("resources/creature_subtypes.json")
    os.rename("resources/creature_subtypes_count.json", "resources/creature_subtypes.json")
    with open("resources/creature_subtypes.json", "r") as f:
        data = json.load(f)

        new_data = []
        for item in data:
            if item[0] != "\u2014":
                new_data.append(item)

        with open("resources/creature_subtypes.json", "w") as f:
            json.dump(new_data, f)

def get_deck_creature_types_percentages_json():
    # Read the creature subtypes from the JSON file
    with open("resources/creature_subtypes.json", "r") as f:
        creature_data = json.load(f)

    # Calculate the total count of creature subtypes
    total_count = sum(item[1] for item in creature_data)

    # Calculate the percentages for each creature subtype
    creature_percentages = []
    for item in creature_data:
        count = item[1]
        creature = item[0]
        percentage = round(count / total_count * 100, 2)
        creature_percentages.append({"creature": creature, "percentage": percentage})

    # Write the percentages to a new JSON file
    with open("resources/creature_subtypes_percentages.json", "w") as f:
        json.dump(creature_percentages, f)

def check_high_tribal_percentage_json():
    with open('resources/creature_subtypes_percentages.json', 'r') as f:
        creature_data = json.load(f)
        first_subtype = creature_data[0]['creature']
        if first_subtype == 'Shapeshifter' or first_subtype == 'Changeling':
            return {'tribal': True}
        percentage = creature_data[0]['percentage']
        if percentage > 43:
            return {'tribal': True}
    return {'tribal': False}




### / Tribal Detection ###


### Mana Math ###

def get_deck_mana_costs_json(decklist_file, output_file):
    with open(decklist_file) as f:
        decklist = f.readlines()
    mana_costs = {"C": 0, "W": 0, "U": 0, "B": 0, "R": 0, "G": 0}
    for line in decklist:
        line_parts = line.strip().split(" ", 1)
        if len(line_parts) != 2:
            continue
        card_count = int(line_parts[0])
        card_name = line_parts[1]
        card_info = get_card_info(card_name)
        if card_info is None:
            continue
        else:
            mana_cost = card_info["mana_cost"]
            for symbol in mana_cost:
                if symbol in mana_costs:
                    mana_costs[symbol] += card_count
                elif symbol == "{C}" or (symbol.isdigit() and int(symbol) > 0):
                    mana_costs["C"] += card_count
    C_mana = mana_costs.get('C', 0)
    W_mana = mana_costs.get('W', 0)
    U_mana = mana_costs.get('U', 0)
    B_mana = mana_costs.get('B', 0)
    R_mana = mana_costs.get('R', 0)
    G_mana = mana_costs.get('G', 0)
    mana_costs_json = {
        "C": C_mana,
        "W": W_mana,
        "U": U_mana,
        "B": B_mana,
        "R": R_mana,
        "G": G_mana
    }
    with open(output_file, 'w') as f:
        json.dump(mana_costs_json, f)

def get_deck_mana_color_percentages_json():
    # read the mana costs from the file
    with open('resources/deck_mana_costs.json', 'r') as f:
        mana_costs = json.load(f)

    # calculate the total mana cost
    total_mana = sum(mana_costs.values())

    # calculate the percentages and round them to 2 decimal places
    percentages = {k: round(v / total_mana * 100, 2) for k, v in mana_costs.items()}

    # write the percentages to the file
    with open('resources/deck_mana_percentages.json', 'w') as f:
        json.dump({k: f"{v:.2f}%" for k, v in percentages.items()}, f)

### / Mana Math ###

### Card Type Counts ###

# called by get_landbase
def get_deck_card_types(decklist_file):
    with open(decklist_file) as f:
        decklist = f.readlines()
    card_types = {}
    for line in decklist:
        line_parts = line.strip().split(" ", 1)
        if len(line_parts) != 2:
            continue
        card_count = int(line_parts[0])
        card_name = line_parts[1]
        card_info = get_card_info(card_name)
        if card_info is None:
            continue
        else:
            card_type = card_info["type"].split(" — ")[0]
            if card_type not in card_types:
                card_types[card_type] = 0
            card_types[card_type] += card_count
    
    # Count all types of enchantments
    enchantment_count = 0
    for card_type, count in card_types.items():
        if "Enchantment" in card_type:
            enchantment_count += count
    card_types["Enchantments"] = enchantment_count
    
    # Count all types of artifacts
    artifact_count = 0
    for card_type, count in card_types.items():
        if "Artifact" in card_type:
            artifact_count += count
    card_types["Artifacts"] = artifact_count
    
    # Count all types of creatures
    creature_count = 0
    for card_type, count in card_types.items():
        if "Creature" in card_type:
            creature_count += count
    card_types["Creatures"] = creature_count
    
    # Count all types of instants
    instant_count = card_types.get("Instant", 0)
    for card_type, count in card_types.items():
        if "Instant" in card_type and card_type != "Instant":
            instant_count += count
    card_types["Instants"] = instant_count
    
    # Count all types of sorceries
    sorcery_count = card_types.get("Sorcery", 0)
    for card_type, count in card_types.items():
        if "Sorcery" in card_type and card_type != "Sorcery":
            sorcery_count += count
    card_types["Sorceries"] = sorcery_count
    
    # Count all types of planeswalkers
    planeswalker_count = card_types.get("Planeswalker", 0)
    for card_type, count in card_types.items():
        if "Planeswalker" in card_type and card_type != "Planeswalker":
            planeswalker_count += count
    card_types["Planeswalkers"] = planeswalker_count
    
    # Count all types of legendary cards
    legendary_count = 0
    for card_type, count in card_types.items():
        if "Legendary" in card_type:
            legendary_count += count
    card_types["Legendaries"] = legendary_count
    
    return card_types

### / Card Type Counts ###



### Land Calculator ###

def get_landbase(decklist_file):
    # count all card types that are spells
    card_types = get_deck_card_types(decklist_file)

    with open("resources/card_types.json", "w") as f:
        enchantment_count = card_types.get("Enchantments", 0)
        artifact_count = card_types.get("Artifacts", 0)
        creature_count = card_types.get("Creatures", 0)
        instant_count = card_types.get("Instants", 0)
        sorcery_count = card_types.get("Sorceries", 0)
        planeswalker_count = card_types.get("Planeswalkers", 0)
        legendary_count = card_types.get("Legendaries", 0)
        
        data = {
            "Enchantments": enchantment_count,
            "Artifacts": artifact_count,
            "Creatures": creature_count,
            "Instants": instant_count,
            "Sorceries": sorcery_count,
            "Planeswalkers": planeswalker_count,
            "Legendaries": legendary_count
        }
        
        json.dump(data, f, indent=4)

    ##################################################
    # calculate % of spells
    with open("resources/card_types.json", "r") as f:
        data = json.load(f)

        total_count = sum(data.values()) - data["Legendaries"] # exclude legendary cards
        percentages = {}

        with open("resources/card_type_percentages.json", "w") as f:
            for card_type, count in data.items():
                if card_type != "Legendaries":
                    percentage = round(count / total_count * 100, 2)
                else:
                    non_legendary_count = sum(data.values()) - data["Legendaries"]
                    percentage = round(count / non_legendary_count * 100, 2) # percentage of legendaries in non-legendary spells
                percentages[card_type] = percentage

            json.dump(percentages, f, indent=4)








    # Get mana color percentages from decklist
    with open('resources/deck_mana_percentages.json', 'r') as f:
        deck_colors = json.load(f)
        deck_colors = {k: float(v.strip('%')) for k, v in deck_colors.items()}
    # Count number of unique colors that isn't colorless
    num_colors = sum(1 for color in deck_colors if color != 'C' and deck_colors[color] > 0)
    # add up all colored mana, ignores colorless mana for calculations
    total_WUBRG = sum(float(str(deck_colors[c]).strip('%')) for c in deck_colors if c != 'C')





    # Define types of lands to consider


    # S Tier



    staples = {
        "Command Tower",
        "Urza's Saga"
    }

    # Conditional Lands based on majority color

    percent45_black = {
        "Cabal Coffers": ["B"],
        "Urborg": ["B"],
        "Urborg, Tomb of Yawgmoth": ["B"],
        "Bojuka Bog": ["B"],
        "Agadeem's Awakening": ["B"]
    }

    percent45_red = {
        "Hammerheim": ["R"],
        "Valakut, The Molten Pinnacle": ["R"],
        "Shatterskull Smashing": ["R"]
    }

    percent45_green = {
        "Yavimaya, Cradle of Growth": ["G"],
        "Pendelhaven": ["G"],
        "Yavimaya Hollow": ["G"]
    } 

    percent45_blue = {
        "Mystic Sanctuary": ["U"]
    }

    percent45_white = {
        "Kor Haven": ["W"],
        "Emeria's Call": ["W"]
    }

    # If the deck runs green at all, put Gaea's Cradle in it

    Gaeas = {
        "Gaea's Cradle": ["G"]
    }

    # Staples based on color count 

    five_color_staples = {
        "The World Tree"
    }

    four_or_more_staples = {
        "Cascading Cataracts",
        "Reflecting Pool",
        "Spire of Industry"
    }

    three_or_more_staples = {
        "Exotic Orchard"
    }

    two_or_more_staples = {
        "Field of the Dead"
    }

    three_or_less_staples = {
        "Ancient Tomb",
        "Strip Mine"
    }

    two_or_less_staples = {
        "Nykthos, Shrine to Nyx",
        "War Room"
    }

    # For tribal 
    
    tribal_staples = {
        "Cavern of Souls",
        "Secluded Courtyard"
    }

    # enchantment deck thats runs W - serra's sanctum, Hall of Heloid's generosity,
    # runs black, and likes to sacrifice - phyrexian tower
    # likes to sacrifice - high market

    # deck is black and green only (and likes to sacrifice) - Grim Backwoods
    # deck is red and green only - Kessig wolf run / Skarrg, the Rage Pits
    # deck is green and white only - gavony township 
    # deck is white and blue only - Moorland Haunt
    # deck is blue and black only (and likes to mill) - Nephalia Drownyard
    # deck is white and black only - Vault of the Archangel
    # deck is red and white only - Slayer's Stronghold
    # deck is red and blue only - Desolate Lighthouse
    # deck is green and blue only (and likes playing at instant speed) - Alchemist's Refuge


    # I want more card draw - bonders' enclave
    # I play a ton of instants and sorceries - Boseiju, Who Shelters All
    # My deck is commander combat focused - Witch's Clinic
    # My commander is very expensive to play - command beacon
    # lifegain lands - .....
    # artifact deck or your deck likes treasures - treasure vault
    # artifact deck - mishra's workshop, artifact lands (for colors of deck) darksteel citadel, 
    # artifact deck that has blue - academy ruins
    # I like to Proliferate - Karn's bastion, vivid lands


    # utilities 
    #   utility lands on avg based of color amount
    #   0-5 (4+ colors)  / 5-8 (3 colors) /  7-9 (2 colors) /  10-12 (1 color)


    #  arcane lighthouse, winding canyons, opal palace

    
    rainbow_lands = {
        "Mana Confluence",
        "City of Brass",
        "Path of Ancestry"
    }
    
    dual_lands = {
        "Tundra": ["W", "U"],
        "Underground Sea": ["U", "B"],
        "Badlands": ["B", "R"],
        "Taiga": ["R", "G"],
        "Savannah": ["G", "W"],
        "Scrubland": ["W", "B"],
        "Volcanic Island": ["U", "R"],
        "Bayou": ["B", "G"],
        "Plateau": ["R", "W"],
        "Tropical Island": ["G", "U"]
    }
    fetch_lands = {
        "Flooded Strand": ["W", "U"],
        "Polluted Delta": ["B", "U"],
        "Bloodstained Mire": ["B", "R"],
        "Wooded Foothills": ["R", "G"],
        "Windswept Heath": ["G", "W"],
        "Marsh Flats": ["W", "B"],
        "Scalding Tarn": ["U", "R"],
        "Verdant Catacombs": ["B", "G"],
        "Arid Mesa": ["R", "W"],
        "Misty Rainforest": ["G", "U"]
    }

    shock_lands = {
        "Sacred Foundry": ["R", "W"],
        "Watery Grave": ["B", "U"],
        "Blood Crypt": ["B", "R"],
        "Temple Garden": ["G", "W"],
        "Breeding Pool": ["G", "U"],
        "Hallowed Fountain": ["W", "U"],
        "Stomping Ground": ["R", "G"],
        "Godless Shrine": ["B", "W"],
        "Overgrown Tomb": ["B", "G"]
    }

    crowd_lands = {
        "Sea of Clouds": ["W", "U"],
        "Morphic Pool": ["U", "B"],
        "Luxury Suite": ["B", "R"],
        "Spire Garden": ["R", "G"],
        "Bountiful Promenade": ["G", "W"],
        "Vault of Champions": ["W", "B"],
        "Training Center": ["U", "R"],
        "Undergrowth Stadium": ["B", "G"],
        "Spectator Seating": ["R", "W"],
        "Rejuvenating Springs": ["G", "U"]
    }
    
    slow_duals = {
        "Deserted Beach": ["W", "U"],
        "Shipwreck Marsh": ["U", "B"],
        "Haunted Ridge": ["B", "R"],
        "Rockfall Vale": ["R", "G"],
        "Overgrown Farmland": ["G", "W"],
        "Shattered Sanctum": ["W", "B"],
        "Stormcarved Coast": ["U", "R"],
        "Deathcap Glade": ["B", "G"],
        "Sundown Pass": ["R", "W"],
        "Dreamroot Cascade": ["G", "U"]
    }

    horizon_lands = {
        "Horizon Canopy": ["G", "W"],
        "Silent Clearing": ["W", "B"],
        "Fiery Islet": ["U", "R"],
        "Nurturing Peatland": ["B", "G"],
        "Sunbaked Canyon": ["R", "W"],
        "Waterlogged Grove": ["G", "U"]
    }


    # A Tier


    check_lands = {
        "Glacial Fortress": ["W", "U"],
        "Drowned Catacomb": ["U", "B"],
        "Dragonskull Summit": ["B", "R"],
        "Rootbound Crag": ["R", "G"],
        "Sunpetal Grove": ["G", "W"],
        "Isolated Chapel": ["W", "B"],
        "Sulfur Falls": ["U", "R"],
        "Woodland Cemetery": ["B", "G"],
        "Clifftop Retreat": ["R", "W"],
        "Hinterland Harbor": ["G", "U"]
    }

    pain_lands = {
        "Adarkar Wastes": ["W", "U"],
        "Underground River": ["U", "B"],
        "Sulfurous Springs": ["B", "R"],
        "Karplusan Forest": ["R", "G"],
        "Brushland": ["G", "W"],
        "Caves of Koilos": ["W", "B"],
        "Shivan Reef": ["U", "R"],
        "Llanowar Wastes": ["B", "G"],
        "Battlefield Forge": ["R", "W"],
        "Yavimaya Coast": ["G", "U"]
    }


    # B Tier


    # only fast in lands running lots of basics, could cut these
    tango_lands = {
        "Prairie Stream": ["W", "U"],
        "Sunken Hollow": ["U", "B"],
        "Smoldering Marsh": ["B", "R"],
        "Cinder Glade": ["R", "G"],
        "Canopy Vista": ["G", "W"]
    }

    filter_lands = {
        "Mystic Gate": ["W", "U"],
        "Sunken Ruins": ["U", "B"],
        "Graven Cairns": ["B", "R"],
        "Fire-Lit Thicket": ["R", "G"],
        "Wooded Bastion": ["G", "W"],
        "Fetid Heath": ["W", "B"],
        "Cascade Bluffs": ["U", "R"],
        "Twilight Mire": ["B", "G"],
        "Rugged Prairie": ["R", "W"],
        "Flooded Grove": ["G", "U"]
    }

    tri_lands = {
        "Jetmir's Garden": ["W", "G", "R"],
        "Ziatora's Proving Ground": ["B", "R", "G"],
        "Xander's Lounge": ["U", "B", "R"],
        "Raffine's Tower": ["W", "U", "B"],
        "Spara's Headquarters": ["G", "W", "U"],
        "Savage Lands": ["B", "R", "G"],
        "Seaside Citadel": ["G", "W", "U"],
        "Arcane Sanctum": ["B", "W", "U"],
        "Crumbling Necropolis": ["B", "R", "U"],
        "Jungle Shrine": ["G", "R", "W"]
    }

    cycling_lands = {
        "Irrigated Farmland": ["W", "U"],
        "Fetid Pools": ["U", "B"],
        "Canyon Slough": ["B", "R"],
        "Sheltered Thicket": ["R", "G"],
        "Scattered Groves": ["G", "W"]
    }

    legendary_monos = {
        "Eiganjo, Seat of the Empire": ["W"],
        "Otawara, Soaring City": ["U"],
        "Takenuma, Abandoned Mire": ["B"],
        "Sokenzan, Crucible of Defiance": ["R"],
        "Boseiju, Who Endures": {"G"}
    }

    # only for decks with heavy black in colors
    tainted_lands = {
        "Tainted Field": ["W", "B"],
        "Tainted Isle": ["U", "B"],
        "Tainted Peak": ["B", "R"],
        "Tainted Wood": ["B", "G"]
    }



    # C Tier

    snow_duals = {
        "Glacial Floodplain": ["W", "U"],
        "Ice Tunnel": ["U", "B"],
        "Sulfurous Mire": ["B", "R"],
        "Highland Forest": ["R", "G"],
        "Arctic Treeline": ["G", "W"],
        "Snowfield Sinkhole": ["W", "B"],
        "Volatile Fjord": ["U", "R"],
        "Woodland Chasm": ["B", "G"],
        "Alpine Meadow": ["R", "W"],
        "Rimewood Falls": ["G", "U"]
    }


    temple_lands = {
        "Temple of Enlightenment": ["W", "U"],
        "Temple of Deceit": ["U", "B"],
        "Temple of Malice": ["B", "R"],
        "Temple of Abandon": ["R", "G"],
        "Temple of Plenty": ["G", "W"],
        "Temple of Silence": ["W", "B"],
        "Temple of Epiphany": ["U", "R"],
        "Temple of Malady": ["B", "G"],
        "Temple of Triumph": ["R", "W"],
        "Temple of Mystery": ["G", "U"]
    }


    pathway_lands = {
        "Hengegate Pathway": ["W", "U"],
        "Clearwater Pathway": ["U", "B"],
        "Blightstep Pathway": ["B", "R"],
        "Cragcrown Pathway": ["R", "G"],
        "Branchloft Pathway": ["G", "W"],
        "Brightclimb Pathway": ["W", "B"],
        "Riverglide Pathway": ["U", "R"],
        "Darkbore Pathway": ["B", "G"],
        "Needleverge Pathway": ["R", "W"],
        "Barkchannel Pathway": ["G", "U"]
    }

    dnd_monos = {
        "Cave of the Frost Dragon": ["W"],
        "Hall of Storm Giants": ["U"],
        "Hive of the Eye Tyrant": ["B"],
        "Den of the Bugbear": ["R"],
        "Lair of the Hydra": {"G"}
    }

    snow_covered_monos = {
        "Snow-covered Plains": ["W"],
        "Snow-covered Island": ["U"],
        "Snow-covered Swamp": ["B"],
        "Snow-covered Mountain": ["R"],
        "Snow-covered Forest": ["G"]
    }

    # Build list of lands to include in landbase
    landbase = []

    # Add snow-covered basics
    if num_colors <= 2:
        for land_name, colors in snow_covered_monos.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # Add staples
    for land_name in staples:
        landbase.append(land_name)

    # If applicable, add Gaea's Cradle
    for land_name, colors in Gaeas.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                if 'G' in deck_colors:
                    landbase.append(land_name)

    # add rainbow_lands if deck has more than 1 color
    if num_colors >= 2:
        for land_name in rainbow_lands:
            landbase.append(land_name)

    # if color is 45% majority, add mono colored staples
    for land_name, colors in percent45_black.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                if deck_colors['B'] >= total_WUBRG * 0.45:
                    landbase.append(land_name)

    for land_name, colors in percent45_blue.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                if deck_colors['U'] >= total_WUBRG * 0.45:
                    landbase.append(land_name)

    for land_name, colors in percent45_green.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                if deck_colors['G'] >= total_WUBRG * 0.45:
                    landbase.append(land_name)

    for land_name, colors in percent45_red.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                if deck_colors['R'] >= total_WUBRG * 0.45:
                    landbase.append(land_name)

    for land_name, colors in percent45_white.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                if deck_colors['W'] >= total_WUBRG * 0.45:
                    landbase.append(land_name)
    
    # Color count staples
    if num_colors == 5:
        for land_name in five_color_staples:
            landbase.append(land_name)

    if num_colors >= 4:
        for land_name in four_or_more_staples:
            landbase.append(land_name)

    if num_colors >= 3:
        for land_name in three_or_more_staples:
            landbase.append(land_name)

    if num_colors >= 2:
        for land_name in two_or_more_staples:
            landbase.append(land_name)

    if num_colors <= 3:
        for land_name in three_or_less_staples:
            landbase.append(land_name)

    if num_colors <= 2:
        for land_name in two_or_less_staples:
            landbase.append(land_name)

    # Tribal Staples
    if tribal == True:
        for land_name in tribal_staples:
            landbase.append(land_name)



    # Prioritize dual lands
    for land_name, colors in dual_lands.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                landbase.append(land_name)

    # fetch lands
    for land_name, colors in fetch_lands.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                landbase.append(land_name)

    # shock lands
    for land_name, colors in shock_lands.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                landbase.append(land_name)

    # slow duals
    for land_name, colors in slow_duals.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                landbase.append(land_name)

    # crowd lands
    for land_name, colors in crowd_lands.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                landbase.append(land_name)

    # horizon lands (we want 2 at a maximum)
    if num_colors <= 3:
        horizon_count = 0
        for land_name, colors in horizon_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    if horizon_count < 2:
                        landbase.append(land_name)
                        horizon_count += 1
                    else:
                        break

    # check lands
    for land_name, colors in check_lands.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                landbase.append(land_name)

    # pain lands
    if num_colors <= 3:
        for land_name, colors in pain_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # tango lands
    if num_colors == 2:
        for land_name, colors in tango_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # tri lands
    if num_colors >= 3:
        for land_name, colors in tri_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # filter lands
    if num_colors <= 3:
        for land_name, colors in filter_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)
                
    # cycling lands
    for land_name, colors in cycling_lands.items():
        if all(color in deck_colors.keys() for color in colors):
            if all(deck_colors[color] > 0 for color in colors):
                landbase.append(land_name)

    # mono color legendary channel lands
    if num_colors <= 2:
        for land_name, colors in legendary_monos.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # tainted lands
    if num_colors <= 3 and 'B' in deck_colors:
        for land_name, colors in tainted_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # snow duals
    if num_colors >= 3:
        for land_name, colors in snow_duals.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # temple lands
    if num_colors == 2:
        for land_name, colors in temple_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # pathway lands
    if num_colors == 2:
        for land_name, colors in pathway_lands.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)

    # mono color dnd lands
    if num_colors <= 2:
        for land_name, colors in dnd_monos.items():
            if all(color in deck_colors.keys() for color in colors):
                if all(deck_colors[color] > 0 for color in colors):
                    landbase.append(land_name)
                                

    # Open file for writing
    with open('resources/land_suggestions.txt', 'w') as f:
        # Write the land suggestions to file
        for land in landbase:
            count = landbase.count(land)
            f.write(f"{count} {land}\n")

    # Return the landbase list
    return landbase

### / Land Calculator ### 
#####################################



# write all creature types sorted by keyword count to creature_subtypes.txt

get_deck_creature_types_json('resources/new_deck.txt')
expand_creature_counts_json()
group_creature_subtypes_by_count_json()
### determine if deck is a tribal deck
get_deck_creature_types_percentages_json()
tribal_result_json = check_high_tribal_percentage_json()
tribal = tribal_result_json['tribal']
### write mana costs (cmc) to deck_mana_costs.json
get_deck_mana_costs_json("resources/new_deck.txt", "resources/deck_mana_costs.json")
### Get mana %s and write the result to deck_mana_percentages.json
get_deck_mana_color_percentages_json()

### write and return landbase to text file land_suggestions.txt
landbase = get_landbase('resources/new_deck.txt')
print(landbase)
