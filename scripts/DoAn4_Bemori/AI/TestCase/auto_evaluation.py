import re
from unidecode import unidecode

from AI.TestCase.testcase_validator import validate_testcases
from utils.action_extractor import extract_action
from utils.data_binding_utils import normalize_key


NOT_AVAILABLE = "N/A" # Dùng khi chưa có dữ liệu hoặc không có kết quả.

# danh sách các keyword thuộc nhóm kiểm tra kết quả
VERIFY_KEYWORDS = [
    "VERIFY_ELEMENT_TEXT_EQUALS",
    "VERIFY_TEXT_CONTAINS",
    "VERIFY_ELEMENT_VISIBLE",
    "VERIFY_ELEMENT_PRESENT"
]


# Hàm tính phần trăm
def percent(numerator, denominator):
    # Nếu mẫu số bằng 0 thì trả về 100 để tránh lỗi
    if denominator == 0:
        return 100.0

    return round(
        (numerator / denominator) * 100,
        2
    )


def normalize_text(text):
    # Nếu đầu vào là None thì trả về chuỗi rỗng
    if text is None:
        return ""

    # Chuyển text về string, viết thường, xóa khoảng trắng đầu/cuối
    text = str(text).lower().strip()
    text = unidecode(text) # Bỏ dấu tiếng Việt
    text = re.sub(r"[^a-zA-Z0-9_ ]+", " ", text) # Xóa ký tự đặc biệt
    text = re.sub(r"\s+", " ", text) # Gộp nhiều khoảng trắng thành một khoảng trắng

    return text.strip()


# Hàm gom các keyword gần giống nhau về cùng một nhóm
def normalize_action(keyword):
    # Nếu keyword là click, double click hoặc right click thì đều xem là nhóm CLICK
    if keyword in [
        "CLICK",
        "DOUBLE_CLICK",
        "RIGHT_CLICK"
    ]:
        return "CLICK"

    # Nhập text hoặc xóa text đều gom vào nhóm INPUT
    if keyword in [
        "INPUT_TEXT",
        "CLEAR_TEXT"
    ]:
        return "INPUT"

    # Các thao tác chọn dropdown được gom vào nhóm SELECT
    if keyword in [
        "SELECT_BY_TEXT",
        "SELECT_BY_VALUE",
        "SELECT_BY_INDEX"
    ]:
        return "SELECT"

    # Check hoặc uncheck checkbox đều thuộc nhóm CHECKBOX
    if keyword in [
        "CHECK_CHECKBOX",
        "UNCHECK_CHECKBOX"
    ]:
        return "CHECKBOX"

    # Nếu không thuộc nhóm nào thì giữ nguyên keyword ban đầu
    return keyword


# kiểm tra keyword có phải keyword verify không
def is_verify_keyword(keyword):
    return keyword in VERIFY_KEYWORDS


# Chuẩn hóa nội dung step trước
def is_user_action(step):
    text = normalize_text(step)

    # Nếu step rỗng thì không phải user action
    if not text:
        return False

    # Nếu step có chữ "he thong" thì xem là bước hệ thống, ko phải hđ người dùng
    if "he thong" in text:
        return False

    # Lấy keyword tương ứng từ nội dung step
    keyword = extract_action(step)

    # Nếu không tìm được keyword thì không tính
    if not keyword:
        return False

    # Nếu keyword là verify thì không phải hành động người dùng
    if is_verify_keyword(keyword):
        return False

    # Nếu vượt qua tất cả điều kiện trên thì đây là user action
    return True


# Hàm lấy ra các step là hành động người dùng trong execution_path
def get_user_action_steps(execution_path):
    return [
        step for step in execution_path.get("steps", [])
        if is_user_action(step)
    ]


