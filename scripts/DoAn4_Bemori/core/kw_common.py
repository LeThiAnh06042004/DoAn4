from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException, NoSuchFrameException, NoSuchWindowException
import time
import logging


class KWCommon:
    """ Bộ keyword dùng chung cho toàn framework (Keyword Driven Testing - KDT) """

    def __init__(self, driver, locator_reader=None, timeout=10):
        self.driver = driver
        self.locator_reader = locator_reader
        self.wait = WebDriverWait(driver, timeout)
        self.actions = ActionChains(driver)
        self._if_condition = False  # dùng cho IF/ELSE

    def _resolve_locator(self, locator_input):
        """ Chuyển locator key (string từ YAML) thành tuple (By, value) """
        if isinstance(locator_input, tuple) and len(locator_input) == 2:
            return locator_input

        if not isinstance(locator_input, str):
            raise ValueError(f"Locator phải là string hoặc tuple (By, value), nhận được: {type(locator_input)}")

        if self.locator_reader is None:
            raise ValueError("LocatorReader chưa được truyền → không resolve được locator key")

        try:
            loc_dict = self.locator_reader.get(locator_input)
            strategy_str = loc_dict.get("strategy") or loc_dict.get("by", "id").lower()
            value = loc_dict.get("value")

            if not value:
                raise ValueError(f"Locator '{locator_input}' thiếu 'value'")

            strategy_map = {
                "id": By.ID,
                "name": By.NAME,
                "xpath": By.XPATH,
                "css": By.CSS_SELECTOR,
                "css selector": By.CSS_SELECTOR,
                "class": By.CLASS_NAME,
                "class name": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "tag name": By.TAG_NAME,
                "link text": By.LINK_TEXT,
                "partial link text": By.PARTIAL_LINK_TEXT,
            }

            by_strategy = strategy_map.get(strategy_str)
            if by_strategy is None:
                raise ValueError(f"Strategy không hợp lệ '{strategy_str}'")

            return (by_strategy, value)

        except KeyError:
            raise KeyError(f"Locator key '{locator_input}' KHÔNG tồn tại trong YAML")

    def find_element(self, locator_name):
        by, value = self._resolve_locator(locator_name)
        return self.wait.until(
            EC.presence_of_element_located((by, value))
        )

    # ==================================================
    # 1. NAVIGATION - Điều hướng trang web
    # ==================================================
    def OPEN_URL(self, url: str):
        """ Mở một URL mới """
        self.driver.get(url)

    def REFRESH_PAGE(self):
        """ Làm mới trang hiện tại """
        self.driver.refresh()

    def GO_BACK(self):
        """ Quay lại trang trước """
        self.driver.back()

    def GO_FORWARD(self):
        """ Tiến tới trang tiếp theo """
        self.driver.forward()

    def CLOSE_BROWSER(self):
        """ Đóng trình duyệt """
        self.driver.quit()

    def MAXIMIZE_WINDOW(self):
        """ Phóng to cửa sổ trình duyệt """
        self.driver.maximize_window()

    def GET_CURRENT_URL(self):
        """ Lấy URL hiện tại của trang """
        return self.driver.current_url

    def GET_PAGE_TITLE(self):
        """ Lấy tiêu đề trang hiện tại """
        return self.driver.title

    def VERIFY_URL(self, expected_url: str):
        """ Kiểm tra URL hiện tại có đúng không """
        assert self.driver.current_url == expected_url, f"URL thực tế: {self.driver.current_url} != {expected_url}"

    def VERIFY_PAGE_TITLE(self, expected_title: str):
        """ Kiểm tra tiêu đề trang có đúng không """
        assert self.driver.title == expected_title, f"Tiêu đề thực tế: {self.driver.title} != {expected_title}"

    def SWITCH_TO_NEW_TAB(self):
        """ Chuyển sang tab mới nhất (tab cuối cùng) """
        self.wait.until(EC.number_of_windows_to_be(len(self.driver.window_handles)))
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def SWITCH_TO_TAB_BY_TITLE(self, title_part: str):
        """ Chuyển sang tab có tiêu đề chứa chuỗi nhất định """
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if title_part in self.driver.title:
                return
        raise Exception(f"Không tìm thấy tab chứa tiêu đề '{title_part}'")

    def SWITCH_TO_FRAME(self, locator):
        """ Chuyển vào iframe theo locator """
        resolved = self._resolve_locator(locator)
        self.driver.switch_to.frame(self.driver.find_element(*resolved))

    def SWITCH_TO_DEFAULT_CONTENT(self):
        """ Thoát ra khỏi iframe, trở về nội dung chính """
        self.driver.switch_to.default_content()

    def SWITCH_TO_ALERT(self):
        """ Chuyển sang alert nếu có """
        return self.driver.switch_to.alert

    # ==================================================
    # 2. ACTION - Thao tác người dùng
    # ==================================================
    def CLICK(self, locator):
        """ Click vào element """
        resolved = self._resolve_locator(locator)
        self.driver.find_element(*resolved).click()

    def DOUBLE_CLICK(self, locator):
        """ Double click vào element """
        resolved = self._resolve_locator(locator)
        self.actions.double_click(self.driver.find_element(*resolved)).perform()

    def RIGHT_CLICK(self, locator):
        """ Chuột phải vào element """
        resolved = self._resolve_locator(locator)
        self.actions.context_click(self.driver.find_element(*resolved)).perform()

    def HOVER(self, locator):
        """ Di chuột đến element (hover) """
        resolved = self._resolve_locator(locator)
        self.actions.move_to_element(self.driver.find_element(*resolved)).perform()

    def INPUT_TEXT(self, locator, text: str = ""):
        """ Nhập văn bản vào input, tự động clear trước """
        # xử lý dữ liệu None
        if text is None:
            text = ""
        resolved = self._resolve_locator(locator)
        element = self.driver.find_element(*resolved)
        element.clear()
        # chỉ send_keys khi có dữ liệu
        if str(text).strip():
            element.send_keys(str(text))

    def GET_TEXT(self, locator):
        """Lấy text của element"""
        resolved = self._resolve_locator(locator)
        element = self.driver.find_element(*resolved)
        return element.text

    def CLEAR_TEXT(self, locator):
        """ Xóa nội dung trong input """
        resolved = self._resolve_locator(locator)
        self.driver.find_element(*resolved).clear()

    def SEND_KEYS(self, locator, keys):
        """ Gửi phím đặc biệt (ENTER, TAB, ESC...) """
        resolved = self._resolve_locator(locator)
        self.driver.find_element(*resolved).send_keys(keys)

    def PRESS_ENTER(self, locator):
        """ Nhấn phím Enter trong element """
        resolved = self._resolve_locator(locator)
        self.driver.find_element(*resolved).send_keys(Keys.ENTER)

    def UPLOAD_FILE(self, locator, file_path: str):
        """ Upload file (đơn hoặc nhiều file nếu input hỗ trợ) """
        resolved = self._resolve_locator(locator)
        self.driver.find_element(*resolved).send_keys(file_path)

    def SELECT_BY_TEXT(self, locator, text: str):
        """ Chọn option trong dropdown theo text hiển thị """
        resolved = self._resolve_locator(locator)
        Select(self.driver.find_element(*resolved)).select_by_visible_text(text)

    def SELECT_BY_VALUE(self, locator, value: str):
        """ Chọn option trong dropdown theo value """
        resolved = self._resolve_locator(locator)
        Select(self.driver.find_element(*resolved)).select_by_value(value)

    def SELECT_BY_INDEX(self, locator, index: int):
        """ Chọn option trong dropdown theo chỉ số (0-based) """
        resolved = self._resolve_locator(locator)
        Select(self.driver.find_element(*resolved)).select_by_index(index)

    def CHECK_CHECKBOX(self, locator):
        """ Tick checkbox nếu chưa được tick """
        resolved = self._resolve_locator(locator)
        element = self.driver.find_element(*resolved)
        if not element.is_selected():
            element.click()

    def UNCHECK_CHECKBOX(self, locator):
        """ Bỏ tick checkbox nếu đang được tick """
        resolved = self._resolve_locator(locator)
        element = self.driver.find_element(*resolved)
        if element.is_selected():
            element.click()

    def SCROLL_TO_ELEMENT(self, locator):
        """ Cuộn trang đến vị trí element """
        resolved = self._resolve_locator(locator)
        element = self.driver.find_element(*resolved)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def SCROLL_TO_TOP(self):
        """ Cuộn trang lên đầu """
        self.driver.execute_script("window.scrollTo(0, 0);")

    def SCROLL_TO_BOTTOM(self):
        """ Cuộn trang xuống cuối """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def DRAG_AND_DROP(self, source_locator, target_locator):
        """ Kéo thả từ element nguồn đến element đích """
        source_resolved = self._resolve_locator(source_locator)
        target_resolved = self._resolve_locator(target_locator)
        source = self.driver.find_element(*source_resolved)
        target = self.driver.find_element(*target_resolved)
        self.actions.drag_and_drop(source, target).perform()

    def CLICK_JS(self, locator):
        """ Click bằng JavaScript (khi element bị che hoặc không click được bình thường) """
        resolved = self._resolve_locator(locator)
        element = self.driver.find_element(*resolved)
        self.driver.execute_script("arguments[0].click();", element)

    def FOCUS_ELEMENT(self, locator):
        """ Đưa focus vào element (thường dùng cho input) """
        resolved = self._resolve_locator(locator)
        element = self.driver.find_element(*resolved)
        self.driver.execute_script("arguments[0].focus();", element)

    # ==================================================
    # 3. VERIFICATION - Xác minh & Assert
    # ==================================================
    def VERIFY_ELEMENT_PRESENT(self, locator_name):
        element = self.find_element(locator_name)

        if not element:
            raise AssertionError(f"Không tìm thấy element: {locator_name}")

        return True

    def VERIFY_ELEMENT_VISIBLE(self, locator):
        """ Kiểm tra element hiển thị trên màn hình (visible) """
        resolved = self._resolve_locator(locator)
        try:
            self.wait.until(EC.visibility_of_element_located(resolved))
            self._if_condition = True
            return True
        except TimeoutException:
            self._if_condition = False
            return False

    def VERIFY_ELEMENT_NOT_PRESENT(self, locator):
        """ Kiểm tra element KHÔNG tồn tại trong DOM """
        resolved = self._resolve_locator(locator)
        try:
            self.wait.until(EC.invisibility_of_element_located(resolved))
            return True
        except TimeoutException:
            return False

    def VERIFY_TEXT_CONTAINS(self, locator, expected_text: str):
        """ Kiểm tra text của element có chứa chuỗi mong đợi """
        resolved = self._resolve_locator(locator)
        try:
            actual = self.driver.find_element(*resolved).text.strip()
            return expected_text.strip() in actual
        except NoSuchElementException:
            return False

    def VERIFY_ELEMENT_TEXT_EQUALS(self, locator, expected_text: str):
        """Kiểm tra text của element bằng đúng chuỗi"""

        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        resolved = self._resolve_locator(locator)

        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(resolved)
        )

        actual = element.text.strip()

        if not actual:
            actual = element.get_attribute("textContent") or ""

        if not actual:
            actual = element.get_attribute("innerText") or ""

        actual = actual.strip()
        expected = expected_text.strip()

        assert actual == expected, (
            f"Text thực tế: '{actual}' != '{expected}'"
        )

    def VERIFY_ATTRIBUTE(self, locator, attr_name: str, expected_value: str):
        """ Kiểm tra giá trị của attribute (class, href, value...) """
        resolved = self._resolve_locator(locator)
        actual = self.driver.find_element(*resolved).get_attribute(attr_name)
        assert actual == expected_value, f"Attribute '{attr_name}' thực tế: '{actual}' != '{expected_value}'"

    def VERIFY_ELEMENT_COUNT(self, locator, expected_count: int):
        """ Kiểm tra số lượng element khớp locator """
        resolved = self._resolve_locator(locator)
        count = len(self.driver.find_elements(*resolved))
        assert count == expected_count, f"Số lượng element: {count} != {expected_count}"

    def VERIFY_ELEMENT_SELECTED(self, locator):
        """ Kiểm tra checkbox/radio đã được chọn """
        resolved = self._resolve_locator(locator)
        return self.driver.find_element(*resolved).is_selected()

    def VERIFY_ALERT_PRESENT(self):
        """ Kiểm tra có alert/popup hiện """
        try:
            self.wait.until(EC.alert_is_present())
            return True
        except TimeoutException:
            return False

    def VERIFY_ALERT_TEXT_CONTAINS(self, expected_text: str):
        """ Kiểm tra text trong alert có chứa chuỗi """
        try:
            alert = self.driver.switch_to.alert
            return expected_text in alert.text
        except NoAlertPresentException:
            return False

    def IS_ELEMENT_PRESENT(self, locator_name):
        resolved = self._resolve_locator(locator_name)
        elements = self.driver.find_elements(*resolved)
        return len(elements) > 0


    # ==================================================
    # 4. SYSTEM / WAIT / DEBUG - Hệ thống, chờ đợi, debug
    # ==================================================
    def WAIT_FOR_ELEMENT_VISIBLE(self, locator, timeout=10):
        """ Chờ element hiển thị trên màn hình (visible) """
        resolved = self._resolve_locator(locator)
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(resolved))
            return True
        except TimeoutException:
            return False

    def WAIT_FOR_ELEMENT_PRESENT(self, locator, timeout=10):
        """ Chờ element tồn tại trong DOM (có thể ẩn) """
        resolved = self._resolve_locator(locator)
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(resolved))
            return True
        except TimeoutException:
            return False

    def WAIT_FOR_ELEMENT_CLICKABLE(self, locator, timeout=10):
        """ Chờ element có thể click được """
        resolved = self._resolve_locator(locator)
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(resolved))
            return True
        except TimeoutException:
            return False

    def WAIT_FOR_SECONDS(self, seconds):
        """ Chờ cứng theo giây """
        time.sleep(int(seconds))

    def WAIT_FOR_PAGE_LOAD(self, timeout=15):
        """ Chờ trang load hoàn toàn (document.readyState == 'complete') """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False

    def LOG_INFO(self, message: str):
        """ Ghi log mức INFO """
        logging.info(message)

    def LOG_ERROR(self, message: str):
        """ Ghi log mức ERROR """
        logging.error(message)

    def TAKE_SCREENSHOT(self, file_path: str):
        """ Chụp ảnh màn hình """
        self.driver.save_screenshot(file_path)

    def TAKE_SCREENSHOT_ON_FAIL(self, file_path: str = "screenshot_fail.png"):
        """ Chụp ảnh khi test fail (dùng trong except) """
        self.driver.save_screenshot(file_path)

    def EXECUTE_JS(self, script: str):
        """ Thực thi lệnh JavaScript tùy chỉnh """
        return self.driver.execute_script(script)

    def GET_ALERT_TEXT(self):
        """ Lấy nội dung alert nếu có """
        try:
            alert = self.driver.switch_to.alert
            return alert.text
        except NoAlertPresentException:
            return None

    def ACCEPT_ALERT(self):
        """ Đồng ý alert nếu có """
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            pass

    def DISMISS_ALERT(self):
        """ Hủy alert nếu có """
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
        except NoAlertPresentException:
            pass