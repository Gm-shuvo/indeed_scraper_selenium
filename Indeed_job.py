from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import os
import pandas as pd
import time
import json
from dotenv import load_dotenv
load_dotenv()

# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import NoSuchElementException


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
SCRAPEOPS_API_KEY = os.environ.get("SCRAPEOPS_API_KEY")
print(SCRAPEOPS_API_KEY)
selenium_wire_options = {
    'proxy': {
        'http': f'http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353',
        'https': f'http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353',
        'no_proxy': 'localhost:127.0.0.1'
    }
}

options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options, seleniumwire_options=selenium_wire_options)

driver.set_window_size(1024, 1024)

driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)

links = []

for i in range(1):
    url = f"https://www.indeed.com/jobs?q=bangladesh&start={str(i) + '0'}"
    print(url)
    driver.get(url)
    time.sleep(2)
    try:
        jobs_list = driver.find_elements(
            By.XPATH, "(//div[@class='job_seen_beacon']//h2)[@class='jobTitle css-1h4a4n5 eu4oa1w0']//a")
        print(len(jobs_list))
        for element in jobs_list:
            links.append(element.get_attribute("href"))
            print(element.get_attribute("href"))
    except:
        pass
    
job_titles = []
job_types = []
job_locations = []
company_names = []
job_dates = []
job_description = []
apply_links = []

i = 0
for link in links:
    print(i)
    i += 1
    driver.get(link)
    time.sleep(5)
    try:
        job_title = driver.find_element(
            By.XPATH, "//div[@class='jobsearch-JobInfoHeader-title-container ']//h1")
        job_titles.append(job_title.text)
        print(job_title.text)
    except:
        job_titles.append("Not Found")
    try:
        job_type = driver.find_element(
            By.XPATH, "((//div[@class='css-6z8o9s eu4oa1w0'])[2])")
        job_types.append(job_type.text)
        print(job_type.text)
    except:
        job_types.append("Not Found")
    try:
        job_location = driver.find_element(
            By.XPATH, "(//div[@class='css-6z8o9s eu4oa1w0'])[1]")
        job_locations.append(job_location.text)
        print(job_location.text)
    except:
        job_locations.append("Not Found")
    try:
        company_name = driver.find_element(
            By.XPATH, "div[data-company-name='true']")
        company_names.append(company_name.text)
        print(company_name.text)
    except:
        company_names.append("Not Found")
    try:
        job_date = driver.find_element(
            By.XPATH, "(//span[@class='css-kyg8or eu4oa1w0'])")
        job_dates.append(job_date.text)
        print(job_date.text)
    except:
        job_dates.append("Not Found")
    try:
        job_description = driver.find_element(
            By.XPATH, "(//div[@id='jobDescriptionText'])")
        job_description.append(job_description.text)
        print(job_description.text)
    except:
        job_description.append("Not Found")
    try:
        
        apply_links.append(link)
    except:
        apply_links.append("Not Found")
        
# print(len(job_titles), len(job_types), len(job_locations), len(job_dates), len(job_description), len(apply_links))
driver.save_screenshot("datacamp.png")
print("Screenshot saved successfully.")


time.sleep(1000)

driver.close()
