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

    # Nhóm động từ điều hướng
    navigation_patterns = [
        "truy cập",
        "điều hướng",
        "chuyển tới",
        "đi đến",
        "đi tới",
        "mở",
        "vào"
    ]

    # Nhóm đối tượng UI
    target_patterns = [
        "trang",
        "màn hình",
        "chức năng",
        "chi tiết",
        "sản phẩm",
        "bài viết",
        "form"
    ]

    # Logic detect navigation click: Phải có động từ điều hướng vÀ đối tượng UI
    # VD: "Nhập sản phẩm". Có: sản phẩm, Ko có: nhập -> False
    return (
        any(pattern in text for pattern in navigation_patterns)
        and any(pattern in text for pattern in target_patterns)
    )


# Nhận 1 step -> 1 keyword phù hợp nhất
def extract_action(step_text):

    # Normalize trước giúp matching ổn định hơn
    text = normalize_text(step_text)

    # ==================================================
    # ƯU TIÊN INPUT_TEXT
    # VD: "Nhập nd bình luận" d bị map thành verify/content do chưa "nd"
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
    # match
    if any(pattern in text for pattern in input_patterns):
        return "INPUT_TEXT"

    # ==================================================
    # ƯU TIÊN CLICK / ĐIỀU HƯỚNG UI
    # VD: Nếu ko có "chọn sp" or "vào trang" dễ bị map thành SELECT_BY_TEXT.
    # ==================================================
    if is_navigation_click(text): # các step điều hướng UI → map thành CLICK.
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
    # CÁC KEYWORD CÒN LẠI: dùng score matching như cũ
    # ==================================================
    best_keyword = None
    best_score = 0

    # Duyệt ACTION_PATTERNS
    for keyword, patterns in ACTION_PATTERNS.items():

        score = 0

        # pattern dài hơn → specificity cao hơn → score cao hơn
        for pattern in patterns:
            if pattern in text:
                score += len(pattern)

        # Chọn keyword có score cao nhất
        if score > best_score:
            best_score = score
            best_keyword = keyword

    return best_keyword