import re

from utils.action_extractor import extract_action


def normalize_space(text):
    if text is None:
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()


def extract_quoted_text(text):
    if not text:
        return ""

    text = str(text)

    patterns = [
        r'"([^"]+)"',
        r"'([^']+)'",
        r"“([^”]+)”",
        r"‘([^’]+)’"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return normalize_space(match.group(1))

    return ""


def should_use_contains(text):
    text = str(text).lower()

    contains_patterns = [
        "có chứa",
        "thông báo chứa",
        "nội dung chứa",
        "contains",
        "hiển thị chữ",
        "hiển thị nội dung"
    ]

    return any(
        pattern in text
        for pattern in contains_patterns
    )


def is_generic_expected(text):
    if not text:
        return True

    text = str(text)
    text_lower = text.lower()

    if extract_quoted_text(text):
        return False

    if ":" in text:
        return False

    specific_patterns = [
        " là ",
        " có chứa ",
        " thông báo chứa ",
        " nội dung chứa ",
        " hiển thị chữ ",
        " hiển thị nội dung "
    ]

    if any(pattern in text_lower for pattern in specific_patterns):
        return False

    generic_patterns = [
        "thông báo xuất hiện",
        "thông báo hiển thị",
        "hiển thị thông báo",
        "xuất hiện trên giao diện",
        "hiển thị trên giao diện",
        "trên giao diện",
        "hệ thống kiểm tra",
        "hệ thống gửi",
        "không gửi đơn hàng",
        "không gửi thông tin"
    ]

    return any(
        pattern in text_lower
        for pattern in generic_patterns
    )


def clean_expected_text(text):
    if not text:
        return ""

    text = normalize_space(text)

    quoted = extract_quoted_text(text)

    if quoted:
        return quoted

    if ":" in text:
        value = text.split(":", 1)[1]
        return normalize_space(value)

    patterns = [
        r".*có chứa\s+(.+)$",
        r".*thông báo chứa\s+(.+)$",
        r".*nội dung chứa\s+(.+)$",
        r".*contains\s+(.+)$",
        r".*hiển thị chữ\s+(.+)$",
        r".*hiển thị nội dung\s+(.+)$",
        r".*nội dung thông báo là\s+(.+)$",
        r".*thông báo là\s+(.+)$",
        r".*\slà\s+(.+)$"
    ]

    for pattern in patterns:
        match = re.match(pattern, text, flags=re.IGNORECASE)

        if match:
            return normalize_space(match.group(1))

    if is_generic_expected(text):
        return ""

    return normalize_space(
        text
        .strip()
        .strip(":")
        .strip('"')
        .strip("'")
        .strip("“")
        .strip("”")
    )


def get_verify_value(raw_step, expected_results):
    for expected in expected_results:
        quoted = extract_quoted_text(expected)

        if quoted:
            return quoted

    for expected in expected_results:
        if ":" in str(expected):
            value = clean_expected_text(expected)

            if value:
                return value

    for expected in expected_results:
        if is_generic_expected(expected):
            continue

        value = clean_expected_text(expected)

        if value:
            return value

    return clean_expected_text(raw_step)


def infer_verify_keyword(raw_step, expected_results):
    full_text = " ".join(
        [raw_step] + expected_results
    )

    if should_use_contains(full_text):
        return "VERIFY_TEXT_CONTAINS"

    keyword = extract_action(full_text)

    if keyword in [
        "VERIFY_ELEMENT_TEXT_EQUALS",
        "VERIFY_TEXT_CONTAINS"
    ]:
        return keyword

    return "VERIFY_ELEMENT_TEXT_EQUALS"


def build_verify_steps_from_expected(expected_results, raw_steps=None):
    verify_steps = []

    raw_steps = raw_steps or []
    context_text = " ".join(raw_steps + expected_results)

    for expected in expected_results:
        has_specific_value = (
            extract_quoted_text(expected)
            or ":" in str(expected)
        )

        if not has_specific_value:
            continue

        value = clean_expected_text(expected)

        if not value:
            continue

        keyword = (
            "VERIFY_TEXT_CONTAINS"
            if should_use_contains(context_text)
            else "VERIFY_ELEMENT_TEXT_EQUALS"
        )

        verify_steps.append({
            "keyword": keyword,
            "value": value
        })

    return verify_steps


def is_duplicate_step(existing_steps, new_step):
    for step in existing_steps:
        if (
            step.get("keyword") == new_step.get("keyword")
            and step.get("locator") == new_step.get("locator")
            and str(step.get("value", "")).strip()
            == str(new_step.get("value", "")).strip()
        ):
            return True

    return False