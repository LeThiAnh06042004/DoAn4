from utils.action_patterns import ACTION_PATTERNS


# Chuẩn hoá câu input trước khi match
def normalize_text(text):
    if text is None:
        return ""

    return str(text).lower().strip()


# Nhận 1 step -> 1 keyword phù hợp nhất
def extract_action(step_text):

    text = normalize_text(step_text)

    # ==================================================
    # ƯU TIÊN INPUT_TEXT
    # Lý do:
    # "Nhập nội dung bình luận" có chữ "nội dung"
    # nên nếu chỉ tính score, nó dễ bị nhận nhầm thành VERIFY.
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
    # ƯU TIÊN CLICK / ĐIỀU HƯỚNG
    # ==================================================
    click_patterns = [
        "điều hướng",
        "truy cập",
        "chuyển tới",
        "đi đến",
        "vào trang chi tiết",
        "mở sản phẩm",
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