def get_important_words(text):
    text_norm = normalize_text(text)

    # danh sách các từ ít quan trọng, cần loại bỏ khi so sánh
    stop_words = {
        "step",
        "nguoi",
        "dung",
        "he",
        "thong",
        "vao",
        "o",
        "va",
        "cac",
        "cua",
        "tren",
        "tai",
        "cho",
        "de",
        "duoc",
        "la",
        "mot",
        "co",
        "hop",
        "le",
        "khong"
    }

    # Tách text thành từng từ, loại stop word và loại từ chỉ có 1 ký tự
    return [
        word for word in text_norm.split()
        if word not in stop_words and len(word) > 1
    ]


# Hàm tính mức độ trùng từ giữa step trong execution path và step trong test case
def word_overlap_score(path_step, testcase_step):
    # Lấy các từ quan trọng của path_step, đồng thời chuẩn hóa testcase_step
    path_words = get_important_words(path_step)
    tc_text = normalize_text(testcase_step)

    # Nếu path không có từ quan trọng thì điểm là 0
    if not path_words:
        return 0

    matched = 0 # Biến đếm số từ khớp

    # Duyệt từng từ quan trọng của path. Nếu từ đó xuất hiện trong testcase step thì tăng matched
    for word in path_words:
        if word in tc_text:
            matched += 1

    # Trả về tỷ lệ khớp
    return matched / len(path_words)


# kiểm tra một step trong execution path có liên quan/tương ứng với một step trong testcase không
def is_step_related(path_step, testcase_step):
    # Lấy keyword của hai step
    path_keyword = extract_action(path_step)
    tc_keyword = extract_action(testcase_step)

    # Nếu một trong hai không có keyword thì không liên quan
    if not path_keyword or not tc_keyword:
        return False

    # Nếu một trong hai là verify keyword thì không xét là user action
    if is_verify_keyword(path_keyword) or is_verify_keyword(tc_keyword):
        return False

    # Chuẩn hóa action
    path_action = normalize_action(path_keyword)
    tc_action = normalize_action(tc_keyword)

    # Nếu nhóm hành động khác nhau thì không liên quan
    if path_action != tc_action:
        return False

    # Tính điểm trùng từ
    score = word_overlap_score(
        path_step,
        testcase_step
    )

    # Nếu điểm khớp từ khóa từ 30% trở lên thì xem là cùng step
    if score >= 0.3:
        return True

    # Nếu điểm chưa đạt 0.3 thì tiếp tục lấy danh sách từ quan trọng của hai step
    path_words = get_important_words(path_step)
    tc_words = get_important_words(testcase_step)

    if path_words and tc_words:
        common = set(path_words).intersection(set(tc_words)) # Tìm từ chung

        # Nếu có ít nhất một từ chung thì vẫn xem là liên quan
        if len(common) > 0:
            return True

    return False # Nếu không thỏa điều kiện nào thì không liên quan


# Hàm đếm xem testcase giữ lại được bao nhiêu hành động người dùng từ execution path
def count_preserved_user_actions(execution_path, testcase):
    # Lấy danh sách user action trong execution path và danh sách step trong testcase
    path_steps = get_user_action_steps(execution_path)
    testcase_steps = testcase.get("steps", [])

    matched = 0 # số step tìm thấy
    missing_steps = [] # các step bị thiếu

    used_tc_indexes = set() # lưu index testcase step đã dùng để tránh match trùng

    # Duyệt từng step cần có
    for path_step in path_steps:
        found = False # Ban đầu coi như chưa tìm thấy

        # Duyệt từng step trong testcase
        for index, tc_step in enumerate(testcase_steps):
            # Nếu step testcase này đã được dùng để match với step trước đó thì bỏ qua
            if index in used_tc_indexes:
                continue

            # Nếu hai step liên quan nhau thì:
            # Tăng số matched, đánh dấu testcase step đã dùng, rồi dừng tìm cho path step hiện tạo
            if is_step_related(path_step, tc_step):
                matched += 1
                used_tc_indexes.add(index)
                found = True
                break

        # Nếu duyệt hết testcase mà không tìm thấy step tương ứng thì đưa vào danh sách thiếu
        if not found:
            missing_steps.append(path_step)

    return matched, len(path_steps), missing_steps # trả về số step khớp, tổng step cần có, danh sách step thiếu


