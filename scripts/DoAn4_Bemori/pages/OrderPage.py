from core.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class OrderPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver, "MuaHang_Bemori_locators.yaml")

    def click_SP(self):
        self.click("lnkSanPham")

    def click_MuaHang(self):
        self.click("btnMuaHang")

    def nhapTen(self, ten):
        self.send_keys("txtTenNguoiMua", ten)

    def nhapSDT(self, sdt):
        self.send_keys("txtSoDienThoaiNguoiMua", sdt)

    def nhapDC(self, dc):
        self.send_keys("txtDiaChiNhanHang", dc)

    def nhapYCThem(self, yc):
        self.send_keys("txtYeuCauThem", yc)

    def click_Mua(self):
        self.click("btnMua")

    def get_TBThanhCong(self):
        try:
            locator = self.get_locator("lblThongBaoThanhCong")
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_TBNhapTen(self):
        try:
            locator = self.get_locator("lblThongBaoNhapTen")
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_TBNhapSDT(self):
        try:
            locator = self.get_locator("lblThongBaoNhapSoDienThoai")
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_TBNhapDC(self):
        try:
            locator = self.get_locator("lblThongBaoNhapDiaChi")
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_TBChiCoSo(self):
        try:
            locator = self.get_locator("lblThongBaoDienThoaiChiCoSo")
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_TB10So(self):
        try:
            locator = self.get_locator("lblThongBaoDienThoai10so")
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    def get_Error(self):
        try:
            locator = self.get_locator("Loi")
            element = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except TimeoutException:
            return ""
