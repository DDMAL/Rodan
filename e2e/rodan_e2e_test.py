# Some code has been borrowed from https://github.com/jsoma/selenium-github-actions
# Under the MIT License.

# Standard libraries
import json
from os import environ
from time import sleep
from urllib.parse import urljoin

# Third-party libraries
import requests
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
        driver.implicitly_wait(3)
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
        projects = None
        while not projects:
            new_project_button.click()
            sleep(1)
            projects = self.driver.find_elements(
                By.XPATH, '//*[@id="table-projects"]/tbody/tr'
            )
        return projects[0]


    def enter_project(self, project):
        project.doubleclick()


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
    rodan.delete_all_projects()
    project = rodan.create_new_project()
    rodan.enter_project(project)


if __name__ == "__main__":
    main()
