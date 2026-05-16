import os

from AI.TestCase import testcase_generator
from AI.TestCase.testcase_excel_exporter import export_testcases_to_excel
from AI.TestCase.script_generator import generate_keyword_steps
from AI.TestCase.excel_script_exporter import export_script_to_excel


# ==================================================
# CẤU HÌNH ĐẦU VÀO
# Người dùng chỉ cần sửa 3 biến này
# ==================================================
UC_FILE = "UC_BinhLuan.txt"
LOCATOR_FILE = "BinhLuan_locators.yaml"
DATA_FILE = "data_BinhLuan.sqlite"


def run_generation():
    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    project_root = os.path.abspath(
        os.path.join(
            base_dir,
            "..",
            ".."
        )
    )

    # ==================================================
    # INPUT PATHS
    # ==================================================
    uc_path = os.path.join(
        base_dir,
        "UC",
        UC_FILE
    )

    locator_path = os.path.join(
        project_root,
        "resources",
        "locators",
        LOCATOR_FILE
    )

    data_path = os.path.join(
        project_root,
        "resources",
        "data",
        DATA_FILE
    )

    # ==================================================
    # VALIDATE INPUT
    # ==================================================
    if not os.path.exists(uc_path):
        raise FileNotFoundError(
            f"Không tìm thấy Use Case: {uc_path}"
        )

    if not os.path.exists(locator_path):
        raise FileNotFoundError(
            f"Không tìm thấy Locator: {locator_path}"
        )

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Không tìm thấy Data: {data_path}"
        )

    # ==================================================
    # FUNCTION NAME
    # ==================================================
    function_name = (
        os.path.basename(uc_path)
        .replace("UC_", "")
        .replace(".txt", "")
    )

    # ==================================================
    # READ USE CASE
    # ==================================================
    with open(
            uc_path,
            "r",
            encoding="utf-8"
    ) as f:
        use_case_text = f.read()

    # ==================================================
    # AI SINH TEST CASE
    # ==================================================
    testcases = testcase_generator.generate_testcases_from_usecase(
        use_case_text
    )

    # ==================================================
    # SAVE TEST CASE JSON
    # TC/<file>
    # ==================================================
    tc_folder = os.path.join(
        base_dir,
        "TC"
    )

    os.makedirs(
        tc_folder,
        exist_ok=True
    )

    tc_path = os.path.join(
        tc_folder,
        f"TC_{function_name}.json"
    )

    testcase_generator.save_testcases(
        testcases,
        tc_path
    )

    # ==================================================
    # EXPORT TEST CASE EXCEL
    # ==================================================
    template_path = os.path.join(
        base_dir,
        "Sample_TestCase.xlsx"
    )

    export_testcases_to_excel(
        testcases=testcases,
        module_name=function_name,
        template_path=template_path
    )

    # ==================================================
    # TEST CASE -> TEST SCRIPT
    # KHÔNG DÙNG AI
    # ==================================================
    keyword_steps = generate_keyword_steps(
        testcases=testcases,
        locator_path=locator_path,
        data_path=data_path
    )

    # ==================================================
    # EXPORT SCRIPT VÀO test/cases
    # ==================================================
    script_folder = os.path.join(
        project_root,
        "test",
        "cases"
    )

    os.makedirs(
        script_folder,
        exist_ok=True
    )

    script_path = os.path.join(
        script_folder,
        f"SCR_{function_name}.xlsx"
    )

    export_script_to_excel(
        keyword_steps,
        script_path
    )

    # ==================================================
    # LOG
    # ==================================================
    print("===== GENERATION DONE =====")
    print(f"Use Case : {uc_path}")
    print(f"Locator  : {locator_path}")
    print(f"Data     : {data_path}")
    print(f"TC JSON  : {tc_path}")
    print(f"TC Excel : {template_path}")
    print(f"Script   : {script_path}")


if __name__ == "__main__":
    run_generation()