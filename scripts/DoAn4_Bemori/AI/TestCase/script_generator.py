import yaml

from utils.config_loader import load_config
from utils.action_extractor import extract_action
from utils.semantic_locator_mapper import map_locator_semantic

from utils.data_binding_utils import (
    build_locator_context,
    load_test_data,
    get_locator_obj,
    infer_condition_for_input,
    find_matching_data_row,
    get_value_from_row,
    ensure_list,
    normalize_key
)

from utils.verify_utils import (
    build_verify_steps_from_expected,
    extract_quoted_text,
    is_duplicate_step
)


# xác định Locator nào là message locator
def is_message_locator(loc):
    # Ghép name + semantic rồi normalize.
    text = " ".join([
        loc.get("name", ""),
        " ".join(ensure_list(loc.get("semantic", [])))
    ])

    text_norm = normalize_key(text)

    # Kiểm tra nếu có keyword này → locator được xem là message locator.
    message_keywords = [
        "thongbao",
        "message",
        "success",
        "missing",
        "invalid",
        "loi",
        "thanhcong"
    ]

    return any(
        key in text_norm
        for key in message_keywords
    )


# Đây là tầng Rule-based pre-filter
# Không semantic toàn bộ locator mà lọc trước theo keyword rồi semantic sau
def filter_locators_by_keyword(keyword, locator_context):
    # Nếu kw là INPUT_TEXT thì c hỉ cho map tới input field, textarea
    if keyword == "INPUT_TEXT":
        return [
            loc for loc in locator_context
            if loc.get("type") in [
                "input field",
                "textarea"
            ]
        ]

    if keyword in [
        "CLICK",
        "DOUBLE_CLICK",
        "RIGHT_CLICK"
    ]:
        return [
            loc for loc in locator_context
            if loc.get("type") in [
                "button",
                "link",
                "image",
                "icon",
                "element"
            ]
        ]

    if keyword in [
        "VERIFY_ELEMENT_TEXT_EQUALS",
        "VERIFY_TEXT_CONTAINS"
    ]:
        message_locators = [
            loc for loc in locator_context
            if is_message_locator(loc)
        ]

        if message_locators:
            return message_locators

        return [
            loc for loc in locator_context
            if loc.get("type") == "label"
        ]

    if keyword in [
        "VERIFY_ELEMENT_VISIBLE",
        "VERIFY_ELEMENT_PRESENT"
    ]:
        return [
            loc for loc in locator_context
            if loc.get("type") in [
                "label",
                "element",
                "combobox",
                "table"
            ]
        ]

    return locator_context


# Semantic đôi khi ko đủ chính xác cho input field nên thêm rule scoring để boost độ chính xác.
def map_input_locator_by_rule(step_text, locator_context):
    text_norm = normalize_key(step_text)

    best_locator = None
    best_score = 0

    # Loại bỏ từ vô nghĩa.
    stop_words = [
        "nhap",
        "onhap",
        "vao",
        "input",
        "field",
        "textbox",
        "textarea"
    ]

    for loc in locator_context:
        if loc.get("type") not in [
            "input field",
            "textarea"
        ]:
            continue

        score = 0

        candidates = []

        # candidates
        candidates.append(loc.get("name", ""))

        candidates.extend(
            ensure_list(loc.get("semantic", []))
        )

        candidates.extend(
            ensure_list(loc.get("data_key", []))
        )

        for candidate in candidates:
            candidate_norm = normalize_key(candidate)

            if not candidate_norm:
                continue

            cleaned = candidate_norm

            for word in stop_words:
                cleaned = cleaned.replace(word, "")

            if not cleaned:
                continue

            # Nếu text match mạnh: score += len(cleaned) * 5
            if cleaned in text_norm:
                score += len(cleaned) * 5

            elif candidate_norm in text_norm:
                score += len(candidate_norm) * 4

            else:
                parts = [
                    p for p in cleaned.split()
                    if p and p not in stop_words
                ]

                for part in parts:
                    if normalize_key(part) in text_norm:
                        score += len(part)

        print(
            f"[INPUT RULE] step='{step_text}' "
            f"| locator={loc.get('name')} "
            f"| score={score}"
        )

        if score > best_score:
            best_score = score
            best_locator = loc.get("name")

    print(
        f"[INPUT RULE BEST] step='{step_text}' "
        f"=> {best_locator} | score={best_score}"
    )

    if best_score > 0:
        return best_locator

    return None


