# Originally from https://github.com/jsoma/selenium-github-actions
# Under the MIT License.

import json

from os import environ
from time import sleep
from urllib.parse import urljoin

from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

PROTOCOL = "https"
SITE = "rodan2.simssa.ca"

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

driver.implicitly_wait(5)

# driver.get(SITE)

username = environ["RODAN_USERNAME"]
password = environ["RODAN_PASSWORD"]

# username_field = driver.find_element(By.ID, "text-login_username")
# password_field = driver.find_element(By.ID, "text-login_password")
# login_button = driver.find_element(By.ID, "button-login")

# username_field.send_keys(username)
# password_field.send_keys(password)
# login_button.click()

# while not driver.get_cookies():
#     sleep(1)

# new_project_button = driver.find_element(By.ID, "button-new_project")

# new_project_button.click()

# projects_table = driver.find_element(By.XPATH, '//*[@id="table-projects"]')

# print(projects_table.get_attribute("innerHTML"))
full_url = f'{PROTOCOL}://{username}:{password}@{SITE}'
projects_url = urljoin(full_url, "api/projects/?format=json")
projects_json = driver.get(projects_url)
print(driver.page_source)
