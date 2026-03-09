from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class BinhLuanKeywords:
    """ Keyword library for BinhLuan
    Nghĩa tiếng Việt: Thư viện keyword cho chức năng BinhLuan """

    def __init__(self, driver, locator_reader=None):
        self.driver = driver
        self.locator_reader = locator_reader
        self.wait = WebDriverWait(driver, 10)

    def _resolve_locator(self, locator_input):
        """ Chuyển locator key thành tuple (By, value) """
        if isinstance(locator_input, tuple) and len(locator_input) == 2:
            return locator_input
        if self.locator_reader is None:
            raise ValueError("LocatorReader chưa được truyền")
        loc_dict = self.locator_reader.get(locator_input)
        strategy_str = loc_dict.get("by", "id").lower()
        value = loc_dict.get("value")
        strategy_map = {"id": By.ID, "xpath": By.XPATH, "css": By.CSS_SELECTOR}
        by_strategy = strategy_map.get(strategy_str)
        return (by_strategy, value)

    # ====================== VERIFY KEYWORDS ======================
    def VERIFY_EMPTY_COMMENT_ERROR(self):
        """ Xác minh thông báo khi bình luận rỗng """
        resolved = self._resolve_locator("TBNhapBL")
        try:
            self.wait.until(EC.visibility_of_element_located(resolved))
            text = self.driver.find_element(*resolved).text.strip()
            return "Bạn chưa nhập bình luận" in text
        except TimeoutException:
            return False

    def VERIFY_EMPTY_NAME_ERROR(self):
        """ Xác minh thông báo khi tên rỗng """
        resolved = self._resolve_locator("TBNhapTen")
        try:
            self.wait.until(EC.visibility_of_element_located(resolved))
            text = self.driver.find_element(*resolved).text.strip()
            return "Bạn chưa nhập tên" in text
        except TimeoutException:
            return False

    def VERIFY_NAME_MAX_LENGTH(self):
        """ Xác minh độ dài tối đa của họ tên """
        resolved = self._resolve_locator("txtHoTen")
        try:
            text = self.driver.find_element(*resolved).get_attribute("value")
            return len(text) <= 255
        except:
            return False

    def VERIFY_EMPTY_PHONE_ERROR(self):
        """ Xác minh thông báo khi SDT rỗng """
        resolved = self._resolve_locator("TBNhapSDT")
        try:
            self.wait.until(EC.visibility_of_element_located(resolved))
            text = self.driver.find_element(*resolved).text.strip()
            return "Bạn chưa nhập số điện thoại" in text
        except TimeoutException:
            return False

    def VERIFY_PHONE_NON_DIGIT_CHARACTERS(self):
        """ Xác minh SDT chứa ký tự không phải số """
        resolved = self._resolve_locator("TBChiCoSo")
        try:
            self.wait.until(EC.visibility_of_element_located(resolved))
            text = self.driver.find_element(*resolved).text.strip()
            return "Số điện thoại chỉ bao gồm những số" in text
        except TimeoutException:
            return False

    def VERIFY_PHONE_MIN_LENGTH(self):
        """ Xác minh SDT < 10 số """
        resolved = self._resolve_locator("TB10so")
        try:
            self.wait.until(EC.visibility_of_element_located(resolved))
            text = self.driver.find_element(*resolved).text.strip()
            return "Số điện thoại phải có ít nhất 10 số" in text
        except TimeoutException:
            return False

    def SUBMIT_VALID_COMMENT_SUCCESS(self):
        """ Xác minh gửi bình luận thành công """
        resolved = self._resolve_locator("TBThanhCong")
        try:
            self.wait.until(EC.visibility_of_element_located(resolved))
            text = self.driver.find_element(*resolved).text.strip()
            return "Gửi bình luận thành công" in text
        except TimeoutException:
            return False