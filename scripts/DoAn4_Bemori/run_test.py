import pytest

from utils.excel_reader import read_excel_to_testcases
from utils.data_loader import *
from utils.locator_reader import LocatorReader
from core.kw_common import KWCommon
from core.kw_dispatcher import KeywordDispatcher
from core.step_excutor import execute_steps
from utils.logger import logging


# ================= CONFIG =================
SCRIPT_PATH = "test/cases/SCR_MuaHang.xlsx"
DATA_PATH = "resources/data/data_MuaHang.txt"
LOCATOR_PATH = "resources/locators/MuaHang_locators.yaml"

TARGET_TC = None     # None = all | "TC_001" = run 1
USE_DATA = False          # True = dùng data
# ==========================================


# ===== INJECT DATA =====
def inject_data(steps, data_row):
    new_steps = []

    for step in steps:
        value = str(step.get("value", ""))

        for key, val in data_row.items():
            value = value.replace(f"${{{key}}}", str(val))

        new_step = step.copy()
        new_step["value"] = value
        new_steps.append(new_step)

    return new_steps


# ===== LOAD TESTCASE =====
testcases = read_excel_to_testcases(SCRIPT_PATH)

if TARGET_TC:
    testcases = [tc for tc in testcases if tc["name"] == TARGET_TC]


# ===== LOAD DATA =====
data = load_yaml_data(DATA_PATH) if USE_DATA else [None]


# ===== BUILD TEST MATRIX =====
test_matrix = [(tc, d) for tc in testcases for d in data]


# ===== PARAMETRIZE =====
@pytest.mark.parametrize(
    "tc,data_row",
    test_matrix,
    ids=[
        f"{tc['name']}" if not USE_DATA else f"{tc['name']}[data{i}]"
        for i, (tc, _) in enumerate(test_matrix, start=1)
    ]
)
def test_run(driver, tc, data_row):

    logger = logging.getLogger("TestLogger")

    locator_reader = LocatorReader(LOCATOR_PATH)
    kw = KWCommon(driver, locator_reader=locator_reader)
    dispatcher = KeywordDispatcher(kw)

    logger.info(f"===== TESTCASE: {tc['name']} =====")
    logger.info(f"DATA: {data_row}")

    has_failed = False   # 🔥 KEY FIX

    try:
        if USE_DATA and data_row is not None:
            steps = inject_data(tc["steps"], data_row)
        else:
            steps = tc["steps"]

        execute_steps(dispatcher, steps, logger)

        logger.info(f"TESTCASE PASSED: {tc['name']}")

    except Exception as e:
        has_failed = True
        logger.error(f"TESTCASE FAILED: {tc['name']}")
        logger.error(str(e))

    # 🔥 QUYẾT ĐỊNH PASS/FAIL CHO PYTEST
    if has_failed:
        pytest.fail(f"{tc['name']} FAILED")