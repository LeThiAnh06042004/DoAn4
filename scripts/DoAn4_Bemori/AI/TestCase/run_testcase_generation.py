import os
import shutil

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

from AI.TestCase.evaluation_result_parser import (
    find_log_file_by_function_web,
    parse_execution_log
)

from AI.TestCase.auto_evaluation import (
    evaluate_auto_testing_result
)

from AI.TestCase.auto_evaluation_excel_exporter import (
    export_auto_evaluation_to_excel
)

# ==================================================
# CẤU HÌNH ĐẦU VÀO
# ==================================================
UC_FILE = "UC_MuaHang_Bemori.txt"
LOCATOR_FILE = "MuaHang_Bemori_locators.yaml"
DATA_FILE = "data_MuaHang_Bemori.txt"


# ==================================================
# TÁCH TÊN CHỨC NĂNG VÀ TÊN WEBSITE
# ==================================================
def extract_function_and_web_name(uc_file):
    file_name = os.path.basename(uc_file)

    file_name = (
        file_name
        .replace("UC_", "")
        .replace(".txt", "")
    )

    parts = file_name.split("_")

    if len(parts) < 2:
        raise ValueError(
            "Tên file Use Case phải có dạng: "
            "UC_<Tên chức năng>_<Tên web>.txt"
        )

    function_name = parts[0]

    web_name = "_".join(parts[1:])

    return function_name, web_name


# ==================================================
# LẤY DANH SÁCH PATH BỊ THIẾU TEST CASE
# ==================================================
def get_missing_path_ids(validation_report):
    missing_path_ids = []

    for error in validation_report.get("errors", []):
        if error.get("type") == "PATH_TRACEABILITY_ERROR":
            detail = error.get("detail", {})
            missing_path_ids.extend(
                detail.get("missing_path_ids", [])
            )

    return list(dict.fromkeys(missing_path_ids))


# ==================================================
# LẤY DANH SÁCH LỖI THIẾU ACTION
# ==================================================
def get_missing_action_errors(validation_report):
    errors = []

    for error in validation_report.get("errors", []):
        if error.get("type") == "MISSING_USER_ACTION":
            errors.append(error)

    return errors


# ==================================================
# LẤY DANH SÁCH LỖI NHIỀU ĐIỀU KIỆN LỖI TRONG 1 TEST CASE
# ==================================================
def get_multiple_negative_errors(validation_report):
    errors = []

    for error in validation_report.get("errors", []):
        if error.get("type") == "MULTIPLE_NEGATIVE_CONDITIONS":
            errors.append(error)

    return errors


# ==================================================
# LOẠI TEST CASE TRÙNG PATH_ID
# ==================================================
def remove_duplicate_testcases(testcases):
    result = []
    seen_path_ids = set()

    for tc in testcases:
        path_id = tc.get("path_id", "")

        # Nếu testcase không có path_id thì vẫn giữ lại
        if not path_id:
            result.append(tc)
            continue

        # Nếu path_id đã xuất hiện thì bỏ testcase trùng
        if path_id in seen_path_ids:
            continue

        seen_path_ids.add(path_id)
        result.append(tc)

    return result


# ==================================================
# THAY TEST CASE CŨ BẰNG TEST CASE MỚI THEO PATH_ID
# ==================================================
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

    # Nếu path_id chưa tồn tại thì thêm mới
    if not replaced:
        result.append(new_testcase)

    return result


# ==================================================
# REGENERATE TEST CASE CHO PATH BỊ THIẾU
# ==================================================
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

    # Lấy đúng các execution path bị thiếu testcase
    missing_paths = [
        path for path in execution_paths
        if path.get("path_id") in missing_path_ids
    ]

    if not missing_paths:
        return testcases

    # Gọi AI sinh lại đúng các path bị thiếu
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


# ==================================================
# REGENERATE TEST CASE BỊ THIẾU ACTION
# ==================================================
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

        # Gửi lại đúng execution path bị lỗi
        # và danh sách action bị thiếu để AI bổ sung
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


