import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from collections import Counter
import time

# run chrome driver headlessly, and wait time declared
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

# Use webdriver-manager to handle ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# maximum wait time of 10 seconds
wait = WebDriverWait(driver, 8)

# Navigate to edhrec.com
driver.get("https://edhrec.com/random")


try:
    # Wait for the page to load and the h2 element to appear
    heading = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Header_header__MwWvM')))
    heading = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'Header_header__MwWvM')))
    # Get the text of the h1 element
    heading_text = heading.text
    # Remove the "(Commander)" suffix from the heading text
    heading_text = heading_text.replace(' (Commander)', '').strip()
    print(f"Commander found: {heading_text}")  # Debugging information
    # Save the commander to the commander_id.json file
    commander_id_file = 'resources/EDHScraper/commander_id.json'
    with open(commander_id_file, 'w') as f:
        json.dump({'commander': heading_text}, f)
    
    # Code to fetch image goes here
    # ...
    
except TimeoutException:
    # If the h1 element is not found within the specified time, print an error message
    print("Error: Timed out waiting for page to load")
    
# Close the webdriver instance
driver.quit()

