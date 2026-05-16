def to_str(value):
    if value is None:
        return ""

    return str(value)


def validate_data_value(value, condition):
    value = to_str(value)
    condition_type = condition.get("type")

    if condition_type == "valid":
        return value.strip() != ""

    if condition_type == "empty":
        return value.strip() == ""

    if condition_type == "not_found":
        return value.strip() != ""

    if condition_type == "invalid":
        return value.strip() != ""

    if condition_type == "invalid_char":
        return value.strip() != "" and not value.isdigit()

    if condition_type == "min_length":
        min_len = condition.get("value", 0)
        return value.strip() != "" and len(value.strip()) < min_len

    if condition_type == "max_length":
        max_len = condition.get("value", 0)
        return value.strip() != "" and len(value.strip()) > max_len

    return False