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
# ==================================================
UC_FILE = "UC_DangNhap_NetaBooks.txt"
LOCATOR_FILE = "DangNhap_NetaBooks_locators.yaml"
DATA_FILE = "data_DangNhap_NetaBooks.csv"


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
    # LẤY TÊN CHỨC NĂNG TỪ FILE USE CASE
    # Ví dụ: UC_DatHangNhanh.txt -> DatHangNhanh
    # ==================================================
    function_name = (
        os.path.basename(uc_path)
        .replace("UC_", "")
        .replace(".txt", "")
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
    # XUẤT TEST CASE RA EXCEL QA DOCUMENT
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
        f"SCR_{function_name}.xlsx"
    )

    export_script_to_excel(
        keyword_steps,
        script_path
    )

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