# Ktra Script có bước kiểm tra kết quả hay không?
def has_verify_step(script):
    # Kiểm tra script có tồn tại không
    if not script:
        return False

    # Duyệt toàn bộ keyword step
    for step in script.get("steps", []):
        # Kiểm tra keyword có thuộc VERIFY_KEYWORDS không
        if step.get("keyword") in VERIFY_KEYWORDS:
            return True

    return False


# hàm đánh giá Expected Result Accuracy
def count_expected_result_accuracy(
        execution_path,
        testcase,
        script=None
):
    # Lấy expected_messages
    expected_messages = execution_path.get(
        "expected_messages",
        []
    )

    # Lấy expected_result
    testcase_expected = testcase.get(
        "expected_result",
        []
    )

    # Ghép expected_result thành chuỗi
    testcase_expected_text = normalize_key(
        " ".join(testcase_expected)
    )

    # ==================================================
    # CASE 1: Có expected_messages cụ thể
    # Bắt buộc expected_result phải khớp nội dung message.
    # ==================================================
    if expected_messages:
        matched = 0
        missing = []

        for msg in expected_messages:
            msg_norm = normalize_key(msg)

            if msg_norm and msg_norm in testcase_expected_text:
                matched += 1
            else:
                missing.append(msg)

        return matched, len(expected_messages), missing

    # ==================================================
    # CASE 2: Không có expected_messages
    # Nhưng nếu test script đã có VERIFY step thì vẫn đạt.
    # Ví dụ:
    # - Hiển thị danh sách sản phẩm phù hợp
    # - Hiển thị tất cả danh sách sản phẩm
    # ==================================================
    if testcase_expected:
        return 1, 1, []

    if has_verify_step(script):
        return 1, 1, []

    return 0, 1, [
        "Thiếu expected_result hoặc verify step"
    ]


# Hàm này tìm tc tương ứng với path_id
def find_testcase_by_path_id(testcases, path_id):
    for tc in testcases:
        if tc.get("path_id") == path_id:
            return tc

    return None


# Hàm này tìm script tương ứng với testcase
def find_script_by_testcase(keyword_steps, testcase):
    tc_id = testcase.get("test_case_id", "")
    path_id = testcase.get("path_id", "")

    for script in keyword_steps:
        if script.get("test_case_id") == tc_id:
            return script

        if script.get("path_id") == path_id:
            return script

    return None


