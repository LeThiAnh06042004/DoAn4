import os
import re
import ast
import pytest
import base64
from selenium.common.exceptions import WebDriverException

from utils.report_manager import init_report_dirs
from utils.logger import init_logger
from core.base_driver import BaseDriver

from AI.TestCase.update_evaluation_after_execution import (
    update_evaluation_after_execution
)


# ==================================================
# ĐỌC SCRIPT_PATH TRỰC TIẾP TỪ run_test.py
# Không import run_test.py để tránh vòng lặp pytest.
# ==================================================
def find_run_test_file():
    current_dir = os.getcwd()

    # tìm file run_test
    candidate = os.path.join(
        current_dir,
        "run_test.py"
    )

    # nếu tồn tại
    if os.path.exists(candidate):
        return candidate

    return None


# Đọc giá trị SCRIPT_PATH bằng AST
def read_script_path_from_run_test(run_test_path):
    if not run_test_path or not os.path.exists(run_test_path):
        return ""

    with open(
            run_test_path,
            "r",
            encoding="utf-8"
    ) as f:
        # Parse thành AST
        tree = ast.parse(
            f.read()
        )

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                        isinstance(target, ast.Name)
                        and target.id == "SCRIPT_PATH" # tìm
                        and isinstance(node.value, ast.Constant)
                ):
                    return node.value.value # Lấy giá trị

    return ""


# Tách Function Name và Web Name để đặt tên (report, log)
def extract_function_web_from_script(script_path):
    file_name = os.path.basename(script_path)

    # bỏ SCR và .xlsx
    file_name = file_name.replace(
        "SCR_",
        ""
    )

    file_name = file_name.replace(
        ".xlsx",
        ""
    )

    parts = file_name.split("_")

    if len(parts) < 2:
        return "UnknownFunction", "UnknownWeb"

    function_name = parts[0]
    web_name = "_".join(parts[1:])

    return function_name, web_name


RUN_TEST_FILE = find_run_test_file()
SCRIPT_PATH = read_script_path_from_run_test(
    RUN_TEST_FILE
)

FUNCTION_NAME, WEB_NAME = extract_function_web_from_script(
    SCRIPT_PATH
)


# Khởi tạo thư mục report
REPORT_DIRS = init_report_dirs()

# Khởi tạo Logger
LOGGER, LOG_FILE = init_logger(
    REPORT_DIRS["logs_dir"],
    log_file_name=f"log_{FUNCTION_NAME}_{WEB_NAME}.txt"
)

# Tạo file HTML Report
HTML_REPORT_FILE = os.path.join(
    REPORT_DIRS["html_dir"],
    f"report_{FUNCTION_NAME}_{WEB_NAME}.html"
)

EXECUTION_RESULTS = {} # Biến lưu kết quả thực thi


# Tách Test Case ID
def extract_test_case_id(node_name):
    match = re.search(
        r"\[(TC_\d+)\]", # Regex -> lấy TC_001
        node_name
    )

    if match:
        return match.group(1)

    return node_name


# ===== CONFIGURE =====
# Hook pytest_configure(): Được gọi trước khi chạy test
def pytest_configure(config):
    # cấu hình
    config.option.htmlpath = HTML_REPORT_FILE # file HTML report
    config.option.self_contained_html = True # report chứa luôn CSS + ảnh

    # Ghi log
    LOGGER.info(f"Function: {FUNCTION_NAME}")
    LOGGER.info(f"Website: {WEB_NAME}")
    LOGGER.info(f"Báo cáo HTML: {HTML_REPORT_FILE}")


# ===== SAFE SCREENSHOT =====
# Chụp screenshot an toàn
def safe_screenshot(driver, path):
    try:
        # Kiểm tra: Nếu browser vẫn còn sống
        if driver and driver.session_id:
            driver.save_screenshot(path)
            return True
    # Nếu driver chết
    except Exception as e:
        print(f"Screenshot failed: {e}")

    return False


# ===== DRIVER FIXTURE =====
@pytest.fixture
def driver(request):
    LOGGER.info(f"Bắt đầu: {request.node.name} =====")

    # TRƯỚC TEST
    # Khởi tạo ChromeDriver
    base_driver = BaseDriver()
    driver = base_driver.get_driver()

    yield driver # Trả driver cho test

    # ===== SAU TEST =====
    # Nếu fail
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:

        # Tạo screenshot
        screenshot_path = os.path.join(
            REPORT_DIRS["screenshots_dir"],
            f"{request.node.name}.png"
        )

        # Ghi log
        if safe_screenshot(driver, screenshot_path):
            LOGGER.error(f"TEST FAILED: {request.node.name}")
            LOGGER.error(f"Screenshot: {screenshot_path}")
        else:
            LOGGER.error("Không chụp được screenshot (driver died)")

    # Nếu pass
    else:
        LOGGER.info(f"TEST PASSED: {request.node.name}")

    try:
        driver.quit()
    except:
        pass

    LOGGER.info(f"Kết thúc: {request.node.name} =====\n")


# ===== HOOK REPORT =====
# Được gọi sau mỗi testcase
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    setattr(
        item,
        "rep_" + rep.when,
        rep
    )

    # ===== SAVE EXECUTION RESULT =====
    if rep.when == "call":
        tc_id = extract_test_case_id(
            item.name
        )

        # Lưu trạng thái PASS
        if rep.passed:
            EXECUTION_RESULTS[tc_id] = {
                "test_case_id": tc_id,
                "status": "PASS",
                "error": ""
            }

        # Lưu trạng thái FAIL
        elif rep.failed:
            EXECUTION_RESULTS[tc_id] = {
                "test_case_id": tc_id,
                "status": "FAIL",
                "error": str(rep.longrepr)
            }

    # ===== ATTACH SCREENSHOT TO HTML =====
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get(
            "driver",
            None
        )

        pytest_html = item.config.pluginmanager.getplugin(
            "html"
        )

        if driver and pytest_html:
            try:
                png = driver.get_screenshot_as_png() # Lấy ảnh
                encoded = base64.b64encode(
                    png
                ).decode("utf-8") # encode

                extra = getattr(
                    rep,
                    "extra",
                    []
                )

                # Đính kèm: trong report HTML sẽ có ảnh lỗi ngay tại testcase bị fail.
                extra.append(
                    pytest_html.extras.image(
                        encoded,
                        mime_type="image/png",
                        extension="png"
                    )
                )

                rep.extra = extra

            except WebDriverException:
                print("Driver died → không attach screenshot")


# ===== AUTO UPDATE EVALUATION AFTER ALL TESTS =====
def pytest_sessionfinish(session, exitstatus):
    execution_results = list(
        EXECUTION_RESULTS.values()
    )

    # gọi để cập nhật file đánh giá
    update_evaluation_after_execution(
        function_name=FUNCTION_NAME,
        web_name=WEB_NAME,
        execution_results=execution_results
    )