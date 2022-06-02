# Some code has been borrowed from https://github.com/jsoma/selenium-github-actions
# Under the MIT License.

import json

import requests

from os import environ
from time import sleep
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

URL = "rodan2.simssa.ca"

class RodanConnection:
    def __init__(self, url, username, password, protocol="https"):
        self.url = f"{protocol}://{url}"
        self.username = username
        self.password = password
        self.driver = self.setup_driver()

    def setup_driver(self):
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
        return driver

    def delete_all_projects(self):
        projects_url = urljoin(f"{self.url}", "api/projects/?format=json")
        projects_json = requests.get(projects_url, auth=(self.username, self.password))
        if not projects_json.ok:
            raise Exception(
                f"Couldn't load {projects_url}: received HTTP {projects_json.status_code}."
            )
        projects = json.loads(projects_json.text)
        for project in projects["results"]:
            requests.delete(project["url"], auth=(self.username, self.password))

    def login_to_rodan(self):
        self.driver.get(self.url)
        username_field = self.driver.find_element(By.ID, "text-login_username")
        password_field = self.driver.find_element(By.ID, "text-login_password")
        login_button = self.driver.find_element(By.ID, "button-login")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        login_button.click()

        while not self.driver.get_cookies():
            sleep(1)

    def create_new_project(self):
        self.driver.get(self.url)
        new_project_button = self.driver.find_element(By.ID, "button-new_project")
        while not new_project_button.is_enabled():
            sleep(1)
        new_project_button.click()

        projects_table = self.driver.find_element(By.XPATH, '//*[@id="table-projects"]')

        print(projects_table.get_attribute("innerHTML"))

def test():
    username = environ["RODAN_USERNAME"]
    password = environ["RODAN_PASSWORD"]

    rodan = RodanConnection(URL, username, password)
    return rodan


def main():
    username = environ["RODAN_USERNAME"]
    password = environ["RODAN_PASSWORD"]

    rodan = RodanConnection(URL, username, password)
    rodan.login_to_rodan()
    rodan.create_new_project()

if __name__ == '__main__':
    main()
