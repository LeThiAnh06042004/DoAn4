from core.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class QuickOrderPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver, "DatHangNhanh_locators.yaml")

    def click_SP(self):
        self.click("lnkSanPham")

    def nhapDHN(self, sdt):
        self.send_keys("txtDatHangNhanh", sdt)

    def click_Gui(self):
        self.click("btnGui")

    def get_TBThanhCong(self):
        try:
            return self.get_text("lblThanhCong")
        except:
            return ""

    def get_TBrong(self):
        try:
            return self.get_text("lblThongBaoNhapSoDienThoai")
        except:
            return ""

    def get_TBChiCoSo(self):
        try:
            return self.get_text("lblThongBaoSoDienThoaiChiCoSo")
        except:
            return ""

    def get_TBduoi10(self):
        try:
            return self.get_text("lblThongBaoSoDienThoai10so")
        except:
            return ""