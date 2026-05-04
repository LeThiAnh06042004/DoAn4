# hàm nhận action và intent để chọn keyword
def map_keyword(action, intent):

    # ================= INPUT =================
    if action == "input":
        if intent == "clear":
            return "CLEAR_TEXT"
        if intent == "press_enter":
            return "PRESS_ENTER"
        if intent == "send_keys":
            return "SEND_KEYS"
        return "INPUT_TEXT"

    # ================= CLICK =================
    if action == "click":
        if intent == "double_click":
            return "DOUBLE_CLICK"
        if intent == "right_click":
            return "RIGHT_CLICK"
        if intent == "click_js":
            return "CLICK_JS"
        return "CLICK"

    # ================= SELECT =================
    if action == "select":
        if intent == "select_value":
            return "SELECT_BY_VALUE"
        if intent == "select_index":
            return "SELECT_BY_INDEX"
        return "SELECT_BY_TEXT"

    # ================= VERIFY =================
    if action == "verify":
        if intent == "present":
            return "VERIFY_ELEMENT_PRESENT"
        if intent == "not_present":
            return "VERIFY_ELEMENT_NOT_PRESENT"
        if intent == "count":
            return "VERIFY_ELEMENT_COUNT"
        if intent == "selected":
            return "VERIFY_ELEMENT_SELECTED"
        if intent == "attribute":
            return "VERIFY_ATTRIBUTE"
        if intent == "alert":
            return "VERIFY_ALERT_PRESENT"
        return "VERIFY_ELEMENT_VISIBLE"

    if action == "verify_text":
        if intent == "contains":
            return "VERIFY_TEXT_CONTAINS"
        return "VERIFY_ELEMENT_TEXT_EQUALS"

    # ================= NAVIGATION =================
    if action == "navigate":
        return "OPEN_URL"

    # ================= DRAG DROP =================
    if action == "drag_drop":
        return "DRAG_AND_DROP"

    # ================= SCROLL =================
    if action == "scroll":
        if intent == "top":
            return "SCROLL_TO_TOP"
        if intent == "bottom":
            return "SCROLL_TO_BOTTOM"
        return "SCROLL_TO_ELEMENT"

    # ================= HOVER =================
    if action == "hover":
        return "HOVER"

    # ================= UPLOAD =================
    if action == "upload":
        return "UPLOAD_FILE"

    # ================= WAIT =================
    if action == "wait":
        if intent == "clickable":
            return "WAIT_FOR_ELEMENT_CLICKABLE"
        if intent == "page_load":
            return "WAIT_FOR_PAGE_LOAD"
        return "WAIT_FOR_ELEMENT_VISIBLE"

    # ================= LOG =================
    if action == "log":
        return "LOG_INFO"

    return None