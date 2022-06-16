# Some code has been borrowed from https://github.com/jsoma/selenium-github-actions
# Under the MIT License.

# Standard libraries
import atexit
import json
import os
import time
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

TIMEOUT_SECONDS = 10


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
        resource_url = urljoin(self.url, f"api/{resource_type}/?format=json")
        resource_json = requests.get(resource_url, auth=(self.username, self.password))
        if not resource_json.ok:
            raise Exception(
                f"Couldn't load {resource_url}: received HTTP {resource_json.status_code}."
            )
        resources = json.loads(resource_json.text)
        for resource in resources["results"]:
            requests.delete(resource["url"], auth=(self.username, self.password))

    def get_rodan_build_hash(self) -> str:
        api_url = urljoin(self.url, "api?format=json")
        api_request = requests.get(api_url, auth=(self.username, self.password))
        if not api_request.ok:
            raise Exception(
                f"Couldn't load {api_url}: received HTTP {api_request.status_code}."
            )
        api_json = json.loads(api_request.text)
        return api_json["build_hash"]

    def find_visible(self, by, arg):
        element = self.wait.until(EC.visibility_of_element_located((by, arg)))
        self.wait.until(EC.element_to_be_clickable(element))
        return element

    def find_visibles(self, by, arg):
        return self.wait.until(EC.visibility_of_all_elements_located((by, arg)))

    def get_most_recent_from_table(
        self, item_type: str, timeout_secs=TIMEOUT_SECONDS
    ) -> WebElement:
        now_time = start_time = time.monotonic()
        items = None
        while not items:
            items = self.find_visibles(
                By.XPATH, f'//*[@id="table-{item_type}"]/tbody/tr'
            )
            now_time = time.monotonic()
            if now_time - start_time > timeout_secs:
                break
        if not items:
            raise Exception(
                f"Couldn't get item from {item_type} table before timeout of {timeout_secs} seconds was reached!"
            )
        # td[3] corresponds to the "Created" field in the table.
        items = sorted(
            items, reverse=True, key=lambda p: str(p.find_element(By.XPATH, "td[3]"))
        )
        most_recent = items[0]
        self.wait.until(EC.element_to_be_clickable(most_recent))
        return most_recent

    def create_new_project(self):
        new_project_button = self.find_visible(By.ID, "button-new_project")
        new_project_button.click()

    def create_workflow(self, project: WebElement) -> WebElement:
        self.double_click(project)
        self.find_visible(By.ID, "workflow_count").click()
        self.find_visible(By.ID, "button-new_workflow").click()
        return self.get_most_recent_from_table("workflows")

    def wait_for_text_present(
        self, element: WebElement, text: str, timeout_secs=TIMEOUT_SECONDS
    ):
        now_time = start_time = time.monotonic()
        while now_time - start_time < timeout_secs:
            if text in element.text:
                return
            sleep(1)
        raise Exception(f"Timed out waiting for {text} to be present in {element}!")

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
        sleep(5)
        workflow_dropdown.click()
        run_job_button = self.find_visible(By.ID, "button-run")
        run_job_button.click()
        workflow_run = self.get_most_recent_from_table("workflowruns")
        # from pudb import set_trace; set_trace()
        self.wait_for_text_present(workflow_run, "Finished")
        self.double_click(workflow_run)
        # For some reason we need this sleep before we click Resources.
        sleep(1)
        resources_button = self.find_visible(By.ID, "button-resources_show")
        resources_button.click()
        resource_row = self.get_most_recent_from_table("resources")
        self.double_click(resource_row)
        # Wait for download to complete.
        sleep(5)
        with open(
            os.path.join(
                self.downloads_dir.name,
                "Hello World - Python3 - Text output.txt",
            ),
            "r",
        ) as f:
            hello_world_output = f.read()
            return hello_world_output
