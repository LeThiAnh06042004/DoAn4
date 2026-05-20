from utils.action_patterns import ACTION_PATTERNS


# Chuẩn hoá câu input trước khi match
def normalize_text(text):
    if text is None:
        return ""

    return str(text).lower().strip()


def is_navigation_click(text):
    """
    Nhận diện các bước điều hướng/mở trang/mở màn hình.
    Đây là thao tác click trên UI, không phải SELECT.
    """

    navigation_patterns = [
        "truy cập",
        "điều hướng",
        "chuyển tới",
        "đi đến",
        "đi tới",
        "mở",
        "vào"
    ]

    target_patterns = [
        "trang",
        "màn hình",
        "chức năng",
        "chi tiết",
        "sản phẩm",
        "bài viết",
        "form"
    ]

    return (
        any(pattern in text for pattern in navigation_patterns)
        and any(pattern in text for pattern in target_patterns)
    )


# Nhận 1 step -> 1 keyword phù hợp nhất
def extract_action(step_text):

    text = normalize_text(step_text)

    # ==================================================
    # ƯU TIÊN INPUT_TEXT
    # ==================================================
    input_patterns = [
        "không nhập",
        "nhập",
        "điền",
        "gõ",
        "type",
        "enter",
        "fill"
    ]

    if any(pattern in text for pattern in input_patterns):
        return "INPUT_TEXT"

    # ==================================================
    # ƯU TIÊN CLICK / ĐIỀU HƯỚNG UI
    # Lý do:
    # Các câu như "truy cập trang chi tiết sản phẩm",
    # "mở màn hình", "vào chức năng" là hành động click
    # trên giao diện, không phải SELECT_BY_TEXT.
    # ==================================================
    if is_navigation_click(text):
        return "CLICK"

    click_patterns = [
        "nhấn",
        "bấm",
        "click",
        "tap"
    ]

    if any(pattern in text for pattern in click_patterns):
        return "CLICK"

    # ==================================================
    # CÁC KEYWORD CÒN LẠI: dùng score như cũ
    # ==================================================
    best_keyword = None
    best_score = 0

    for keyword, patterns in ACTION_PATTERNS.items():

        score = 0

        for pattern in patterns:
            if pattern in text:
                score += len(pattern)

        if score > best_score:
            best_score = score
            best_keyword = keyword

    return best_keyword