# xác định LOẠI HÀNH ĐỘNG CHÍNH
def detect_action(text: str):
    text = text.lower() # tránh lỗi hoa/thường

    # nếu có “kiểm tra” -> verify
    if any(x in text for x in ["kiểm tra", "verify"]):
        # kiểm tra nội dung → verify_text
        if any(x in text for x in ["thông báo", "text", "nội dung"]):
            return "verify_text"
        return "verify" # kiểm tra tồn tại → verify

    if any(x in text for x in ["nhập", "input", "enter dữ liệu"]):
        return "input"

    if any(x in text for x in ["click", "nhấn", "bấm"]):
        return "click"

    if any(x in text for x in ["chọn", "select"]):
        return "select"

    if any(x in text for x in ["kéo", "thả", "drag"]):
        return "drag_drop"

    if any(x in text for x in ["scroll", "cuộn"]):
        return "scroll"

    if any(x in text for x in ["hover", "di chuột"]):
        return "hover"

    if any(x in text for x in ["upload", "tải lên"]):
        return "upload"

    if any(x in text for x in ["mở", "điều hướng", "navigate"]):
        return "navigate"

    if any(x in text for x in ["chờ", "wait"]):
        return "wait"

    if any(x in text for x in ["log", "ghi log"]):
        return "log"

    return "other" # fallback nếu không detect được


# xác định CHI TIẾT HÀNH VI
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
    if "không tồn tại" in text:
        return "not_present"

    if "tồn tại" in text:
        return "present"

    if "hiển thị" in text:
        return "visible"

    if "chứa" in text:
        return "contains"

    if "bằng" in text:
        return "equals"

    if "số lượng" in text:
        return "count"

    if "được chọn" in text:
        return "selected"

    if "attribute" in text:
        return "attribute"

    if "alert" in text:
        return "alert"

    # ===== WAIT =====
    if "click được" in text:
        return "clickable"

    if "load" in text:
        return "page_load"

    # ===== SCROLL =====
    if "top" in text:
        return "top"

    if "bottom" in text:
        return "bottom"

    # ===== DEFAULT =====
    return "default"