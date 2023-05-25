import os
import pandas as pd
import time
import json
import pymongo
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

driver.set_window_size(1024, 768)

driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)


driver.get('https://www.linkedin.com/jobs/search?keywords=&location=Dhaka%2C%20Dhaka%2C%20Bangladesh&geoId=103561184&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0')

# You can set your own pause time. My laptop is a bit slow so I use 1 sec
scroll_pause_time = 2
screen_height = driver.execute_script(
    "return window.screen.height;")   # get the screen height of the web
i = 1
time.sleep(2)
while i <= 2:
    # scroll one screen height each time
    driver.execute_script(
        "window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled
    # the page


    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    # Break the loop when the height we need to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
      see_more = driver.find_element(
        By.XPATH, "//button[@data-tracking-control-name='infinite-scroller_show-more']")
      if (see_more.text == 'See more jobs'):
        see_more.click()
        time.sleep(2)
        continue
      break


links = []

time.sleep(2)

try:
    jobs_list = driver.find_elements(
        By.XPATH, "(//div[@class='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card'])")
    for element in jobs_list:
        entity_urn = element.get_attribute("data-entity-urn")
        job_id = entity_urn.split(":")[-1]
        # print(job_id)
        url_template = "https://www.linkedin.com/jobs/search?location=Dhaka%2C%20Dhaka%2C%20Bangladesh&geoId=103561184&trk=public_jobs_jobs-search-bar_search-submit&position=23&pageNum=0&currentJobId={}"
        url = url_template.format(job_id)
        links.append(url)
        # print(links)
        
except:
    pass


# try:
#     jobs_list = driver.find_elements(
#         By.XPATH, "(//div[@class='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card'])")
#     for link in jobs_list:
#         all_links = link.find_elements(By.TAG_NAME, 'a')
#         for a in all_links:
#             # print(a.get_attribute('href'))
#             if str(a.get_attribute('href')).startswith("https://bd.linkedin.com/jobs/view/") and a.get_attribute('href') not in links:
#                 links.append(a.get_attribute('href'))

# except:
#     pass

# print(links)

job_titles = []
job_types = []
job_locations = []
company_names = []
job_dates = []
job_description = []
apply_links = []
i = 0
for i in range(5):
    try:
        driver.get(links[i])

        time.sleep(2)
        # Click See more.
        driver.find_element(
            By.XPATH, "//button[@data-tracking-control-name='public_jobs_show-more-html-btn']").click()
        time.sleep(2)
    except:
        pass
    try:
        job_titles.append(driver.find_element(
            By.XPATH, "//h2[@class='top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title']").text)
        company_names.append(driver.find_element(
            By.XPATH, "//a[@class='topcard__org-name-link topcard__flavor--black-link']").text)
        job_locations.append(driver.find_element(
            By.XPATH, "//span[@class='topcard__flavor topcard__flavor--bullet']").text)
        try:
            job_dates.append(driver.find_element(
                By.XPATH, "//span[@class='posted-time-ago__text topcard__flavor--metadata']").text)
        except NoSuchElementException:
            job_dates.append(driver.find_element( 
                By.XPATH, "//span[@class='posted-time-ago__text posted-time-ago__text--new topcard__flavor--metadata']").text)
        except:
            job_dates.append('None')
        apply_links.append(str(links[i]))
        
        job_description.append(driver.find_element( 
            By.XPATH, "(//div[@class='show-more-less-html__markup relative overflow-hidden'])").text)
        types = []
        type_job = driver.find_elements(
            By.XPATH, "//span[@class='description__job-criteria-text description__job-criteria-text--criteria']")
        for type in type_job:
            types.append(type.text)
        job_types.append(types[0] + ' ' + types[1])
    except:
        pass
    time.sleep(2)

print(job_titles, job_types, company_names, job_locations,
    job_dates, apply_links, job_description)

data = zip(job_titles, job_types, company_names, job_locations, job_dates, apply_links, job_description)

# Convert the zipped data to a list of dictionaries
result = []
for item in data:
    job_data = {
        'job_title': item[0],
        'job_type': item[1],
        'company_name': item[2],
        'job_location': item[3],
        'job_date': item[4],
        'apply_link': item[5],
        'job_description': item[6]
    }
    result.append(job_data)

# Convert the list of dictionaries to JSON
# json_data = json.dumps(result)

# # Print the JSON data
# print(json_data)
# with open("data2.json", "w") as f:
#     f.write(json_data)





# # Convert the list of dictionaries to a pandas DataFrame
# df = pd.DataFrame(job_data,
#                   columns=['job_title', 'job_types', 'company_name', 'job_location', 'job_date', 'apply_link', 'job_description'])

# # convert json
# json_data = df.to_json('data.json',orient='records', )
# json to dict
# data = json.loads(json_data)

# # load into mongodb
load_dotenv()
MONGO_URL = os.getenv('MONGO_URL')
# print(MONGO_URL)

dbname = 'jobScraper'
collectionname = 'linkedInJobs'

# Set up a connection to MongoDB Atlas
try:
    client = pymongo.MongoClient(MONGO_URL)
    print("Connected successfully to MongoDB Atlas")
except pymongo.errors.ConnectionFailure as e:
    print("Could not connect to MongoDB Atlas: %s" % e)

db = client[dbname]
collection = db[collectionname]

# # insert data into mongodb
for record in result:
    # Create a unique index for the job_title field
    collection.create_index([('job_title', pymongo.ASCENDING)], unique=True)
    # update = {'$set': record}

    # Try to update the document if it exists, otherwise insert it as a new document
    try:
        collection.insert_one(record)
        print("Data inserted successfully.")
    except pymongo.errors.DuplicateKeyError:
        print("Data already exists in the collection. Skipping insertion.")
    except Exception as e:
        print("Error inserting data:", e)

# # Print the JSON string
# print(json_data)


# # mail = 'devilshuvo12@gmail.com'
# # password = 'devil91?'

# # driver.find_element(By.XPATH, "(//input[@type='text'])").send_keys(mail)

# # driver.find_element(
# #     By.XPATH, "(//input[@type='password'])").send_keys(password)
# # time.sleep(2)

# # driver.find_element(By.XPATH,"//button[normalize-space()='Sign in']").click()

# # driver.find_element(By.TAG_NAME,'body').send_keys(Keys.COMMAND + 't')
# # driver.get('http://stackoverflow.com/')


time.sleep(1000)
driver.close()
