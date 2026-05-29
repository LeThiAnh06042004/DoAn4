import re
from unidecode import unidecode

from utils.action_patterns import ACTION_PATTERNS


# Chuẩn hoá câu input trước khi match
def normalize_text(text):
    if text is None:
        return ""

    text = str(text).lower().strip()
    text = unidecode(text)

    # Chuẩn hoá khoảng trắng
    text = re.sub(r"\s+", " ", text)

    return text


def contains_phrase(text, phrase):
    """
    Kiểm tra phrase theo ranh giới từ.
    Mục đích:
    - "nhap" phải match với "nhap email"
    - "nhap" KHÔNG được match nhầm trong "dang nhap"
    """

    if not text or not phrase:
        return False

    phrase = normalize_text(phrase)

    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"

    return re.search(pattern, text) is not None


def contains_any_phrase(text, patterns):
    return any(
        contains_phrase(text, pattern)
        for pattern in patterns
    )


def is_navigation_click(text):
    """
    Nhận diện các bước điều hướng/mở trang/mở màn hình.
    Đây là thao tác click trên UI, không phải SELECT.
    Không hardcode theo chức năng cụ thể.
    """

    navigation_patterns = [
        "truy cap",
        "dieu huong",
        "chuyen toi",
        "chuyen den",
        "di den",
        "di toi",
        "mo",
        "vao"
    ]

    target_patterns = [
        "trang",
        "man hinh",
        "chuc nang",
        "form",
        "popup",
        "modal",
        "tab",
        "menu",
        "lien ket",
        "link"
    ]

    return (
        contains_any_phrase(text, navigation_patterns)
        and contains_any_phrase(text, target_patterns)
    )


# Nhận 1 step -> 1 keyword phù hợp nhất
def extract_action(step_text):
    text = normalize_text(step_text)

    # ==================================================
    # ƯU TIÊN VERIFY
    # Lý do:
    # Step verify có thể chứa text như "đăng nhập thất bại".
    # Nếu check INPUT trước, chữ "nhập" trong "đăng nhập" dễ bị nhận nhầm.
    # ==================================================
    verify_text_patterns = [
        "kiem tra thong bao",
        "hien thi thong bao",
        "thong bao",
        "kiem tra noi dung",
        "hien thi noi dung",
        "verify text",
        "verify message",
        "exact text",
        "exact message"
    ]

    if contains_any_phrase(text, verify_text_patterns):
        return "VERIFY_ELEMENT_TEXT_EQUALS"

    verify_contains_patterns = [
        "co chua",
        "contains",
        "bao gom",
        "message contains"
    ]

    if contains_any_phrase(text, verify_contains_patterns):
        return "VERIFY_TEXT_CONTAINS"

    verify_visible_patterns = [
        "kiem tra hien thi",
        "duoc hien thi",
        "hien thi",
        "xuat hien",
        "visible"
    ]

    if contains_any_phrase(text, verify_visible_patterns):
        return "VERIFY_ELEMENT_VISIBLE"

    verify_present_patterns = [
        "kiem tra ton tai",
        "ton tai",
        "verify exists",
        "present"
    ]

    if contains_any_phrase(text, verify_present_patterns):
        return "VERIFY_ELEMENT_PRESENT"

    # ==================================================
    # ƯU TIÊN DOUBLE_CLICK
    # ==================================================
    double_click_patterns = [
        "double click",
        "nhap dup"
    ]

    if contains_any_phrase(text, double_click_patterns):
        return "DOUBLE_CLICK"

    # ==================================================
    # ƯU TIÊN RIGHT_CLICK
    # ==================================================
    right_click_patterns = [
        "right click",
        "chuot phai"
    ]

    if contains_any_phrase(text, right_click_patterns):
        return "RIGHT_CLICK"

    # ==================================================
    # ƯU TIÊN PRESS_ENTER
    # ==================================================
    press_enter_patterns = [
        "nhan enter",
        "press enter"
    ]

    if contains_any_phrase(text, press_enter_patterns):
        return "PRESS_ENTER"

    # ==================================================
    # ƯU TIÊN CLICK / ĐIỀU HƯỚNG UI
    # Lý do:
    # "Nhấn nút Đăng nhập" chứa chữ "nhập" trong "đăng nhập".
    # Nếu INPUT chạy trước CLICK sẽ bị nhận nhầm thành INPUT_TEXT.
    # ==================================================
    if is_navigation_click(text):
        return "CLICK"

    click_patterns = [
        "nhan",
        "bam",
        "click",
        "tap"
    ]

    if contains_any_phrase(text, click_patterns):
        return "CLICK"

    # ==================================================
    # ƯU TIÊN INPUT_TEXT
    # ==================================================
    input_patterns = [
        "khong nhap",
        "nhap",
        "dien",
        "go",
        "type",
        "enter",
        "fill"
    ]

    if contains_any_phrase(text, input_patterns):
        return "INPUT_TEXT"

    # ==================================================
    # CÁC KEYWORD CÒN LẠI: dùng score matching
    # Có dùng contains_phrase để tránh match nhầm substring.
    # ==================================================
    best_keyword = None
    best_score = 0

    for keyword, patterns in ACTION_PATTERNS.items():
        score = 0

        for pattern in patterns:
            pattern_norm = normalize_text(pattern)

            if contains_phrase(text, pattern_norm):
                score += len(pattern_norm)

        if score > best_score:
            best_score = score
            best_keyword = keyword

    return best_keyword