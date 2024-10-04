from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Set up headless Chrome browser
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# Load the Instagram page
driver.get("https://www.instagram.com/uofcomedy/?hl=en")
time.sleep(3)  # Allow the page to load

# Scroll down to load more posts
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# Extract image URLs
images = driver.find_elements_by_tag_name("img")
img_urls = [img.get_attribute("src") for img in images if img.get_attribute("src")]

# Get random image URL
import random
random_image_url = random.choice(img_urls)

driver.quit()
print(random_image_url)
