import os
import yaml
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver, locators_file=None):
        self.driver = driver
        self.locators = {} #chứa toàn bộ locators đc load từ file
        if locators_file: #nếu có file sẽ tự độn load
            self.load_locators(locators_file)

    def load_locators(self, file_name):
        # Lấy thư mục gốc project (thư mục chứa core, pages, tests, locators)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "locators", file_name)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy file locator: {path}")

        with open(path, "r", encoding="utf-8") as f:
            self.locators = yaml.safe_load(f)

    def get_locator(self, name):
        if name not in self.locators: #nếu ko tìm thấy tên khoá
            raise KeyError(f"Locator '{name}' không tồn tại trong file YAML.")
        locator_info = self.locators[name]
        by = locator_info["by"].lower() #dựa trn by, trả về tuple chuẩn selenium
        value = locator_info["value"]

        if by == "id":
            return (By.ID, value)
        elif by == "xpath":
            return (By.XPATH, value)
        elif by == "css":
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
        locator = self.get_locator(name)
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def click(self, name, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.get_locator(name))
        )
        element.click()

    def send_keys(self, name, text, timeout=10):
        element = self.find_element(name, timeout)
        element.clear()
        element.send_keys(text)

    def get_text(self, name, timeout=10):
        element = self.find_element(name, timeout)
        return element.text
