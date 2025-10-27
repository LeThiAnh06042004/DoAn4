from core.base_page import BasePage

class HomePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver, "TimKiem_locators.yaml")

    def nhap_tu_khoa(self, keyword):
        self.send_keys("txtTimKiem", keyword)

    def click_tim_kiem(self):
        self.click("btnTimKiem")

    def get_search_results(self):
        try:
            return self.get_text("txtTimThay")
        except:
            return ""

    def get_no_result_message(self):
        """Lấy thông báo khi không tìm thấy sản phẩm"""
        try:
            return self.get_text("txtKoTimThay")
        except:
            return ""
