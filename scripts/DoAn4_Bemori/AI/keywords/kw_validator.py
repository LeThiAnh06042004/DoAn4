def validate_keywords(keyword_list: list):
    """
    Validate danh sách keyword, hỗ trợ cả:
    - list[str] (ví dụ: ["OPEN_URL (Mở URL)"])
    - list[dict] (cũ: [{"method_name": "OPEN_URL", ...}])
    """
    seen = set()
    valid = []
    duplicates = []

    for kw in keyword_list:
        if isinstance(kw, str):
            # Format mới: string "METHOD_NAME (nghĩa)"
            method_name = kw.split(" (")[0].strip() if " (" in kw else kw.strip()
        elif isinstance(kw, dict):
            # Format cũ: dict
            method_name = kw.get("method_name")
            if not method_name:
                print(f"WARNING: Keyword thiếu 'method_name': {kw}")
                continue
        else:
            print(f"WARNING: Keyword không hợp lệ: {kw}")
            continue

        if method_name in seen:
            duplicates.append(kw)
        else:
            seen.add(method_name)
            valid.append(kw)

    return valid, duplicates