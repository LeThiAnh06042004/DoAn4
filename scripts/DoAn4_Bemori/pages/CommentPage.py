from core.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert

class CommentPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver, "BinhLuan_locators.yaml")

    def click_SP(self):
        self.click("lnkSanPham")

    def nhapND(self, nd):
        self.send_keys("txtNoiDungBinhLuan", nd)

    def nhapHoTen(self, ten):
        self.send_keys("txtHoTen", ten)

    def nhapSDT(self, sdt):
        self.send_keys("txtSoDienThoai", sdt)

    def click_BinhLuan(self):
        self.click("btnGuiBinhLuan")

        # ===== FIX ALERT =====
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = Alert(self.driver)
            print(f"[ALERT]: {alert.text}")
            alert.accept()
        except TimeoutException:
            pass
        except UnexpectedAlertPresentException:
            try:
                Alert(self.driver).accept()
            except:
                pass

    # ===== GET MESSAGE =====
    def get_TBThanhCong(self):
        return self._safe_get_text("lblThongBaoThanhCong")

    def get_TBNhapBL(self):
        return self._safe_get_text("lblThongBaoNhapBinhLuan")

    def get_TBNhapTen(self):
        return self._safe_get_text("lblThongBaoNhapTen")

    def get_TBNhapSDT(self):
        return self._safe_get_text("lblThongBaoNhapSoDienThoai")

    def get_TBChiCoSo(self):
        return self._safe_get_text("lblThongBaoSoDienThoaiChiCoSo")

    def get_TB10So(self):
        return self._safe_get_text("lblThongBaoSoDienThoai10so")

    def _safe_get_text(self, locator):
        try:
            return self.get_text(locator)
        except:
            return ""
