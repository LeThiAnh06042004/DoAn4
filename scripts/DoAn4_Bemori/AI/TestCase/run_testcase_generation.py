import os
import json

from AI.TestCase import testcase_generator
from AI.TestCase.testcase_excel_exporter import export_testcases_to_excel
from AI.TestCase.script_generator import generate_keyword_steps
from AI.TestCase.excel_script_exporter import export_script_to_excel


def run_generation():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # ================= USE CASE =================
    uc_path = os.path.join(base_dir, "UC", "UC_TimKiem.txt")

    with open(uc_path, "r", encoding="utf-8") as f:
        use_case_text = f.read()

    # ================= AI: GENERATE TC =================
    testcases = testcase_generator.generate_testcases_from_usecase(use_case_text)

    function_name = os.path.basename(uc_path).replace("UC_", "").replace(".txt", "")

    # ================= FOLDER =================
    tc_folder = os.path.join(base_dir, "TC", function_name)
    os.makedirs(tc_folder, exist_ok=True)

    # ================= SAVE JSON =================
    tc_path = os.path.join(tc_folder, f"TC_{function_name}.json")
    testcase_generator.save_testcases(testcases, tc_path)

    # ================= EXPORT TC EXCEL =================
    template_path = os.path.join(base_dir, "Sample_TestCase.xlsx")

    export_testcases_to_excel(
        testcases=testcases,
        module_name=function_name,
        template_path=template_path
    )

    # ================= ROOT =================
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

    # ================= LOCATOR =================
    locator_path = os.path.join(
        project_root,
        "locators",
        f"{function_name}_locators.yaml"
    )

    # ================= DATA =================
    data_folder = os.path.join(project_root, "data")

    possible_files = [
        f"data_{function_name}.txt",
        f"data_{function_name}.csv",
        f"data_{function_name}.json",
        f"data_{function_name}.xlsx",
        f"data_{function_name}.xls",
        f"data_{function_name}.yaml",
        f"data_{function_name}.yml",
        f"data_{function_name}.sqlite"
    ]

    data_path = None
    for file in possible_files:
        full = os.path.join(data_folder, file)
        if os.path.exists(full):
            data_path = full
            break

    print(f"TC: {tc_path}")
    print(f"Locator: {locator_path}")
    print(f"Data: {data_path if data_path else 'Không có'}")

    # ================= AI: TC → SCRIPT =================
    keyword_steps = generate_keyword_steps(
        testcases=testcases,
        locator_path=locator_path,
        data_path=data_path
    )

    # ================= EXPORT SCRIPT =================
    script_path = os.path.join(
        base_dir,
        "scripts",
        "SCR",
        f"SCR_{function_name}.xlsx"
    )

    os.makedirs(os.path.dirname(script_path), exist_ok=True)

    export_script_to_excel(keyword_steps, script_path)

    print(f"JSON: {tc_path}")
    print(f"Excel TC: {template_path}")
    print(f"Script: {script_path}")


if __name__ == "__main__":
    run_generation()