# ==================================================
# REGENERATE TEST CASE BỊ NHIỀU NEGATIVE CONDITION
# ==================================================
def regenerate_multiple_negative_testcases(
        execution_paths,
        testcases,
        validation_report
):
    negative_errors = get_multiple_negative_errors(
        validation_report
    )

    if not negative_errors:
        return testcases

    print("===== REGENERATE MULTIPLE NEGATIVE CONDITION TESTCASES =====")

    path_map = {
        path.get("path_id"): path
        for path in execution_paths
    }

    tc_map = {
        tc.get("test_case_id"): tc
        for tc in testcases
    }

    for error in negative_errors:
        tc_id = error.get("testcase")
        old_tc = tc_map.get(tc_id)

        if not old_tc:
            continue

        path_id = old_tc.get("path_id")
        path = path_map.get(path_id)

        if not path:
            continue

        print(
            f"Regenerate testcase {tc_id} for {path_id} "
            f"because MULTIPLE_NEGATIVE_CONDITIONS"
        )

        # Gửi lại đúng execution path của testcase lỗi.
        # Truyền thêm validation_errors để prompt biết lỗi cần sửa.
        regenerated = testcase_generator.generate_testcases_from_usecase(
            [path],
            regenerate_mode=True,
            validation_errors=[error]
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


# ==================================================
# VALIDATION + SELF-HEALING LOOP
# ==================================================
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

        # 1. Nếu thiếu execution path thì sinh lại path bị thiếu
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

        # 2. Nếu thiếu action thì sinh lại testcase bị thiếu action
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

        # 3. Nếu testcase có nhiều negative condition thì sinh lại testcase đó
        negative_errors = get_multiple_negative_errors(
            validation_report
        )

        if negative_errors:
            testcases = regenerate_multiple_negative_testcases(
                execution_paths,
                testcases,
                validation_report
            )
            changed = True

        # Nếu không có lỗi nào thuộc nhóm có thể tự regenerate thì dừng
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


def remove_extra_path_testcases(testcases, execution_paths):
    valid_path_ids = {
        path.get("path_id")
        for path in execution_paths
    }

    return [
        tc for tc in testcases
        if tc.get("path_id") in valid_path_ids
    ]

# ==================================================
# MAIN PIPELINE
# ==================================================
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
    # BUILD ĐƯỜNG DẪN INPUT
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
    # KIỂM TRA FILE INPUT CÓ TỒN TẠI KHÔNG
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
    # LẤY TÊN CHỨC NĂNG VÀ WEBSITE TỪ FILE USE CASE
    # ==================================================
    function_name, web_name = extract_function_and_web_name(
        UC_FILE
    )

    # ==================================================
    # ĐỌC USE CASE
    # ==================================================
    with open(
            uc_path,
            "r",
            encoding="utf-8"
    ) as f:
        use_case_text = f.read()

    # ==================================================
    # USE CASE -> EXECUTION PATHS
    # ==================================================
    execution_paths = build_execution_paths(
        use_case_text
    )

    print("===== EXECUTION PATHS =====")

    for path in execution_paths:
        print(path)

    # ==================================================
    # AI SINH TEST CASE TỪ EXECUTION PATHS
    # ==================================================
    testcases = testcase_generator.generate_testcases_from_usecase(
        execution_paths
    )

    if isinstance(testcases, dict):
        testcases = [testcases]

    testcases = remove_duplicate_testcases(
        testcases
    )

    testcases = remove_extra_path_testcases(
        testcases,
        execution_paths
    )

    # ==================================================
    # VALIDATE TEST CASE + SELF-HEALING
    # Nếu thiếu path, thiếu action hoặc nhiều negative condition
    # thì framework sẽ gọi AI sinh lại testcase lỗi.
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
    # LƯU TEST CASE JSON
    # ==================================================
    tc_json_folder = os.path.join(
        base_dir,
        "TC",
        "JSON"
    )

    os.makedirs(
        tc_json_folder,
        exist_ok=True
    )

    tc_path = os.path.join(
        tc_json_folder,
        f"TC_{function_name}_{web_name}.json"
    )

    testcase_generator.save_testcases(
        testcases,
        tc_path
    )

    # ==================================================
    # XUẤT TEST CASE RA EXCEL QA DOCUMENT
    # Mỗi chức năng là một sheet.
    # ==================================================
    tc_excel_folder = os.path.join(
        base_dir,
        "TC",
        "Excel"
    )

    os.makedirs(
        tc_excel_folder,
        exist_ok=True
    )

    base_template_path = os.path.join(
        base_dir,
        "Sample_TestCase.xlsx"
    )

    template_path = os.path.join(
        tc_excel_folder,
        f"Sample_TestCase_{web_name}.xlsx"
    )

    if not os.path.exists(template_path):
        shutil.copy(
            base_template_path,
            template_path
        )

    export_testcases_to_excel(
        testcases=testcases,
        module_name=function_name,
        template_path=template_path
    )

    # ==================================================
    # TEST CASE -> KEYWORD TEST SCRIPT
    # Sinh keyword steps từ test case:
    # - map keyword
    # - map locator
    # - bind data
    # - tạo verify step
    # ==================================================
    keyword_steps = generate_keyword_steps(
        testcases=testcases,
        locator_path=locator_path,
        data_path=data_path,
        execution_paths=execution_paths
    )

    # ==================================================
    # EXPORT SCRIPT RA FILE EXCEL
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
        f"SCR_{function_name}_{web_name}.xlsx"
    )

    export_script_to_excel(
        keyword_steps,
        script_path
    )

    # ==================================================
    # ĐÁNH GIÁ TỰ ĐỘNG TEST CASE + TEST SCRIPT
    # ==================================================

    # Folder reports của framework thực thi
    reports_dir = os.path.join(
        project_root,
        "reports"
    )

    # Tìm log đúng chức năng + website
    execution_log_file = find_log_file_by_function_web(
        reports_dir=reports_dir,
        function_name=function_name,
        web_name=web_name
    )

    # Parse kết quả PASS / FAIL từ log
    execution_results = parse_execution_log(
        execution_log_file
    ) if execution_log_file else []

    # ==================================================
    # TẠO FOLDER ĐÁNH GIÁ
    # ==================================================
    evaluation_folder = os.path.join(
        base_dir,
        "Evaluation"
    )

    os.makedirs(
        evaluation_folder,
        exist_ok=True
    )

    evaluation_path = os.path.join(
        evaluation_folder,
        f"EV_{function_name}_{web_name}.xlsx"
    )

    # ==================================================
    # ĐÁNH GIÁ TỰ ĐỘNG
    # ==================================================
    evaluation_summary, testcase_details, script_details = evaluate_auto_testing_result(
        execution_paths=execution_paths,
        testcases=testcases,
        keyword_steps=keyword_steps,
        validation_report=validation_report,
        execution_results=execution_results
    )

    # ==================================================
    # EXPORT FILE ĐÁNH GIÁ
    # ==================================================
    export_auto_evaluation_to_excel(
        summary=evaluation_summary,
        testcase_details=testcase_details,
        script_details=script_details,
        output_path=evaluation_path,
        function_name=function_name,
        web_name=web_name
    )

    print("\n===== AUTO EVALUATION =====")
    print(f"Log file: {execution_log_file}")
    print(f"Evaluation file: {evaluation_path}")

    # ==================================================
    # LOG KẾT QUẢ
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