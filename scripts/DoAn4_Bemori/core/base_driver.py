import os
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class BaseDriver:
    def __init__(self, browser=None):
        # Đọc config từ file, lấy đg dẫn tuyệt đối tới file
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(ROOT_DIR, "config", "config.yaml")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # Nếu không truyền browser thì lấy mặc định trong config.yaml
        self.browser = browser or self.config.get("browser", "chrome")
        self.driver = None

    def get_driver(self):
        """Khởi tạo WebDriver theo browser"""
        if self.browser.lower() == "chrome":
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        elif self.browser.lower() == "firefox":
            self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        elif self.browser.lower() == "edge":
            self.driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
        else:
            raise ValueError(f"Browser '{self.browser}' không được hỗ trợ!")

        # Maximize window + timeout
        self.driver.maximize_window()
        self.driver.implicitly_wait(self.config.get("implicit_wait", 10))
        return self.driver

    def quit_driver(self):
        """Đóng WebDriver"""
        if self.driver:
            self.driver.quit()