# Đây là API chính để map locator
def map_locator_by_keyword(
        step_text,
        keyword,
        locator_context
):
    # INPUT_TEXT: Ưu tiên rule-based mapping. Nếu fail thì semantic mapping
    if keyword == "INPUT_TEXT":
        rule_locator = map_input_locator_by_rule(
            step_text,
            locator_context
        )

        if rule_locator:
            return rule_locator

    # Với các kw khác thì map theo semantic
    candidates = filter_locators_by_keyword(
        keyword,
        locator_context
    )

    if not candidates:
        candidates = locator_context

    return map_locator_semantic(
        step_text,
        candidates
    )


# Tìm raw step liên quan tới expected result
# VD: Expected: "Hiển thị thông báo thành công". Raw step: Kiểm tra có chứa "thành công" -> match
def find_related_verify_raw_steps(expected, raw_steps):
    expected_norm = normalize_key(expected)
    quoted = extract_quoted_text(expected)
    quoted_norm = normalize_key(quoted)

    related_steps = []

    for step in raw_steps:
        step_norm = normalize_key(step)

        if (
                "kiemtra" not in step_norm
                and "thongbao" not in step_norm
                and "hienthi" not in step_norm
                and "cochua" not in step_norm
                and "contains" not in step_norm
        ):
            continue

        if quoted_norm and quoted_norm in step_norm:
            related_steps.append(step)
            continue

        if expected_norm and expected_norm in step_norm:
            related_steps.append(step)
            continue

        if "cochua" in step_norm or "contains" in step_norm:
            related_steps.append(step)
            continue

    return related_steps


# AUTO GENERATE VERIFY STEP
def build_expected_verify_steps(
        expected_results,
        raw_steps,
        locator_context
):
    verify_steps = [] # Tạo ds rỗng để lưu các bước verify sau khi sinh ra

    # Duyệt từng expected result vì một tc có thể có nhiều expected result
    for expected in expected_results:
        # Tìm raw step liên quan đến expected để lấy lm ngữ cảnh
        related_raw_steps = find_related_verify_raw_steps(
            expected,
            raw_steps
        )

        # Sinh thông tin verify
        # phân tích expected result để xác định keyword verify nào, value cần verify là gì
        verify_infos = build_verify_steps_from_expected(
            [expected],
            related_raw_steps
        )

        # Duyệt từng verify info. Mỗi info là một bước verify đã được phân tích sơ bộ
        for info in verify_infos:
            # Lấy keyword và value
            keyword = info.get("keyword")
            value = info.get("value", "")

            # Trường hợp verify text
            if keyword in [
                "VERIFY_ELEMENT_TEXT_EQUALS",
                "VERIFY_TEXT_CONTAINS"
            ]:
                # Nếu không có value thì bỏ qua
                if not value:
                    continue

                # Tạo locator_text
                # thêm chữ “thông báo” là để semantic locator mapping dễ tìm đến locator message hơn
                locator_text = f"thông báo {value}"

                # Map locator
                locator = map_locator_by_keyword(
                    locator_text,
                    keyword,
                    locator_context
                )

                # Thêm verify step
                verify_steps.append({
                    "keyword": keyword,
                    "locator": locator,
                    "value": value
                })

            # Trường hợp verify visible / present
            elif keyword in [
                "VERIFY_ELEMENT_VISIBLE",
                "VERIFY_ELEMENT_PRESENT"
            ]:
                # Map locator theo value
                locator = map_locator_by_keyword(
                    value,
                    keyword,
                    locator_context
                )

                # Thêm verify step. Kiểm tra tồn tại nên ko cần value
                verify_steps.append({
                    "keyword": keyword,
                    "locator": locator,
                    "value": ""
                })

    return verify_steps


# Tự động thêm OPEN_URL và CLOSE_BROWSER
def inject_setup_teardown(result):
    config = load_config()
    base_url = config.get("base_url", "")

    for tc in result:
        steps = tc.get("steps", [])

        keywords = [
            s.get("keyword", "")
            for s in steps
        ]

        # Nếu chưa có OPEN_URL
        if "OPEN_URL" not in keywords:
            steps.insert(0, {
                "keyword": "OPEN_URL",
                "locator": "",
                "value": base_url
            })

        # Nếu chưa có CLOSE_BROWSER
        if "CLOSE_BROWSER" not in keywords:
            steps.append({
                "keyword": "CLOSE_BROWSER",
                "locator": "",
                "value": ""
            })

    return result


