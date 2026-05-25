import re
from unidecode import unidecode


# Chuẩn hóa text để so sánh step, matching, detect lỗi
def normalize_text(text):
    if text is None:
        return ""

    # Lowercase + strip
    text = str(text).lower().strip()
    # Bỏ dấu tiếng Việt
    text = unidecode(text)

    # Bỏ prefix Step 1:
    text = re.sub(
        r"^step\s*\d+\s*:\s*",
        "",
        text
    )

    # Bỏ prefix 1. / 1a.
    text = re.sub(
        r"^\d+[a-zA-Z]?\.\s*",
        "",
        text
    )

    # Bỏ punctuation
    text = re.sub(
        r"[\"“”':,.]",
        " ",
        text
    )

    return re.sub(r"\s+", " ", text).strip()


def remove_step_prefix(text):
    return normalize_text(text)


# lấy text trong dấu ngoặc kép
def extract_quoted_messages(text):
    if not text:
        return []

    results = []

    matches = re.findall(
        r'"([^"]+)"|“([^”]+)”',
        str(text)
    )

    for item in matches:
        value = item[0] or item[1]

        if value:
            results.append(value.strip())

    return results


# Kiểm tra testcase có đủ field không.
def validate_testcase_structure(testcase):
    required_fields = [
        "test_case_id",
        "path_id",
        "scenario",
        "precondition",
        "steps",
        "expected_result"
    ]

    missing_fields = []

    for field in required_fields:
        if field not in testcase:
            missing_fields.append(field)

    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields
    }


# Kiểm tra số lượng testcase.
def validate_testcase_count(execution_paths, testcases):
    return {
        "valid": len(execution_paths) == len(testcases),
        "expected": len(execution_paths),
        "actual": len(testcases)
    }


# Kiểm tra thiếu path/dư path
def validate_path_traceability(execution_paths, testcases):
    # Lấy danh sách path_id từ execution paths
    expected_path_ids = [
        path.get("path_id")
        for path in execution_paths
    ]

    # Lấy danh sách path_id từ testcase
    actual_path_ids = [
        tc.get("path_id")
        for tc in testcases
    ]

    # Tìm path bị thiếu testcase
    missing = [
        pid for pid in expected_path_ids
        if pid not in actual_path_ids
    ]

    extra = [
        pid for pid in actual_path_ids
        if pid not in expected_path_ids
    ]

    # Nếu thiếu path
    return {
        "valid": len(missing) == 0 and len(extra) == 0,
        "missing_path_ids": missing,
        "extra_path_ids": extra
    }


# Nhận diện step nội bộ hệ thống.
def is_system_step(step):
    step = normalize_text(step)

    system_keywords = [
        "he thong kiem tra",
        "he thong hien thi",
        "he thong xu ly",
        "system"
    ]

    return any(
        keyword in step
        for keyword in system_keywords
    )


def is_navigation_or_setup_step(step):
    """
    Các bước điều hướng/setup có thể được xử lý bởi:
    - precondition
    - OPEN_URL
    - setup của framework
    nên không bắt buộc phải validate như business action.
    """

    step = normalize_text(step)

    navigation_keywords = [
        "truy cap",
        "dieu huong",
        "mo trang",
        "mo man hinh",
        "mo chuc nang",
        "vao trang",
        "den trang"
    ]

    return any(
        keyword in step
        for keyword in navigation_keywords
    )


# extract keyword quan trọng
def get_important_words(text):
    text = normalize_text(text)

    # stop_word sẽ bị bỏ
    stop_words = {
        "nguoi",
        "dung",
        "vao",
        "tren",
        "duoc",
        "cac",
        "nhung",
        "mot",
        "cua",
        "cho",
        "voi",
        "khi",
        "neu",
        "thi",
        "la",
        "co",
        "tai",
        "den",
        "bang",
        "sau",
        "truoc"
    }

    return [
        word for word in text.split()
        if len(word) >= 3 and word not in stop_words
    ]


# Kiểm tra testcase step có tương ứng với execution path step không
def is_step_related(path_step, testcase_step):
    # Normalize text trước khi so sánh
    path_step = normalize_text(path_step)
    testcase_step = normalize_text(testcase_step)

    # NNếu step rỗng → False (ko thể ss)
    if not path_step or not testcase_step:
        return False

    # match hoàn toàn
    if path_step == testcase_step:
        return True

    # Partial match
    if path_step in testcase_step:
        return True

    # testcase viết ngắn hơn execution path
    if testcase_step in path_step:
        return True

    # Tách keyword quan trọng
    path_words = get_important_words(path_step)
    tc_words = set(get_important_words(testcase_step))

    if not path_words:
        return False

    # Đếm số keyword match
    matched = 0

    for word in path_words:
        if word in tc_words:
            matched += 1

    # Tính tỷ lệ match
    ratio = matched / len(path_words)

    return ratio >= 0.45 # Nếu match >= 45% → xem như related.


# AI thường: bỏ sót step, thiếu click button, thiếu verify. Hàm này detect điều đó.
def validate_missing_user_actions(execution_path, testcase):
    # Lấy step từ execution path và testcase
    path_steps = execution_path.get("steps", [])
    testcase_steps = testcase.get("steps", [])

    missing_steps = []

    # Duyệt path step để kiểm tra xem testcase có bỏ sót step nghiệp vụ nào không
    for path_step in path_steps:
        path_step_norm = normalize_text(path_step)

        # Bỏ qua system step và navigation step
        if is_system_step(path_step_norm):
            continue

        if is_navigation_or_setup_step(path_step_norm):
            continue

        found = False

        for tc_step in testcase_steps:
            # Gọi hàm is_step_related để kiểm tra step có tương ứng hay không.
            if is_step_related(
                    path_step_norm,
                    tc_step
            ):
                found = True
                break

        # Nếu không tìm thấy → missing step
        if not found:
            missing_steps.append(path_step_norm)

    # Trả kết quả validation
    return {
        "valid": len(missing_steps) == 0,
        "missing_steps": missing_steps
    }