def evaluate_test_cases(
        execution_paths,
        testcases,
        keyword_steps,
        validation_report=None
):
    details = [] # Danh sách chi tiết từng path

    total_paths = len(execution_paths)
    covered_paths = 0 # Đếm số path có testcase

    total_required_actions = 0 # Tổng số action cần có
    total_preserved_actions = 0 # Tổng số action được giữ lại

    total_expected = 0 # Tổng expected
    total_expected_matched = 0 # Tổng expected match

    # Validator
    # Nếu caller không truyền validation_report thì tự validate.
    validation_report = validation_report or validate_testcases(
        execution_paths,
        testcases
    )

    error_path_ids = set() # Tạo tập path lỗi

    for error in validation_report.get("errors", []):
        path_id = error.get("path_id")

        if path_id:
            error_path_ids.add(path_id)

    # Duyệt từng execution path
    for path in execution_paths:
        path_id = path.get("path_id", "") # lấy path_id

        # Tìm testcase
        testcase = find_testcase_by_path_id(
            testcases,
            path_id
        )

        # Nếu có testcase
        if testcase:
            covered_paths += 1 # Tăng coverage

            # Tìm script
            script = find_script_by_testcase(
                keyword_steps,
                testcase
            )

            # Tính completeness
            preserved, required, missing_steps = count_preserved_user_actions(
                path,
                testcase
            )

            # Tính expected accuracy
            expected_matched, expected_count, missing_expected = count_expected_result_accuracy(
                path,
                testcase,
                script
            )

            tc_id = testcase.get("test_case_id", "")

            # Kiểm tra validator
            # Nếu path không nằm trong error_path_ids thì PASS
            validation_status = (
                "PASS"
                if path_id not in error_path_ids
                else "FAIL"
            )

        # Nếu KHÔNG có testcase
        else:
            tc_id = ""
            required = len(get_user_action_steps(path))
            preserved = 0
            missing_steps = get_user_action_steps(path)

            expected_count = max(
                len(path.get("expected_messages", [])),
                1
            )
            expected_matched = 0
            missing_expected = path.get(
                "expected_messages",
                []
            )

            if not missing_expected:
                missing_expected = [
                    "Không có testcase tương ứng"
                ]

            validation_status = "FAIL"

        # Cộng dồn
        total_required_actions += required
        total_preserved_actions += preserved

        total_expected += expected_count
        total_expected_matched += expected_matched

        # Thêm vào details
        details.append({
            "path_id": path_id,
            "test_case_id": tc_id,
            "path_covered": testcase is not None,
            "required_actions": required,
            "preserved_actions": preserved,
            "missing_actions": missing_steps,
            "expected_count": expected_count,
            "expected_matched": expected_matched,
            "missing_expected": missing_expected,
            "validation_status": validation_status
        })

    # Tính KPI cuối
    # Coverage
    execution_path_coverage = percent(
        covered_paths,
        total_paths
    )

    # Completeness
    step_completeness = percent(
        total_preserved_actions,
        total_required_actions
    )

    # Expected Accuracy
    expected_result_accuracy = percent(
        total_expected_matched,
        total_expected
    )

    # đếm số path PASS
    validation_pass_count = sum(
        1 for item in details
        if item.get("validation_status") == "PASS"
    )

    validation_pass_rate = percent(
        validation_pass_count,
        len(details)
    )

    # Summary
    # Cuối cùng tạo summary = [...] gồm 4 metric: Execution Path Coverage, Step Completeness, Expected Result Accuracy, Validation Pass Rate
    # và trả về return summary, details
    summary = [
        {
            "group": "Test Case Quality",
            "metric": "Execution Path Coverage",
            "formula": "Paths with Test Case / Total Execution Paths",
            "value": execution_path_coverage,
            "note": "Đánh giá AI sinh đủ test case cho execution path hay không"
        },
        {
            "group": "Test Case Quality",
            "metric": "Step Completeness",
            "formula": "Preserved User Actions / Required User Actions",
            "value": step_completeness,
            "note": "Đánh giá test case có giữ đủ bước user action không"
        },
        {
            "group": "Test Case Quality",
            "metric": "Expected Result Accuracy",
            "formula": "Matched Expected Results / Required Expected Results",
            "value": expected_result_accuracy,
            "note": "Nếu không có expected message, dùng verify step để xác nhận"
        },
        {
            "group": "Test Case Quality",
            "metric": "Validation Pass Rate",
            "formula": "Validation PASS Test Cases / Total Test Cases",
            "value": validation_pass_rate,
            "note": "Đánh giá tỷ lệ test case pass validator"
        }
    ]

    return summary, details


