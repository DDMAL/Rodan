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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

TIMEOUT_SECONDS = 5


class RodanConnection:
    def __init__(self, url, username, password, protocol="https"):
        self.url = f"{protocol}://{url}"
        self.username = username
        self.password = password
        self.downloads_dir = TemporaryDirectory()
        self.driver = self.setup_driver()
        self.wait = WebDriverWait(self.driver, TIMEOUT_SECONDS)
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
        return driver

    def find_visible(self, by, arg):
        return self.wait.until(EC.visibility_of_element_located((by, arg)))

    def find_visibles(self, by, arg):
        return self.wait.until(EC.visibility_of_all_elements_located((by, arg)))

    def double_click(self, element: WebElement):
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.double_click()
        actions.perform()

    def navigate_home(self):
        self.driver.get(self.url)

    def login_to_rodan(self):
        username_field = self.find_visible(By.ID, "text-login_username")
        password_field = self.find_visible(By.ID, "text-login_password")
        login_button = self.find_visible(By.ID, "button-login")

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
        new_project_button = self.find_visible(By.ID, "button-new_project")
        new_project_button.click()

    def get_most_recent_from_table(self, item: str) -> WebElement:
        items = self.find_visibles(By.XPATH, f'//*[@id="table-{item}"]/tbody/tr')
        # td[3] corresponds to the "Created" field in the table.
        return sorted(
            items, reverse=True, key=lambda p: str(p.find_element(By.XPATH, "td[3]"))
        )[0]

    def create_workflow(self, project: WebElement) -> WebElement:
        self.double_click(project)
        self.find_visible(By.ID, "workflow_count").click()
        self.find_visible(By.ID, "button-new_workflow").click()
        workflows = None
        while not workflows:
            workflows = self.find_visibles(
                By.XPATH, '//*[@id="table-workflows"]/tbody/tr'
            )
            sleep(1)
        return workflows[0]

    def build_hello_world_workflow(self, workflow) -> str:
        self.double_click(workflow)
        workflow_dropdown = self.find_visible(
            By.XPATH, '//*[@id="region-main"]//*[contains(text(), "Workflow")]'
        )
        workflow_dropdown.click()
        add_job_button = self.find_visible(By.ID, "button-add_job")
        add_job_button.click()
        filter_button = self.find_visible(By.ID, "filter-menu")
        filter_button.click()
        name_button = self.find_visible(
            By.XPATH, '//*[@id="filter-menu"]//*[@data-id="filter_name"]'
        )
        name_button.click()
        name_filter = self.find_visible(By.ID, "name__icontains")
        name_filter.send_keys("hello")
        hello_job_row = self.find_visible(
            By.XPATH, '//*[@id="table-jobs"]//td[text()="Hello World - Python3"]'
        )
        self.double_click(hello_job_row)
        close_button = self.find_visible(
            By.XPATH, '//*[@id="modal-generic"]//button[@class="close"]'
        )
        close_button.click()
        # Wait for workflow to be validated before running it.
        sleep(3)
        workflow_dropdown.click()
        run_job_button = self.find_visible(By.ID, "button-run")
        run_job_button.click()
        while True:
            try:
                workflow_run = self.get_most_recent_from_table("workflowruns")
                break
            except IndexError:
                sleep(1)
        while workflow_run.find_element(By.XPATH, "td[5]").text != "Finished":
            sleep(1)
        self.double_click(workflow_run)
        # For some reason we need this sleep before we click Resources.
        sleep(1)
        resources_button = self.find_visible(By.ID, "button-resources_show")
        resources_button.click()
        resource_row = self.get_most_recent_from_table("resources")
        EC.element_to_be_clickable(resource_row)
        self.double_click(resource_row)
        # Wait for download to complete.
        sleep(3)
        with open(
            os.path.join(
                self.downloads_dir.name,
                "Hello World - Python3 - Text output.txt",
            ),
            "r",
        ) as f:
            hello_world_output = f.read()
            return hello_world_output
