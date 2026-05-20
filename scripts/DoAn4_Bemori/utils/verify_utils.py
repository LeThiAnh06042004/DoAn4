import re
from unidecode import unidecode

from utils.action_extractor import extract_action


def normalize_space(text):
    if text is None:
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()


def normalize_text(text):
    if text is None:
        return ""

    text = normalize_space(text).lower()
    text = unidecode(text)

    return text


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
    text = normalize_text(text)

    contains_patterns = [
        "co chua",
        "thong bao co chua",
        "noi dung co chua",
        "message contains",
        "text contains",
        "contains"
    ]

    return any(
        pattern in text
        for pattern in contains_patterns
    )


def is_generic_expected(text):
    if not text:
        return True

    text = str(text)
    text_lower = normalize_text(text)

    if extract_quoted_text(text):
        return False

    if ":" in text:
        return False

    specific_patterns = [
        " la ",
        " co chua ",
        " thong bao chua ",
        " noi dung chua ",
        " hien thi chu ",
        " hien thi noi dung "
    ]

    if any(pattern in text_lower for pattern in specific_patterns):
        return False

    generic_patterns = [
        "thong bao xuat hien",
        "thong bao hien thi",
        "hien thi thong bao",
        "xuat hien tren giao dien",
        "hien thi tren giao dien",
        "tren giao dien",
        "he thong kiem tra",
        "he thong gui",
        "khong gui don hang",
        "khong gui thong tin"
    ]

    return any(
        pattern in text_lower
        for pattern in generic_patterns
    )


def is_visible_expected(text):
    if not text:
        return False

    text_lower = normalize_text(text)

    if extract_quoted_text(text):
        return False

    message_patterns = [
        "thong bao",
        "message"
    ]

    if any(
        pattern in text_lower
        for pattern in message_patterns
    ):
        return False

    visible_patterns = [
        "danh sach",
        "ket qua",
        "san pham",
        "toan bo",
        "phu hop",
        "duoc hien thi",
        "hien thi danh sach",
        "hien thi ket qua",
        "xuat hien"
    ]

    return any(
        pattern in text_lower
        for pattern in visible_patterns
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
        r".*co chua\s+(.+)$",
        r".*thông báo chứa\s+(.+)$",
        r".*thong bao chua\s+(.+)$",
        r".*nội dung chứa\s+(.+)$",
        r".*noi dung chua\s+(.+)$",
        r".*contains\s+(.+)$",
        r".*hiển thị chữ\s+(.+)$",
        r".*hien thi chu\s+(.+)$",
        r".*hiển thị nội dung\s+(.+)$",
        r".*hien thi noi dung\s+(.+)$",
        r".*nội dung thông báo là\s+(.+)$",
        r".*noi dung thong bao la\s+(.+)$",
        r".*thông báo là\s+(.+)$",
        r".*thong bao la\s+(.+)$",
        r".*\slà\s+(.+)$",
        r".*\sla\s+(.+)$"
    ]

    text_norm = normalize_text(text)

    for pattern in patterns:
        match = re.match(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return normalize_space(match.group(1))

        match_norm = re.match(
            pattern,
            text_norm,
            flags=re.IGNORECASE
        )

        if match_norm:
            return normalize_space(match_norm.group(1))

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


def build_verify_steps_from_expected(
        expected_results,
        raw_steps=None
):
    verify_steps = []

    raw_steps = raw_steps or []

    # ==================================================
    # Detect contains từ raw step
    # ==================================================
    raw_step_text = " ".join(
        str(s)
        for s in raw_steps
    )

    use_contains_from_step = should_use_contains(
        raw_step_text
    )

    for expected in expected_results:
        raw_expected_text = str(expected).strip()

        if not raw_expected_text:
            continue

        expected_text = raw_expected_text

        # ==============================================
        # PRIORITY:
        # step context > expected text
        # ==============================================
        use_contains = (
            use_contains_from_step
            or should_use_contains(raw_expected_text)
        )

        quoted = extract_quoted_text(expected_text)

        if quoted:
            keyword = (
                "VERIFY_TEXT_CONTAINS"
                if use_contains
                else "VERIFY_ELEMENT_TEXT_EQUALS"
            )

            verify_steps.append({
                "keyword": keyword,
                "value": quoted
            })

            continue

        if ":" in expected_text:
            value = clean_expected_text(expected_text)

            if value:
                keyword = (
                    "VERIFY_TEXT_CONTAINS"
                    if use_contains
                    else "VERIFY_ELEMENT_TEXT_EQUALS"
                )

                verify_steps.append({
                    "keyword": keyword,
                    "value": value
                })

            continue

        if is_visible_expected(expected_text):
            verify_steps.append({
                "keyword": "VERIFY_ELEMENT_VISIBLE",
                "value": expected_text
            })

            continue

        value = clean_expected_text(expected_text)

        if not value:
            value = expected_text

        keyword = (
            "VERIFY_TEXT_CONTAINS"
            if use_contains
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