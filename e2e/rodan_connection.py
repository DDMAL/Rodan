# Some code has been borrowed from https://github.com/jsoma/selenium-github-actions
# Under the MIT License.

# Standard libraries
import atexit
import json
import os
from tempfile import TemporaryDirectory
from time import sleep
from typing import List
from urllib.parse import urljoin

# Third-party libraries
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager


class RodanConnection:
    def __init__(self, url, username, password, protocol="https"):
        self.url = f"{protocol}://{url}"
        self.username = username
        self.password = password
        self.downloads_dir = TemporaryDirectory()
        self.driver = self.setup_driver()
        atexit.register(self.cleanup)

    def cleanup(self):
        self.downloads_dir.cleanup()

    def setup_driver(self):
        prefs = {
            "profile.default_content_settings.popups": 0,
            "download.default_directory": self.downloads_dir.name,
        }
        options = [
            "--headless",
            "--disable-gpu",
            "--window-size=1920,1200",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        chrome_options = Options()
        for option in options:
            chrome_options.add_argument(option)
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        driver.implicitly_wait(3)
        return driver

    def double_click(self, element: WebElement):
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.double_click()
        actions.perform()

    def navigate_home(self):
        self.driver.get(self.url)

    def login_to_rodan(self):
        username_field = self.driver.find_element(By.ID, "text-login_username")
        password_field = self.driver.find_element(By.ID, "text-login_password")
        login_button = self.driver.find_element(By.ID, "button-login")

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        login_button.click()

        while not self.driver.get_cookies():
            sleep(1)

    def delete_all_resources(self, resource_type: str):
        resource_url = urljoin(f"{self.url}", f"api/{resource_type}/?format=json")
        resource_json = requests.get(resource_url, auth=(self.username, self.password))
        if not resource_json.ok:
            raise Exception(
                f"Couldn't load {resource_url}: received HTTP {resource_json.status_code}."
            )
        resources = json.loads(resource_json.text)
        for resource in resources["results"]:
            requests.delete(resource["url"], auth=(self.username, self.password))

    def create_new_project(self):
        new_project_button = self.driver.find_element(By.ID, "button-new_project")
        # This seems like an adequate time to wait for the page to load.
        sleep(3)
        new_project_button.click()

    def get_most_recent_from_table(self, item: str) -> WebElement:
        items = self.driver.find_elements(By.XPATH, f'//*[@id="table-{item}"]/tbody/tr')
        # td[3] corresponds to the "Created" field in the table.
        return sorted(
            items, reverse=True, key=lambda p: str(p.find_element(By.XPATH, "td[3]"))
        )[0]

    def create_workflow(self, project: WebElement) -> WebElement:
        self.double_click(project)
        self.driver.find_element(By.ID, "workflow_count").click()
        self.driver.find_element(By.ID, "button-new_workflow").click()
        workflows = None
        while not workflows:
            workflows = self.driver.find_elements(
                By.XPATH, '//*[@id="table-workflows"]/tbody/tr'
            )
            sleep(3)
        return workflows[0]

    def build_hello_world_workflow(self, workflow) -> str:
        self.double_click(workflow)
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
        name_filter = self.driver.find_element(By.ID, "name__icontains")
        name_filter.send_keys("hello")
        hello_job_row = self.driver.find_element(
            By.XPATH, '//*[@id="table-jobs"]//td[text()="Hello World - Python3"]'
        )
        self.double_click(hello_job_row)
        close_button = self.driver.find_element(
            By.XPATH, '//*[@id="modal-generic"]//button[@class="close"]'
        )
        close_button.click()
        # Without this sleep, the test breaks.
        sleep(3)
        workflow_dropdown.click()
        run_job_button = workflow_dropdown.find_element(
            By.XPATH, '//*[@id="button-run"]'
        )
        run_job_button.click()
        while True:
            try:
                workflow_run = self.get_most_recent_from_table("workflowruns")
            except IndexError:
                sleep(1)
        while workflow_run.find_element(By.XPATH, "td[5]").text != "Finished":
            sleep(1)
        resources_button = self.driver.find_element(By.ID, "button-resources_show")
        resources_button.click()
        resource_row = self.get_most_recent_from_table("resources")
        self.double_click(resource_row)
        with open(
            os.path.join(
                self.downloads_dir.name,
                "Hello World - Python3 - Text output.txt",
            ),
            "r",
        ) as f:
            hello_world_output = f.read()
            return hello_world_output
