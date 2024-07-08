import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from collections import Counter
import time

# run chrome driver headlessly, and wait time declared
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)
# maximum wait time of 10 seconds
wait = WebDriverWait(driver, 5)


def card_combos():
    with open('resources/new_deck.txt') as f:
        card_list = [line.strip() for line in f if line.strip()]

    combos_dict = {}

    def replace_characters(string):
        # Remove leading quantity and any whitespace before the card name
        string = ' '.join(string.strip().split()[1:])
        string = string.replace("'", "")
        # Replace all non-alphanumeric characters with a space
        string = ''.join(c if c.isalnum() else ' ' for c in string)
        # Replace multiple spaces with a single space
        string = ' '.join(string.split())
        # Replace spaces with hyphens
        string = string.replace(' ', '-')
        # Make string lowercase
        string = string.lower()
        # Return the modified string
        return string

    # Iterate through the card_list and search for combos for each card
    for card in card_list:
        # Replace characters in card name
        card = replace_characters(card)

        # Navigate to EDHREC combos page for the card
        url = f'https://edhrec.com/combos/{card}'
        driver.get(url)

        # Check if an error message is displayed on the page
        try:
            error_message = wait.until(EC.visibility_of_element_located(
                (By.XPATH,'//h1[@class="page-heading" and text()="Error"]')))
            continue
        except NoSuchElementException:
            pass
        except TimeoutException:
            pass

        # Find all combo headings on the page
        # Wait for the combos to appear on the page
        try:
            combos = wait.until(EC.visibility_of_all_elements_located(
                (By.XPATH, '//div[@class="CardView_cardlist__gPRb+"]/a/h3')))

            if combos:
                combos_dict[card] = [combo.text for combo in combos]
            else:
                combos_dict[card] = []
        except TimeoutException:
            combos_dict[card] = []

    # Save the combos dictionary to a JSON file
    with open('resources/EDHScraper/card_combos.json', 'w') as f:
        json.dump(combos_dict, f, indent=4)

# sort the output by number of +'s in each item, less should be at that top and more should be at the bottom


def extract_combos():
    with open('resources/EDHScraper/card_combos.json') as f:
        data = json.load(f)
    all_combos = []
    for combo_list in data.values():
        all_combos.extend(combo_list)

    with open('resources/EDHScraper/card_combos_multiple.json', 'w') as f:
        json.dump(all_combos, f)

    with open('resources/EDHScraper/card_combos_multiple.json') as f:
        data = json.load(f)

    duplicates = [combo for combo, count in Counter(data).items() if count > 1]

    with open('resources/EDHScraper/card_combos_multiple.json', 'w') as f:
        json.dump(duplicates, f)



card_combos()
driver.quit()
extract_combos()