# VD: Nếu execution path có "Đặt hàng thành công" thì testcase phải chứa message này.
def validate_expected_messages(execution_path, testcase):
    expected_messages = execution_path.get(
        "expected_messages",
        []
    )

    testcase_text = " ".join(
        testcase.get("steps", [])
        + testcase.get("expected_result", [])
    )

    missing_messages = []

    for message in expected_messages:
        if message not in testcase_text:
            missing_messages.append(message)

    return {
        "valid": len(missing_messages) == 0,
        "missing_messages": missing_messages
    }


# Nếu testcase có expected_result thì phải có verify step tương ứng
def validate_verify_steps(testcase):
    # Lấy ds expected_result
    expected_results = testcase.get(
        "expected_result",
        []
    )

    # # Lấy ds step
    steps = testcase.get(
        "steps",
        []
    )

    verify_steps = []

    # Duyệt các step, nếu step có chứa một trong các từ dưới thì coi là verify step
    for step in steps:
        text = normalize_text(step)

        if (
                "kiem tra" in text
                or "thong bao" in text
                or "hien thi" in text
        ):
            verify_steps.append(step)

    return {
        # Kiểm tra số lượng verify step có lớn hơn hoặc bằng số lượng expected result không
        # Nếu có → xem là hợp lệ
        "valid": len(verify_steps) >= len(expected_results),
        "expected_result_count": len(expected_results),
        "verify_step_count": len(verify_steps)
    }


# Một negative testcase chỉ nên test 1 lỗi
def validate_single_negative_condition(testcase):
    scenario = normalize_text(
        testcase.get("scenario", "")
    )

    steps_text = normalize_text(
        " ".join(testcase.get("steps", []))
    )

    text = scenario + " " + steps_text

    # negative_groups
    negative_groups = {
        "empty": [
            "khong nhap",
            "rong",
            "de trong",
            "bo trong"
        ],
        "invalid_format": [
            "khong hop le",
            "sai dinh dang",
            "invalid"
        ],
        "invalid_char": [
            "khong phai so",
            "chi bao gom so",
            "ky tu khong phai so",
            "chua chu cai",
            "chua ky tu dac biet"
        ],
        "min_length": [
            "it hon",
            "duoi",
            "toi thieu",
            "it nhat"
        ],
        "max_length": [
            "vuot qua",
            "qua dai",
            "lon hon"
        ],
        "not_found": [
            "khong tim thay",
            "khong ton tai"
        ]
    }

    matched_groups = []

    for group_name, keywords in negative_groups.items():
        if any(keyword in text for keyword in keywords):
            matched_groups.append(group_name)

    if (
            "empty" in matched_groups
            and "invalid_char" in matched_groups
            and "tu khoa" in text
    ):
        matched_groups.remove("invalid_char")

    return {
        "valid": len(matched_groups) <= 1,
        "negative_condition_count": len(matched_groups),
        "matched_groups": matched_groups
    }


def validate_testcases(execution_paths, testcases):
    # report
    report = {
        "valid": True,
        "errors": []
    }

    # Validate count
    count_result = validate_testcase_count(
        execution_paths,
        testcases
    )

    if not count_result["valid"]:
        report["valid"] = False
        report["errors"].append({
            "type": "COUNT_MISMATCH",
            "detail": count_result
        })

    # Validate traceability
    trace_result = validate_path_traceability(
        execution_paths,
        testcases
    )

    if not trace_result["valid"]:
        report["valid"] = False
        report["errors"].append({
            "type": "PATH_TRACEABILITY_ERROR",
            "detail": trace_result
        })

    # Build path map
    path_map = {
        path.get("path_id"): path
        for path in execution_paths
    }

    # Validate từng testcase
    for tc in testcases:
        tc_id = tc.get("test_case_id", "")
        path_id = tc.get("path_id", "")

        # Validate structure
        structure_result = validate_testcase_structure(tc)

        if not structure_result["valid"]:
            report["valid"] = False
            report["errors"].append({
                "type": "INVALID_STRUCTURE",
                "testcase": tc_id,
                "detail": structure_result
            })
            continue

        path = path_map.get(path_id)

        # Validate missing action
        if path:
            missing_action_result = validate_missing_user_actions(
                path,
                tc
            )

            if not missing_action_result["valid"]:
                report["valid"] = False
                report["errors"].append({
                    "type": "MISSING_USER_ACTION",
                    "testcase": tc_id,
                    "path_id": path_id,
                    "detail": missing_action_result
                })

            # Validate message
            message_result = validate_expected_messages(
                path,
                tc
            )

            if not message_result["valid"]:
                report["valid"] = False
                report["errors"].append({
                    "type": "MESSAGE_MISMATCH",
                    "testcase": tc_id,
                    "path_id": path_id,
                    "detail": message_result
                })

        # Validate verify steps
        verify_result = validate_verify_steps(tc)

        if not verify_result["valid"]:
            report["valid"] = False
            report["errors"].append({
                "type": "MISSING_VERIFY_STEP",
                "testcase": tc_id,
                "detail": verify_result
            })

        # Validate negative isolation
        negative_result = validate_single_negative_condition(tc)

        if not negative_result["valid"]:
            report["valid"] = False
            report["errors"].append({
                "type": "MULTIPLE_NEGATIVE_CONDITIONS",
                "testcase": tc_id,
                "detail": negative_result
            })

    return report # Return validation report