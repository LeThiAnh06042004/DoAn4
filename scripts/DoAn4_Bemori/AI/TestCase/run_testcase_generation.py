import os

from AI.TestCase import testcase_generator

from AI.TestCase.execution_path_builder import (
    build_execution_paths
)

from AI.TestCase.testcase_validator import (
    validate_testcases
)

from AI.TestCase.testcase_excel_exporter import (
    export_testcases_to_excel
)

from AI.TestCase.script_generator import (
    generate_keyword_steps
)

from AI.TestCase.excel_script_exporter import (
    export_script_to_excel
)


# ==================================================
# CẤU HÌNH ĐẦU VÀO
# Người dùng chỉ cần sửa 3 biến này
# ==================================================
UC_FILE = "UC_DatHangNhanh.txt"
LOCATOR_FILE = "DatHangNhanh_locators.yaml"
DATA_FILE = "data_DatHangNhanh.json"


def get_missing_path_ids(validation_report):
    missing_path_ids = []

    for error in validation_report.get("errors", []):
        if error.get("type") == "PATH_TRACEABILITY_ERROR":
            detail = error.get("detail", {})
            missing_path_ids.extend(
                detail.get("missing_path_ids", [])
            )

    return list(dict.fromkeys(missing_path_ids))


def get_missing_action_errors(validation_report):
    errors = []

    for error in validation_report.get("errors", []):
        if error.get("type") == "MISSING_USER_ACTION":
            errors.append(error)

    return errors


def remove_duplicate_testcases(testcases):
    result = []
    seen_path_ids = set()

    for tc in testcases:
        path_id = tc.get("path_id", "")

        if not path_id:
            result.append(tc)
            continue

        if path_id in seen_path_ids:
            continue

        seen_path_ids.add(path_id)
        result.append(tc)

    return result


def replace_testcase_by_path_id(
        testcases,
        new_testcase
):
    path_id = new_testcase.get("path_id", "")

    if not path_id:
        return testcases

    replaced = False
    result = []

    for tc in testcases:
        if tc.get("path_id") == path_id:
            result.append(new_testcase)
            replaced = True
        else:
            result.append(tc)

    if not replaced:
        result.append(new_testcase)

    return result


def regenerate_missing_testcases(
        execution_paths,
        testcases,
        validation_report
):
    missing_path_ids = get_missing_path_ids(
        validation_report
    )

    if not missing_path_ids:
        return testcases

    print("===== REGENERATE MISSING PATHS =====")
    print(f"Missing path ids: {missing_path_ids}")

    missing_paths = [
        path for path in execution_paths
        if path.get("path_id") in missing_path_ids
    ]

    if not missing_paths:
        return testcases

    regenerated = testcase_generator.generate_testcases_from_usecase(
        missing_paths,
        regenerate_mode=True
    )

    if isinstance(regenerated, dict):
        regenerated = [regenerated]

    for new_tc in regenerated:
        testcases = replace_testcase_by_path_id(
            testcases,
            new_tc
        )

    testcases = remove_duplicate_testcases(
        testcases
    )

    return testcases


def regenerate_missing_action_testcases(
        execution_paths,
        testcases,
        validation_report
):
    missing_action_errors = get_missing_action_errors(
        validation_report
    )

    if not missing_action_errors:
        return testcases

    print("===== REGENERATE MISSING ACTION TESTCASES =====")

    path_map = {
        path.get("path_id"): path
        for path in execution_paths
    }

    for error in missing_action_errors:
        path_id = error.get("path_id")
        detail = error.get("detail", {})
        missing_actions = detail.get(
            "missing_steps",
            []
        )

        path = path_map.get(path_id)

        if not path:
            continue

        print(
            f"Regenerate testcase for {path_id}, "
            f"missing actions: {missing_actions}"
        )

        regenerated = testcase_generator.generate_testcases_from_usecase(
            [path],
            regenerate_mode=True,
            missing_actions=missing_actions
        )

        if isinstance(regenerated, dict):
            regenerated = [regenerated]

        if not regenerated:
            continue

        new_tc = regenerated[0]

        testcases = replace_testcase_by_path_id(
            testcases,
            new_tc
        )

    testcases = remove_duplicate_testcases(
        testcases
    )

    return testcases


def validate_with_regeneration(
        execution_paths,
        testcases,
        max_retry=2
):
    validation_report = validate_testcases(
        execution_paths,
        testcases
    )

    print("===== VALIDATION REPORT =====")
    print(validation_report)

    retry_count = 0

    while (
            not validation_report["valid"]
            and retry_count < max_retry
    ):
        changed = False

        missing_path_ids = get_missing_path_ids(
            validation_report
        )

        if missing_path_ids:
            testcases = regenerate_missing_testcases(
                execution_paths,
                testcases,
                validation_report
            )
            changed = True

        missing_action_errors = get_missing_action_errors(
            validation_report
        )

        if missing_action_errors:
            testcases = regenerate_missing_action_testcases(
                execution_paths,
                testcases,
                validation_report
            )
            changed = True

        if not changed:
            break

        validation_report = validate_testcases(
            execution_paths,
            testcases
        )

        print("===== VALIDATION REPORT AFTER REGENERATE =====")
        print(validation_report)

        retry_count += 1

    return testcases, validation_report


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
    # BUILD EXECUTION PATHS
    # ==================================================
    execution_paths = build_execution_paths(
        use_case_text
    )

    print("===== EXECUTION PATHS =====")

    for path in execution_paths:
        print(path)

    # ==================================================
    # AI SINH TEST CASE
    # ==================================================
    testcases = testcase_generator.generate_testcases_from_usecase(
        execution_paths
    )

    if isinstance(testcases, dict):
        testcases = [testcases]

    testcases = remove_duplicate_testcases(
        testcases
    )

    # ==================================================
    # VALIDATE TEST CASE
    # Nếu thiếu path hoặc thiếu action thì regenerate riêng
    # ==================================================
    testcases, validation_report = validate_with_regeneration(
        execution_paths=execution_paths,
        testcases=testcases,
        max_retry=2
    )

    if not validation_report["valid"]:
        raise Exception(
            f"Testcase validation failed: "
            f"{validation_report}"
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
        data_path=data_path,
        execution_paths=execution_paths
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