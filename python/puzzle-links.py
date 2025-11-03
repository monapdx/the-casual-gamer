from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Set up Chrome options (optional: run headless)
options = Options()
options.add_argument("--headless")  # Comment this line to see the browser in action
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Path to your WebDriver
service = Service('chromedriver')  # Replace with your driver path if needed

# Launch browser
driver = webdriver.Chrome(service=service, options=options)

try:
    # Open the webpage
    driver.get("https://www.futilitycloset.com/")

    # Wait until links are loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
    )

    # Find all links with "click for answer"
    links = driver.find_elements(By.XPATH, '//a[contains(text(), "Click for Answer")]')

    # Print the results
    for link in links:
        print(f'{link.text}: {link.get_attribute("href")}')

finally:
    driver.quit()
