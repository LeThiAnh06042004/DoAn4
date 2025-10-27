from core.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class CommentPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver, "BinhLuan_locators.yaml")

    def click_SP(self):
        self.click("txtSP")

    def nhapND(self, nd):
        self.send_keys("txtNoiDungBL", nd)

    def nhapHoTen(self, ten):
        self.send_keys("txtHoTen", ten)

    def nhapSDT(self, sdt):
        self.send_keys("txtSDT", sdt)

    def click_BinhLuan(self):
        self.click("btnBinhLuan")

    def get_TBThanhCong(self):
        try:
            return self.get_text("TBThanhCong")
        except:
            return ""

    def get_TBNhapBL(self):
        try:
            return self.get_text("TBNhapBL")
        except:
            return ""

    def get_TBNhapTen(self):
        try:
            return self.get_text("TBNhapTen")
        except:
            return ""

    def get_TBNhapSDT(self):
        try:
            return self.get_text("TBNhapSDT")
        except:
            return ""

    def get_TBChiCoSo(self):
        try:
            return self.get_text("TBChiCoSo")
        except:
            return ""

    def get_TB10So(self):
        try:
            return self.get_text("TB10so")
        except:
            return ""
