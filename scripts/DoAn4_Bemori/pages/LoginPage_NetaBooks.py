from core.base_page import BasePage


class LoginPage_NetaBooks(BasePage):
    def __init__(self, driver):
        super().__init__(driver, "DangNhap_NetaBooks_locators.yaml")

    # ===== ACTION =====
    def click_DangNhapLink(self):
        self.click("lnkDangNhap")

    def nhapEmail(self, email):
        self.send_keys("txtEmail", email)

    def nhapMatKhau(self, mat_khau):
        self.send_keys("txtMatKhau", mat_khau)

    def click_DangNhap(self):
        self.click("btnDangNhap")

    def dangNhap(self, email, mat_khau):
        self.nhapEmail(email)
        self.nhapMatKhau(mat_khau)
        self.click_DangNhap()

    # ===== GET MESSAGE / VERIFY TEXT =====
    def get_TBDangNhapThatBai(self):
        return self._safe_get_text("lblDangNhapThatBai")

    # ===== CHECK ELEMENT =====
    def is_DangNhapThanhCong(self):
        try:
            return self.is_visible("imgDangNhapThanhCong")
        except:
            return False

    def is_DangNhapThatBai(self):
        try:
            return self.is_visible("lblDangNhapThatBai")
        except:
            return False

    # ===== COMMON =====
    def _safe_get_text(self, locator):
        try:
            return self.get_text(locator)
        except:
            return ""