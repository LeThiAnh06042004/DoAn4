# dịch tên locator → loại UI component
def normalize_locator_name(name):

    name = name.lower()

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

    if name.startswith("ta") or "textarea" in name:
        return "textarea"

    return "element"