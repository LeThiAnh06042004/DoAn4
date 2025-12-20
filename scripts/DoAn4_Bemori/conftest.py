import os
import pytest
import base64
import logging
from utils.report_manager import init_report_dirs
from utils.logger import init_logger
from core.base_driver import BaseDriver

REPORT_DIRS = init_report_dirs()
LOGGER, LOG_FILE = init_logger(REPORT_DIRS["logs_dir"])
HTML_REPORT_FILE = os.path.join(REPORT_DIRS["html_dir"], "report.html")


def pytest_configure(config):
    config.option.htmlpath = HTML_REPORT_FILE
    config.option.self_contained_html = True
    LOGGER.info(f"Báo cáo HTML: {HTML_REPORT_FILE}")


@pytest.fixture
def driver(request):
    LOGGER.info(f"Bắt đầu: {request.node.name} =====")

    base_driver = BaseDriver()
    driver = base_driver.get_driver()
    yield driver

    if request.node.rep_call.failed:
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    # ===================== GẮN ẢNH VÀO REPORT =====================
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("driver")
        pytest_html = item.config.pluginmanager.getplugin("html")

        if driver and pytest_html:
            png = driver.get_screenshot_as_png()
            encoded = base64.b64encode(png).decode("utf-8")

            extra = getattr(rep, "extra", [])
            extra.append(
                pytest_html.extras.image(
                    encoded,
                    mime_type="image/png",
                    extension="png"
                )
            )
            rep.extra = extra
