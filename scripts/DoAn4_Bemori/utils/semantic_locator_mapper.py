from utils.semantic_utils import semantic_score


def map_locator_semantic(step_text, locators):
    """
    Map locator bằng semantic similarity
    """

    # Khởi tạo best match để tìm locator có số core cao nhất
    best_locator = None
    best_score = -1

    for loc in locators:

        # Lấy semantic mô tả locator
        semantic_list = loc.get("semantic", [])

        # semantic có thể là string hoặc list
        if isinstance(semantic_list, str):
            semantic_list = [semantic_list]

        max_semantic_score = 0

        # so sánh step với từng semantic phrase
        for semantic_text in semantic_list:
            # gọi AI similarity
            score = semantic_score(
                step_text,
                semantic_text
            )

            # giữ điểm cao nhất vì 1 locator có thể có nhiều semantic
            if score > max_semantic_score:
                max_semantic_score = score

        # ===== BONUS TYPE SCORE =====
        loc_type = loc.get("type", "").lower()

        step_lower = step_text.lower()

        bonus = 0

        # input
        if any(word in step_lower for word in [
            "nhập",
            "input",
            "enter",
            "type",
            "fill"
        ]):
            if "input" in loc_type or "textarea" in loc_type:
                bonus += 0.1

        # button
        if any(word in step_lower for word in [
            "click",
            "nhấn",
            "bấm",
            "submit"
        ]):
            if "button" in loc_type:
                bonus += 0.1

        # verify text
        if any(word in step_lower for word in [
            "thông báo",
            "message",
            "text",
            "label"
        ]):
            if "label" in loc_type:
                bonus += 0.1

        # TỔNG ĐIỂM CUỐI
        final_score = max_semantic_score + bonus

        print(
            f"[LOCATOR] {loc['name']} "
            f"| semantic={max_semantic_score:.3f} "
            f"| bonus={bonus:.3f} "
            f"| final={final_score:.3f}"
        )

        # CHỌN BEST LOCATOR
        if final_score > best_score:
            best_score = final_score
            best_locator = loc["name"]

    print(
        f"Best locator: {best_locator} "
        f"| score={best_score:.3f}"
    )

    return best_locator