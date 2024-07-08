# MTG Emratool

## Overview

MTG Emratool is an all-in-one EDH (Elder Dragon Highlander) deck-building tool designed for Magic: The Gathering enthusiasts. This tool aims to simplify and enhance the deck-building experience by providing a user-friendly retro interface (built entirely with TKinter because I felt like it lol) and robust functionalities. This was designed to be used in conjuction with Forge, as the card lookup and analysis is built to work directly with Forge's formatting when copy and pasting your decklist.

## Features

- **Land Calculator (and Deck Analysis)**:
Import your decklist to this tool get a returned list of lands in order of descending importance, value of each card is not considered, this tool prioritizes fast lands, fetch lands, and other specifics depending on your decks current mana curve and color identity. This tool will also show you some interesting deck statistics like your mana pip counts, spell counts, creature subtypes, and percentages.
  
- **EDHREC Fetcher**:
Quickly find and add cards to your deck through EDHREC, allows for custom filtering, easy multiline copy and pastes, and also fetches some nice artwork from skryfall
  
- **Random Commander**:
A fun way to pull a random legal commander, either for a deckbuilding challenge, or for fun inspiration.
  
- **Deck Compare**:
Intuitive diff checker for deck versioning, load an old and new list and allow Emratool to point out the cards you have removed and cards you have added between iterations.
  
- **Combo Finder**:
Find infinite combos in your decklist, or combos that you could potentially make with your current decklist, useful for either making a deck more competitive, or removing card combinations that may be too strong for your group.

- **Change Log**:
This project is something I come back to on and off, with additions in card types, changes in EDHREC, Skryfall, Commanderspellbook, etc. I figured I would add a changelog right into the tool as things are updated or bugs are fixed.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/mint-morrogh/MTG_Emratool.git
    ```
2. Navigate to the project directory:
    ```sh
    cd MTG_Emratool
    ```

## Usage

1. Run the main UI script:
    ```sh
    python UI_main.py
    ```
2. Follow the on-screen instructions to start building your deck.


