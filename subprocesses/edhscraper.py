import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def get_chrome_driver():
    """Get a valid ChromeDriver, and handle errors by redownloading if necessary."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    service = None
    driver = None

    # Get the correct path to the ChromeDriver executable
    try:
        service_path = ChromeDriverManager().install()
        chromedriver_path = os.path.join(
            os.path.dirname(service_path),
            "chromedriver.exe"  # Ensure this is pointing to the actual executable
        )

        if not os.path.isfile(chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver executable not found at: {chromedriver_path}")

        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"ChromeDriver successfully started from: {chromedriver_path}")

    except (OSError, WebDriverException, FileNotFoundError) as e:
        print(f"Error initializing ChromeDriver: {e}")
        print("Attempting to redownload ChromeDriver...")

        # Sleep for a brief moment before retrying
        time.sleep(2)

        # Redownload and retry
        service_path = ChromeDriverManager().install()
        chromedriver_path = os.path.join(
            os.path.dirname(service_path),
            "chromedriver.exe"
        )

        if not os.path.isfile(chromedriver_path):
            raise FileNotFoundError(f"ChromeDriver executable not found after redownload at: {chromedriver_path}")

        try:
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"ChromeDriver redownloaded and successfully started from: {chromedriver_path}")
        except Exception as final_exception:
            print(f"Failed to start ChromeDriver after redownload: {final_exception}")
            raise

    return driver

def as_commander(driver):
    # Create a WebDriverWait instance
    wait = WebDriverWait(driver, 10)
    
    # read commander of deck
    with open('resources/EDHScraper/commander_id.json', 'r') as f:
        commander_id = json.load(f)['commander_id']
    
    # read selected theme from file
    selected_theme = ''
    with open('resources/EDHScraper/selected_theme.json', 'r') as f:
        data = json.load(f)
        if data:
            selected_theme = data.get('selected_theme', '')
    
    # append selected theme to URL if it's not blank
    url = f'https://edhrec.com/commanders/{commander_id}'
    if selected_theme:
        url += f'/{selected_theme}'   
    driver.get(url)
    print(url)

    # get high synergy cards
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'highsynergycards')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_highsynergy.json', 'w') as f:
        json.dump({'highsynergy': text}, f)

    # get new cards
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'newcards')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_newcards.json', 'w') as f:
        json.dump({'newcards': text}, f)

    # get top cards
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'topcards')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_topcards.json', 'w') as f:
        json.dump({'topcards': text}, f)

    # get creatures
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'creatures')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_creatures.json', 'w') as f:
        json.dump({'creatures': text}, f)

    # get instants
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'instants')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_instants.json', 'w') as f:
        json.dump({'instants': text}, f)

    # get sorceries
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'sorceries')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_sorceries.json', 'w') as f:
        json.dump({'sorceries': text}, f)

    # get utility artifacts
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'utilityartifacts')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_utilityartifacts.json', 'w') as f:
        json.dump({'utilityartifacts': text}, f)

    # get planeswalkers
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'planeswalkers')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_planeswalkers.json', 'w') as f:
        json.dump({'planeswalkers': text}, f)

    # get enchantments
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'enchantments')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_enchantments.json', 'w') as f:
        json.dump({'enchantments': text}, f)

    # get mana artifacts
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'manaartifacts')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_manaartifacts.json', 'w') as f:
        json.dump({'manaartifacts': text}, f)

    # get utility lands
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'utilitylands')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_utilitylands.json', 'w') as f:
        json.dump({'utilitylands': text}, f)

    # get lands
    try:
        high_synergy_cards = wait.until(EC.presence_of_element_located(
            (By.ID, 'lands')))
        text = high_synergy_cards.text
    except TimeoutException:
        print("Timed out waiting for element.")
        text = ""
    with open('resources/EDHScraper/edhrec_lands.json', 'w') as f:
        json.dump({'lands': text}, f)

    # Get themes
    try:
        themes_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'NavigationPanel_themes__E1O6V')))
        themes = []
        for theme in themes_div.find_elements(By.TAG_NAME, 'a'):
            if 'btn-secondary' in theme.get_attribute('class'):
                href = theme.get_attribute('href')
                theme_name = href.split('/')[-1]
                theme_label = theme.find_element(By.CLASS_NAME, 'NavigationPanel_label__xMLz1').text
                theme_count = theme.find_element(By.CLASS_NAME, 'badge').text
                themes.append({'theme': theme_name, 'label': theme_label, 'count': theme_count})
    except TimeoutException:
        print("Timed out waiting for themes.")
        themes = []

    # Write the themes to the edhrec_themes.json file
    with open('resources/EDHScraper/edhrec_themes.json', 'w') as f:
        json.dump({'themes': themes}, f)

    driver.quit()

# Main execution
driver = get_chrome_driver()
as_commander(driver)
