from unidecode import unidecode

from utils.semantic_utils import semantic_score


def normalize_text(text):
    if text is None:
        return ""

    return unidecode(str(text).lower().strip())


def map_locator_semantic(step_text, locators):
    """
    Map locator bằng semantic similarity + bonus theo loại UI component.
    Không hardcode theo chức năng cụ thể.
    """

    best_locator = None
    best_score = -1

    step_norm = normalize_text(step_text)

    for loc in locators:
        semantic_list = loc.get("semantic", [])

        if isinstance(semantic_list, str):
            semantic_list = [semantic_list]

        max_semantic_score = 0

        for semantic_text in semantic_list:
            score = semantic_score(
                step_text,
                semantic_text
            )

            if score > max_semantic_score:
                max_semantic_score = score

        loc_type = normalize_text(
            loc.get("type", "")
        )

        bonus = 0

        # INPUT
        if any(word in step_norm for word in [
            "nhap",
            "dien",
            "go",
            "input",
            "enter",
            "type",
            "fill"
        ]):
            if "input" in loc_type or "textarea" in loc_type:
                bonus += 0.1

        # LINK
        if any(word in step_norm for word in [
            "link",
            "lien ket",
            "truy cap",
            "dieu huong",
            "chuyen toi",
            "chuyen den",
            "di den",
            "di toi",
            "mo",
            "vao"
        ]):
            if "link" in loc_type:
                bonus += 0.1

        # BUTTON
        if any(word in step_norm for word in [
            "nut",
            "button",
            "nhan",
            "bam",
            "click",
            "tap",
            "submit"
        ]):
            if "button" in loc_type:
                bonus += 0.1

        # MESSAGE / TEXT
        if any(word in step_norm for word in [
            "thong bao",
            "message",
            "text",
            "noi dung",
            "label"
        ]):
            if "label" in loc_type or "element" in loc_type:
                bonus += 0.1

        # VISIBLE ELEMENT
        if any(word in step_norm for word in [
            "hien thi",
            "xuat hien",
            "ton tai",
            "visible",
            "present"
        ]):
            if loc_type in [
                "label",
                "element",
                "image",
                "icon",
                "button",
                "link",
                "table",
                "combobox"
            ]:
                bonus += 0.05

        final_score = max_semantic_score + bonus

        print(
            f"[LOCATOR] {loc['name']} "
            f"| semantic={max_semantic_score:.3f} "
            f"| bonus={bonus:.3f} "
            f"| final={final_score:.3f}"
        )

        if final_score > best_score:
            best_score = final_score
            best_locator = loc["name"]

    print(
        f"Best locator: {best_locator} "
        f"| score={best_score:.3f}"
    )

    return best_locator