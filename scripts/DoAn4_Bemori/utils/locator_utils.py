def normalize_locator_name(name):
    name = name.lower()

    if name.startswith("txt"):
        return "input field"
    if name.startswith("btn"):
        return "button"
    if name.startswith("lbl"):
        return "label"
    if name.startswith("cb") or name.startswith("chk"):
        return "checkbox"
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

    return "element"


def build_locator_hint(locator_keys):
    """
    locator_keys: list[str]
    return: dict
    """

    hint = {}

    for key in locator_keys:
        hint[key] = normalize_locator_name(key)

    return hint