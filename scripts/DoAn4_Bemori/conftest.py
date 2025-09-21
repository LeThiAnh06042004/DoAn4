import os
import pytest
from core.base_driver import BaseDriver
from core.report_manager import ReportManager

@pytest.fixture(scope="class")
def driver(request):
    driver_manager = BaseDriver()
    driver = driver_manager.get_driver()
    request.cls.driver = driver
    yield driver
    driver_manager.quit_driver()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    if result.when == "call" and result.failed:
        driver = item.funcargs.get("driver")
        if driver:
            report_manager = ReportManager()
            report_folder = report_manager.create_report_folder()
            screenshot_path = report_manager.save_screenshot(driver, item.name, report_folder)
            report_path = report_manager.generate_report(item.name, "FAILED", report_folder)
            print(f"\nScreenshot đã lưu: {screenshot_path}")
            print(f"Báo cáo đã lưu: {report_path}")