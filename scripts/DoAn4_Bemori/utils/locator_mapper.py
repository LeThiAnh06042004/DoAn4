def map_locator(step_text, locators):
    step_text = step_text.lower()
    tokens = step_text.split()

    best_match = None
    best_score = -1

    for loc in locators:
        score = 0

        desc = loc.get("desc", "").lower()
        loc_type = loc.get("type", "").lower()

        # =========================================
        # 1. MATCH DESC
        # =========================================
        for token in tokens:
            if token in desc:
                score += 3

        # =========================================
        # 2. MATCH TYPE
        # =========================================
        for token in tokens:
            if token in loc_type:
                score += 1

        # =========================================
        # 3. BONUS RULE THEO NGỮ NGHĨA STEP
        # =========================================

        # ===== INPUT =====
        if any(x in step_text for x in ["nhập", "điền", "gõ"]):
            if "input" in loc_type:
                score += 4

        # ===== CLICK =====
        if any(x in step_text for x in ["click", "nhấn", "bấm"]):
            if "button" in loc_type or "link" in loc_type or "icon" in loc_type:
                score += 4

        # ===== SELECT =====
        if any(x in step_text for x in ["chọn", "select"]):
            if "dropdown" in loc_type or "combobox" in loc_type:
                score += 4

        # ===== CHECKBOX =====
        if "checkbox" in step_text or "tick" in step_text:
            if "checkbox" in loc_type:
                score += 4

        # ===== RADIO =====
        if "radio" in step_text:
            if "radio button" in loc_type:
                score += 4

        # ===== VERIFY TEXT =====
        if any(x in step_text for x in ["thông báo", "nội dung", "text"]):
            if "label" in loc_type or "text" in loc_type:
                score += 3

        # ===== VERIFY LIST / RESULT =====
        if any(x in step_text for x in ["danh sách", "list", "kết quả"]):
            if "table" in loc_type or "combobox" in loc_type:
                score += 3

        # ===== IMAGE =====
        if "ảnh" in step_text or "image" in step_text:
            if "image" in loc_type:
                score += 3

        # =========================================
        # 4. CHỌN LOCATOR TỐT NHẤT
        # =========================================
        if score > best_score:
            best_score = score
            best_match = loc["name"]

    return best_match