# đánh giá test case có sinh được keyword script không và script chạy pass/fail thế nào
def evaluate_test_scripts(
        testcases, # danh sách test case AI đã sinh
        keyword_steps, # danh sách script keyword được sinh từ test case
        execution_results=None # kết quả sau khi chạy test script
):
    details = [] # kết quả chi tiết cho từng test case

    total_testcases = len(testcases) # Đếm tổng số test case
    generated_scripts = 0 # Biến đếm số script sinh được

    # Nếu execution_results là None, nó được đổi thành danh sách rỗng.
    execution_results = execution_results or []

    # biến list thành dictionary để tra cứu nhanh theo test_case_id
    execution_map = {
        item.get("test_case_id"): item
        for item in execution_results
    }

    # Khởi tạo biến đếm thực thi
    executed_count = 0 # số script đã được chạy
    passed_count = 0 # số script chạy thành công

    for tc in testcases:
        tc_id = tc.get("test_case_id", "") # Lấy mã test case

        # Tìm keyword script tương ứng theo test_case_id nếu ko có thì tìm theo path_id
        script = find_script_by_testcase(
            keyword_steps,
            tc
        )

        # Nếu có script thì tăng số script sinh được
        if script:
            generated_scripts += 1

        execution = execution_map.get(tc_id) # Lấy kết quả thực thi của test case

        # Nếu test case đã có kết quả thực thi
        if execution:
            executed_count += 1 # Tăng số đã chạy

            # Nếu status là PASS
            if execution.get("status") == "PASS":
                passed_count += 1

            # Lấy trạng thái thực thi
            execution_status = execution.get("status", "")
            # Lấy lỗi thực thi
            execution_error = execution.get("error", "")

        # Nếu test case chưa có kết quả thực thi
        else:
            execution_status = NOT_AVAILABLE
            execution_error = ""

        # Ghi chi tiết vào details
        details.append({
            "test_case_id": tc_id,
            "path_id": tc.get("path_id", ""),
            "script_generated": script is not None,
            "execution_status": execution_status,
            "execution_error": execution_error
        })

    # Tính Script Generation Coverage = Generated Scripts / Total Test Cases
    script_generation_coverage = percent(
        generated_scripts,
        total_testcases
    )

    # Tính Script Execution Pass Rate = Passed Scripts / Executed Scripts
    # Nếu có ít nhất một script đã chạy thì mới tính tỷ lệ pass
    if executed_count > 0:
        script_execution_pass_rate = percent(
            passed_count,
            executed_count
        )

        execution_note = "Đã lấy từ kết quả thực thi test script"

    # Nếu chưa có script nào được chạy
    else:
        script_execution_pass_rate = NOT_AVAILABLE
        execution_note = "Chưa có kết quả thực thi test script"

    # Tạo summary gồm 2 metric:
    # 1. Script Generation Coverage
    # 2. Script Execution Pass Rate
    summary = [
        {
            "group": "Test Script Verification",
            "metric": "Script Generation Coverage",
            "formula": "Generated Scripts / Total Test Cases",
            "value": script_generation_coverage,
            "note": "Đánh giá test case có chuyển được thành keyword script không"
        },
        {
            "group": "Test Script Verification",
            "metric": "Script Execution Pass Rate",
            "formula": "Passed Scripts / Executed Scripts",
            "value": script_execution_pass_rate,
            "note": execution_note
        }
    ]

    # summary: kết quả tổng hợp để ghi vào sheet Summary.
    # details: chi tiết từng test case để ghi vào sheet TestScript_Evaluation.
    return summary, details


# hàm tổng, gom kết quả đánh giá test case + test script
def evaluate_auto_testing_result(
        execution_paths,
        testcases,
        keyword_steps,
        validation_report=None,
        execution_results=None
):
    # Gọi đánh giá test case
    tc_summary, tc_details = evaluate_test_cases(
        execution_paths,
        testcases,
        keyword_steps,
        validation_report
    )

    # Gọi đánh giá test script
    script_summary, script_details = evaluate_test_scripts(
        testcases,
        keyword_steps,
        execution_results
    )

    # Gộp summary
    summary = tc_summary + script_summary

    # Kết quả cuối gồm:
    # summary: 6 chỉ số tổng hợp.
    # tc_details: chi tiết đánh giá test case.
    # script_details: chi tiết đánh giá test script.
    return summary, tc_details, script_details