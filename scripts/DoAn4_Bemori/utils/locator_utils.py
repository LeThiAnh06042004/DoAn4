# dịch tên locator → loại UI component
def normalize_locator_name(name):
    name = name.lower() # Chuẩn hóa về chữ thường

    # mapping theo prefix
    if name.startswith("txt"):
        return "input field"
    if name.startswith("btn"):
        return "button"
    if name.startswith("lbl"):
        return "label"
    if name.startswith("chk"):
        return "checkbox"
    if name.startswith("cbo"):
        return "combobox"
    if name.startswith("rb"):
        return "radio button"
    if name.startswith("ddl") or name.startswith("select"):
        return "dropdown"
    if name.startswith("tbl"):
        return "table"
    if name.startswith("lnk"):
        return "link"
    if name.startswith("img"):
        return "image"
    if name.startswith("icon"):
        return "icon"

    return "element" # nếu ko match th trả về element


# Biến danh sách locator → dictionary mô tả để AI hiểu UI
def build_locator_hint(locators):
    """
    locators: dict từ file YAML
    return: dict {locator_key: desc}
    """

    hint = {}

    for key, value in locators.items():

        # Ưu tiên dùng desc nếu có
        if isinstance(value, dict) and "desc" in value:
            hint[key] = value["desc"]

        # fallback nếu chưa có desc
        else:
            hint[key] = normalize_locator_name(key)

    return hint