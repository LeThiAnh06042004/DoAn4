import re


def normalize_text(text):
    if text is None:
        return ""
    return str(text).lower().strip()


def infer_condition(text):
    text = normalize_text(text)

    if any(x in text for x in [
        "không nhập",
        "rỗng",
        "để trống",
        "empty"
    ]):
        return {
            "type": "empty"
        }

    if any(x in text for x in [
        "không tồn tại",
        "không tìm thấy",
        "not found",
        "no result"
    ]):
        return {
            "type": "not_found"
        }

    min_match = re.search(
        r"(dưới|ít hơn|nhỏ hơn)\s*(\d+)",
        text
    )

    if min_match:
        return {
            "type": "min_length",
            "value": int(min_match.group(2))
        }

    max_match = re.search(
        r"(quá|vượt quá|lớn hơn|nhiều hơn)\s*(\d+)",
        text
    )

    if max_match:
        return {
            "type": "max_length",
            "value": int(max_match.group(2))
        }

    if any(x in text for x in [
        "không phải số",
        "chỉ bao gồm những số",
        "chỉ gồm số",
        "ký tự không phải số"
    ]):
        return {
            "type": "invalid_char"
        }

    if any(x in text for x in [
        "không hợp lệ",
        "sai định dạng",
        "invalid"
    ]):
        return {
            "type": "invalid"
        }

    return {
        "type": "valid"
    }