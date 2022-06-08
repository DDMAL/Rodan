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
from selenium.webdriver.common.action_chains import ActionChains
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

    def delete_all_resources(self, resource_type):
        resource_url = urljoin(f"{self.url}", f"api/{resource_type}/?format=json")
        resource_json = requests.get(resource_url, auth=(self.username, self.password))
        if not resource_json.ok:
            raise Exception(
                f"Couldn't load {resource_url}: received HTTP {resource_json.status_code}."
            )
        resources = json.loads(resource_json.text)
        for resource in resources["results"]:
            requests.delete(resource["url"], auth=(self.username, self.password))

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

    def navigate_home(self):
        self.driver.get(self.url)

    def create_new_project(self):
        self.navigate_home()
        new_project_button = self.driver.find_element(By.ID, "button-new_project")
        projects = None
        while not projects:
            new_project_button.click()
            sleep(3)
            projects = self.driver.find_elements(
                By.XPATH, '//*[@id="table-projects"]/tbody/tr'
            )
        return projects[0]

    def double_click(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.double_click()
        actions.perform()

    def create_workflow(self, project_element):
        self.double_click(project_element)
        self.driver.find_element(By.ID, "workflow_count").click()
        self.driver.find_element(By.ID, "button-new_workflow").click()
        workflows = None
        while not workflows:
            workflows = self.driver.find_elements(
                By.XPATH, '//*[@id="table-workflows"]/tbody/tr'
            )
            sleep(3)
        return workflows[0]

    def build_workflow(self):
        workflow_dropdown = self.driver.find_element(
            By.XPATH, '//*[@id="region-main"]//*[contains(text(), "Workflow")]'
        )
        workflow_dropdown.click()
        add_job_button = workflow_dropdown.find_element(
            By.XPATH, '//*[@id="button-add_job"]'
        )
        add_job_button.click()
        filter_button = self.driver.find_element(By.ID, "filter-menu")
        filter_button.click()
        name_button = filter_button.find_element(
            By.CSS_SELECTOR, 'a[data-id="filter_name"]'
        )
        name_button.click()
        name_filter.send_keys("one-bit")
        onebit_job_row = self.driver.find_element(
            By.XPATH, '//*[@id="table-jobs"]//tr[contains(@title, "**to_onebit**")]'
        )
        add_button = onebit_job_row.find_element(By.ID, 'button-main_job_button_add')
        add_button.click()



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
