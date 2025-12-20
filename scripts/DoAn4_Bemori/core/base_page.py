import os
import yaml
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, locators_file=None):
        self.driver = driver
        self.locators = {}
        self.logger = logging.getLogger("TestLogger")  #LOGGER CHUNG

        if locators_file:
            self.logger.info(f"Load locator file: {locators_file}")
            self.load_locators(locators_file)

    def load_locators(self, file_name):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "locators", file_name)

        if not os.path.exists(path):
            self.logger.error(f"Không tìm thấy file locator: {path}")
            raise FileNotFoundError(f"Không tìm thấy file locator: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.locators = yaml.safe_load(f)

        self.logger.info(f"Đã load {len(self.locators)} locator từ {file_name}")

    def get_locator(self, name):
        if name not in self.locators:
            self.logger.error(f"Locator '{name}' không tồn tại")
            raise KeyError(f"Locator '{name}' không tồn tại trong file YAML.")

        locator_info = self.locators[name]
        by = locator_info["by"].lower()
        value = locator_info["value"]

        self.logger.debug(f"Lấy locator [{name}] -> ({by}, {value})")

        if by == "id":
            return (By.ID, value)
        elif by == "xpath":
            return (By.XPATH, value)
        elif by in ["css", "css_selector"]:
            return (By.CSS_SELECTOR, value)
        elif by == "name":
            return (By.NAME, value)
        elif by == "class":
            return (By.CLASS_NAME, value)
        elif by == "link_text":
            return (By.LINK_TEXT, value)
        else:
            raise ValueError(f"Loại locator '{by}' không được hỗ trợ.")

    def find_element(self, name, timeout=10):
        self.logger.info(f"Tìm element: {name}")
        locator = self.get_locator(name)
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def click(self, name, timeout=10):
        self.logger.info(f"Click element: {name}")
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.get_locator(name))
        )
        element.click()

    def send_keys(self, name, text, timeout=10):
        self.logger.info(f"Nhập '{text}' vào: {name}")
        element = self.find_element(name, timeout)
        element.clear()
        element.send_keys(text)

    def get_text(self, name, timeout=10):
        self.logger.info(f"Lấy text từ: {name}")
        element = self.find_element(name, timeout)
        return element.text

    def get_alert_text(self, timeout=10):
        self.logger.info("Chờ alert hiển thị...")
        alert = WebDriverWait(self.driver, timeout).until(
            EC.alert_is_present()
        )
        text = alert.text
        self.logger.info(f"Alert text: {text}")
        alert.accept()
        return text
