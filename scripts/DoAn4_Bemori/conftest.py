import os
import pytest
from utils.report_manager import init_report_dirs
from utils.logger import init_logger
from core.base_driver import BaseDriver

#cấu hình pytest nâng cao
# Khởi tạo thư mục + logger
REPORT_DIRS = init_report_dirs()
LOGGER, LOG_FILE = init_logger(REPORT_DIRS["logs_dir"])
HTML_REPORT_FILE = os.path.join(REPORT_DIRS["html_dir"], "report.html")


# Tích hợp pytest-html để sinh báo cáo
def pytest_configure(config):
    config.option.htmlpath = HTML_REPORT_FILE
    config.option.self_contained_html = True
    LOGGER.info(f"Báo cáo đã được lưu tại: {HTML_REPORT_FILE}")


#khai báo 1 fixture cung cấp tài nguyên cho test
@pytest.fixture
def driver(request):
    base_driver = BaseDriver() #khởi tạo webdriver
    driver = base_driver.get_driver()
    yield driver

    # Nếu test fail thì chụp screenshot
    # rep_call.failed: true nếu test case đó thất bại.
    if request.node.rep_call.failed: # request.node: đối tg đại diện cho test hiện tại
        screenshot_path = os.path.join(
            REPORT_DIRS["screenshots_dir"], f"{request.node.name}.png"
        )
        driver.save_screenshot(screenshot_path)
        LOGGER.error(f"Test failed. Screenshot saved: {screenshot_path}")

    else:
        LOGGER.info(f"Test passed: {request.node.name}")

    driver.quit()



# Hook để biết test pass/fail
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Lưu trạng thái vào item để fixture driver sử dụng
    # rep.when có 3 trạng thái là setup (trc khi chạy test), call (trong khi chạy), teardown (sau khi chạy)
    setattr(item, "rep_" + rep.when, rep)
