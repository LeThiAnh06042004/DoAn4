import os
import pytest
import base64
import logging
from utils.report_manager import init_report_dirs
from utils.logger import init_logger
from core.base_driver import BaseDriver

#khởi tạo report, logger và file báo cáo chạy 1 lần
REPORT_DIRS = init_report_dirs()
LOGGER, LOG_FILE = init_logger(REPORT_DIRS["logs_dir"])
HTML_REPORT_FILE = os.path.join(REPORT_DIRS["html_dir"], "report.html")

#cấu hình pytest lúc bắt đầu
def pytest_configure(config):
    #xuất report ra và gộp chung 1 file
    config.option.htmlpath = HTML_REPORT_FILE
    config.option.self_contained_html = True
    LOGGER.info(f"Báo cáo HTML: {HTML_REPORT_FILE}")


#quản lý webdriver cho mỗi test
@pytest.fixture
def driver(request):
    LOGGER.info(f"Bắt đầu: {request.node.name} =====")

    #tạo driver, đọc config và mở browser
    base_driver = BaseDriver()
    driver = base_driver.get_driver()
    yield driver

    #nếu test fail
    if request.node.rep_call.failed:
        #chụp màn hình khi fail
        screenshot_path = os.path.join(
            REPORT_DIRS["screenshots_dir"], f"{request.node.name}.png"
        )
        driver.save_screenshot(screenshot_path)
        LOGGER.error(f"TEST FAILED: {request.node.name}")
        LOGGER.error(f"Screenshot: {screenshot_path}")
    else:
        LOGGER.info(f"TEST PASSED: {request.node.name}")

    driver.quit()
    LOGGER.info(f"Kết thúc: {request.node.name} =====\n")


#bắt kết quả test
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    #bắt kq, xd test pass/fail
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    # gắn ảnh vào report
    if rep.when == "call" and rep.failed: #gắn ảnh khi test fail ở phase call
        driver = item.funcargs.get("driver") #lấy driver từ fixture
        pytest_html = item.config.pluginmanager.getplugin("html") #lấy plugin từ pytest-html

        if driver and pytest_html:
            #chuyển ảnh sang base64 và gán trực tiếp vào html
            png = driver.get_screenshot_as_png()
            encoded = base64.b64encode(png).decode("utf-8")

            extra = getattr(rep, "extra", [])
            #thêm ảnh vào ds đính kèm
            extra.append(
                pytest_html.extras.image(
                    encoded, #nd ảnh
                    mime_type="image/png", #kiểu file
                    extension="png" #đuôi hiển thị
                )
            )
            rep.extra = extra #gắn tài nguyên vào kq test
