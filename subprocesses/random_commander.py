import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
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

# Main Execution
driver = get_chrome_driver()

# maximum wait time of 10 seconds
wait = WebDriverWait(driver, 8)

# Navigate to edhrec.com
driver.get("https://edhrec.com/random")

commander_found = False

try:
    # Wait for the page to load and locate the <h3> element containing the commander name
    heading = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'm-2')))
    heading_text = heading.text
    
    # Remove the "(Commander)" suffix from the heading text
    heading_text = heading_text.replace(' (Commander)', '').strip()
    print(f"Commander found: {heading_text}")  # Debugging information
    
    # Save the commander to the commander_id.json file
    commander_id_file = 'resources/EDHScraper/commander_id.json'
    with open(commander_id_file, 'w') as f:
        json.dump({'commander': heading_text}, f)
    
    commander_found = True

except TimeoutException:
    # If the <h3> element is not found within the specified time, print an error message
    print("Error: Timed out waiting for page to load")

# Close the webdriver instance
driver.quit()

# Check if commander was found and saved
if commander_found:
    try:
        with open('resources/EDHScraper/commander_id.json', 'r') as f:
            commander = json.load(f)['commander']
            print(f"Commander loaded from file: {commander}")
    except (FileNotFoundError, KeyError) as e:
        print(f"Error loading commander from file: {e}")
else:
    print("No commander was found or saved.")
