def validate_data(data, schema):
    valid = []
    invalid = []
    for item in data:
        ok = True
        for field, rule in schema.items():
            value = item.get(field)
            if value is None:
                ok = False
                break
            if not isinstance(value, str):
                ok = False
                break
            # Chỉ check max_length nếu có key trong rule
            if "max_length" in rule and len(value) > rule["max_length"]:
                ok = False
                break
        if ok:
            valid.append(item)
        else:
            invalid.append(item)
    return valid, invalid