def generate_keyword_steps(
        testcases,
        locator_path,
        data_path,
        execution_paths=None
):
    # Load locator YAML
    with open(locator_path, "r", encoding="utf-8") as f:
        locators = yaml.safe_load(f)

    # Convert YAML thành searchable database
    locator_context = build_locator_context(
        locators
    )

    # Load data rows
    data_rows = load_test_data(
        data_path
    )

    if isinstance(data_rows, dict):
        data_rows = [data_rows]

    execution_paths = execution_paths or []

    # hỗ trợ verify mapping
    path_step_map = {
        path.get("path_id"): path.get("steps", [])
        for path in execution_paths
    }

    result = []

    # Xử lý từng testcase
    for tc in testcases:
        raw_steps = tc.get("steps", [])
        expected_results = tc.get("expected_result", [])

        source_steps = path_step_map.get(
            tc.get("path_id", ""),
            []
        )

        verify_context_steps = source_steps + raw_steps

        temp_steps = []
        input_infos = []

        for raw_step in raw_steps:
            # Extract keyword. VD. "Người dùng nhập email" -> INPUT_TEXT
            keyword = extract_action(raw_step)

            if not keyword:
                continue

            # Vì verify sẽ được generate riêng từ expected result nên Skip verify keyword
            if keyword in [
                "VERIFY_ELEMENT_TEXT_EQUALS",
                "VERIFY_TEXT_CONTAINS",
                "VERIFY_ELEMENT_VISIBLE",
                "VERIFY_ELEMENT_PRESENT"
            ]:
                continue

            locator_text = raw_step

            # quoted_field. VD: Nhập "email" -> Lấy "email"
            quoted_field = extract_quoted_text(raw_step)

            if keyword == "INPUT_TEXT" and quoted_field:
                locator_text = f"{raw_step} {quoted_field} {quoted_field}"

            # Map locator
            locator = map_locator_by_keyword(
                locator_text,
                keyword,
                locator_context
            )

            locator_obj = get_locator_obj(
                locator,
                locator_context
            )

            # infer_condition_for_input(). VD: "Ko nhập email" -> empty
            condition = infer_condition_for_input(
                raw_step=raw_step,
                tc=tc,
                locator_obj=locator_obj
            )

            # Lưu thông tin trung gian
            temp_steps.append({
                "keyword": keyword,
                "locator": locator,
                "locator_obj": locator_obj,
                "condition": condition,
                "raw_step": raw_step
            })

            # Chỉ lưu INPUT_TEXT để tìm data row phù hợp
            if keyword == "INPUT_TEXT":
                input_infos.append({
                    "locator": locator,
                    "locator_obj": locator_obj,
                    "condition": condition,
                    "raw_step": raw_step
                })

        # tìm dòng data phù hợp với toàn bộ input conditions
        matched_row = find_matching_data_row(
            data_rows,
            input_infos
        )

        print("=== MATCHED DATA ROW ===")
        print(matched_row)

        generated_steps = []
        visible_verify_seen = set()

        for item in temp_steps:
            keyword = item["keyword"]
            locator = item["locator"]
            locator_obj = item["locator_obj"]
            condition = item["condition"]

            value = ""

            # Bind đúng value vào INPUT_TEXT
            if keyword == "INPUT_TEXT":
                value = get_value_from_row(
                    matched_row,
                    locator_obj,
                    condition
                )

            step_obj = {
                "keyword": keyword,
                "locator": locator,
                "value": value
            }

            if keyword == "VERIFY_ELEMENT_VISIBLE":
                if locator in visible_verify_seen:
                    continue

                visible_verify_seen.add(locator)

            # Chống duplicate step.
            if is_duplicate_step(
                generated_steps,
                step_obj
            ):
                continue

            generated_steps.append(step_obj)

        # Sinh verify tự động từ expected result.
        verify_steps = build_expected_verify_steps(
            expected_results,
            verify_context_steps,
            locator_context
        )

        for verify_step in verify_steps:
            if not is_duplicate_step(
                generated_steps,
                verify_step
            ):
                generated_steps.append(
                    verify_step
                )

        result.append({
            "test_case_id": tc.get("test_case_id", ""),
            "steps": generated_steps
        })

    # Tự động thêm OPEN_URL, CLOSE_BROWSER
    return inject_setup_teardown(result)