import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from collections import Counter
import time

# run chrome driver headlessly, and wait time declared
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)
# maximum wait time of 10 seconds
wait = WebDriverWait(driver, 10)
# reads commander from commander line. (how will this work with forge? maybe need the html copy)
# saves the result to commander_id in commander_id.json


driver.get("https://edhrec.com/commanders/najeela-the-blade-blossom")  # Replace with the actual URL of the page

themes_dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select.form-control')))

# Create a list to hold the option values
option_values = []
for option in themes_dropdown.find_elements(By.TAG_NAME, 'option'):
    value = option.get_attribute('value')
    if value:
        option_values.append(value)

# Write the option values to the edhrec_themes.json file
with open('resources/EDHScraper/edhrec_themes.json', 'w') as f:
    json.dump({'themes': option_values}, f)

# Close the web browser
driver.quit()
