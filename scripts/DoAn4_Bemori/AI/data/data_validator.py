def validate_data(data, schema):
    #Tạo danh sách chứa kết quả
    valid = []
    invalid = []

    #Duyệt từng item trong data
    for item in data:
        ok = True #Giả định ban đầu là hợp lệ

        #Duyệt từng field trong schema
        for field, rule in schema.items():
            value = item.get(field) #Lấy giá trị của field

            #Kiểm tra field có tồn tại không. Nếu dl ko hợp lệ thì thoát khỏi vòng lặp ngay lập tức
            if value is None:
                ok = False
                break

            #Kiểm tra kiểu dữ liệu
            if not isinstance(value, str):
                ok = False
                break

            # Chỉ check max_length nếu có key trong rule
            if "max_length" in rule and len(value) > rule["max_length"]:
                ok = False
                break

        #Nếu tất cả field đều hợp lệ
        if ok:
            valid.append(item)
        else:
            invalid.append(item)
    return valid, invalid #trả về ds dl hợp về và ds dl ko hl