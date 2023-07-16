from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import os
import pandas as pd
import time
import json
import pymongo
from dotenv import load_dotenv

load_dotenv()

options = Options()
# options.add_argument('--headless')
options.add_argument('--no-sandbox')
# SCRAPEOPS_API_KEY = os.environ.get("SCRAPEOPS_API_KEY")
# print(SCRAPEOPS_API_KEY)
# selenium_wire_options = {
#     'proxy': {
#         'http': f'http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353',
#         'https': f'http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353',
#         'no_proxy': 'localhost:127.0.0.1'
#     }
# }

options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

driver.set_window_size(1024, 1024)

driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)

links = []

for i in range(1):
    url = f"https://www.careerjet.com.bd/jobs-in-bangladesh-122411.html?p={str(i)}"
    print(url)
    driver.get(url)
    time.sleep(2)
    try:
        jobs_list = driver.find_elements(
            By.XPATH, "//ul[@class='jobs']//li//article[@class='job clicky']//a")
        print(len(jobs_list))
        for element in jobs_list:
            links.append(element.get_attribute("href"))
            print(element.get_attribute("href"))
    except:
        pass
    
print(len(links))
    
job_titles = []
job_types = []
job_levels = []
job_locations = []
company_names = []
job_dates = []
job_description = []
apply_links = []

i = 0
for link in links[:5]:
    try:
        print(i)
        i += 1
        driver.get(link)
        time.sleep(4)
    except:
        pass
    
    try:
        job_title = driver.find_element(
            By.XPATH, "//div[@class='container']//h1")
        job_titles.append(job_title.text)
        print(job_title.text)
    except:
        job_titles.append("")
    try:
        job_location = driver.find_element(
            By.XPATH, "//div[@class='container']//ul[@class='details']//li/span")
        job_locations.append(job_location.text)
        print("job_location ==> ", job_location.text)
    except:
        job_locations.append("")
        
    try:
        job_type = element = driver.find_element(By.CSS_SELECTOR, "main[id='main'] header li:last-child")
        job_types.append(job_type.text)
        print("job_type ==> ", job_type.text)
    except:
        job_types.append("")
        
    try:
        company_name = driver.find_element(
            By.XPATH, "//div[@class='container']//p[@class='company']")
        company_names.append(company_name.text)
        print("company_name ==> ", company_name.text)
    except:
        company_names.append("")
    try:
        job_date = driver.find_element(
            By.XPATH, "//div[@class='container']//ul[@class='tags']//span[@class='badge badge-r badge-s']")
        job_dates.append(job_date.text)
        print("job_date ==> ", job_date.text)
    except:
        job_dates.append("")
    try:
        job_des = driver.find_element(
            By.XPATH, "//section[@class='content']")
        job_description.append(job_des.text)
        print("job_des ==> ", job_des.text)
    except:
        job_description.append("")
    try:
        apply_links.append(link)
        job_levels.append("")
        print("apply_links ==> ", link)
        print("job_levels ==> ", "")
    except:
        apply_links.append("")
        
driver.close()
driver.quit()

print(len(job_titles), len(job_types), len(job_locations), len(job_dates), len(job_description), len(apply_links))

print(job_titles, job_types, job_levels, company_names, job_locations,
        job_dates, apply_links, job_description)

data = zip(job_titles, job_types, job_levels, company_names, job_locations,
        job_dates, apply_links, job_description)

# Convert the zipped data to a list of dictionaries
result = []
for item in data:
    job_data = {
        'job_title': item[0],
        'job_type': item[1],
        'job_level': item[2], # 'job_level': item[2] if item[2] else 'None
        'company_name': item[3],
        'job_location': item[4],
        'job_date': item[5],
        'apply_link': item[6],
        'job_description': item[7]
        
    }
    result.append(job_data)

json_data = json.dumps(result)

print(len(result))


# # load into mongodb
load_dotenv()
MONGO_URL = os.getenv('MONGO_URL')
print(MONGO_URL)

dbname = 'jobScraper'
collectionname = 'linkedinjobs'
MONGO_URL = os.environ['MONGO_URL']
try:
    client = pymongo.MongoClient(MONGO_URL)
except pymongo.errors.ConnectionFailure as e:
    print("Could not connect to MongoDB Atlas:", e)

db = client[dbname]
collection = db[collectionname]

    # Create indexes for multiple fields if they don't exist
collection.create_index([('job_title', pymongo.ASCENDING)], unique=True)
collection.create_index([('job_location', pymongo.ASCENDING)])
collection.create_index([('company_name', pymongo.ASCENDING)])

for job_data in result:
        try:
            collection.update_one(
                {'job_title': job_data['job_title'], 'job_location': job_data['job_location'], 'company_name': job_data['company_name'], 'job_description': job_data['job_description'],
                    'apply_link': job_data['apply_link'], 'job_type': job_data['job_type'], 'job_level': job_data['job_level']},
                {'$set': {'job_date': job_data['job_date']}},
                upsert=True
            )
            print("Data inserted/updated successfully.")
        except pymongo.errors.DuplicateKeyError:
            print("Data already exists in the collection. Skipping insertion.")
        except Exception as e:
            print("Error inserting/updating data:", e)
