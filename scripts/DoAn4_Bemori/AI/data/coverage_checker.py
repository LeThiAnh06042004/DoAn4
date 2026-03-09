def check_coverage(data, rules):
    """
    Kiểm tra độ bao phủ dữ liệu kiểm thử dựa trên rules.
    - Tự động detect field từ data (không hardcode "keyword").
    - Check các loại: empty, number, special, unicode, max_length.
    """
    if not data:
        return {"empty": False, "number": False, "special": False, "unicode": False, "max_length": False}, ["all"]

    # Lấy danh sách field từ item đầu tiên (giả định tất cả item có cùng cấu trúc)
    fields = list(data[0].keys()) if data else []

    coverage = {
        "empty": False,
        "number": False,
        "special": False,
        "unicode": False,
        "max_length": False
    }

    for item in data:
        for field in fields:
            value = item.get(field, "")

            # Empty check cho bất kỳ field nào
            if value == "":
                coverage["empty"] = True

            # Number: có chứa số trong bất kỳ field nào
            if any(c.isdigit() for c in str(value)):
                coverage["number"] = True

            # Special: có ký tự đặc biệt (không chữ/số) trong bất kỳ field nào
            if any(not c.isalnum() for c in str(value)):
                coverage["special"] = True

            # Unicode: có ký tự > 127 (tiếng Việt có dấu, emoji...) trong bất kỳ field nào
            if any(ord(c) > 127 for c in str(value)):
                coverage["unicode"] = True

            # Max length: có field đạt đúng max_length
            max_len = rules.get("max_length", 255)
            if len(str(value)) == max_len:
                coverage["max_length"] = True

    missing = [k for k, v in coverage.items() if not v]
    return coverage, missing