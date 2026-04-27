def detect_action(text: str):
    text = text.lower()

    if any(x in text for x in ["nhập", "input", "enter dữ liệu"]):
        return "input"

    if any(x in text for x in ["click", "nhấn", "bấm"]):
        return "click"

    if any(x in text for x in ["chọn", "select"]):
        return "select"

    if any(x in text for x in ["kiểm tra", "verify"]):
        if any(x in text for x in ["thông báo", "text", "nội dung"]):
            return "verify_text"
        return "verify"

    if any(x in text for x in ["mở", "điều hướng", "navigate"]):
        return "navigate"

    return "other"


def detect_intent(text: str):
    text = text.lower()

    # ===== INPUT =====
    if "xóa" in text:
        return "clear"

    if "enter" in text:
        return "press_enter"

    if "phím" in text:
        return "send_keys"

    # ===== CLICK =====
    if "double" in text:
        return "double_click"

    if "chuột phải" in text:
        return "right_click"

    if "js" in text:
        return "click_js"

    # ===== SELECT =====
    if "theo text" in text:
        return "select_text"

    if "theo value" in text:
        return "select_value"

    if "theo index" in text:
        return "select_index"

    # ===== VERIFY =====
    if "hiển thị" in text:
        return "visible"

    if "tồn tại" in text:
        return "present"

    if "không tồn tại" in text:
        return "not_present"

    if "chứa" in text:
        return "contains"

    if "bằng" in text:
        return "equals"

    if "số lượng" in text:
        return "count"

    if "được chọn" in text:
        return "selected"

    if "alert" in text:
        return "alert"

    return "default"