# Kiểm tra xem value hiện tại có thỏa condition dữ liệu hay không

# Hàm utility để tránh lỗi kiểu dữ liệu
def to_str(value):
    if value is None:
        return ""

    return str(value) # Convert mọi thứ thành string


# CORE function
def validate_data_value(value, condition):
    value = to_str(value) # tránh lỗi None, tránh lỗi int/float
    condition_type = condition.get("type") # Get condition type

    # Data hợp lệ: chỉ cần không rỗng.
    if condition_type == "valid":
        return value.strip() != ""

    if condition_type == "empty":
        return value.strip() == ""

    # dùng giá trị không rỗng nhưng không tồn tại trong hệ thống.
    if condition_type == "not_found":
        return value.strip() != ""

    # vẫn có dữ liệu nhưng sai format.
    if condition_type == "invalid":
        return value.strip() != ""

    # Value không rỗng và KHÔNG phải toàn số.
    if condition_type == "invalid_char":
        return value.strip() != "" and not value.isdigit()

    if condition_type == "min_length":
        min_len = condition.get("value", 0) # Get min len
        return value.strip() != "" and len(value.strip()) < min_len # Validation

    if condition_type == "max_length":
        max_len = condition.get("value", 0)
        return value.strip() != "" and len(value.strip()) > max_len

    return False # Nếu condition type không hỗ trợ → invalid.