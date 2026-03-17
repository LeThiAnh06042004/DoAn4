#Kiểm tra danh sách keyword do AI sinh ra, loại bỏ keyword trùng lặp và trả về danh sách keyword hợp lệ.

def validate_keywords(keyword_list: list):
    #Docstring của hàm, hệ thống AI có thể sinh keyword ở nhiều format khác nhau.
    """
    Validate danh sách keyword, hỗ trợ cả:
    - list[str] (ví dụ: ["OPEN_URL (Mở URL)"])
    - list[dict] (cũ: [{"method_name": "OPEN_URL", ...}])
    """

    #khởi tạo các biến
    seen = set() #lưu method_name đã gặp trước đó
    valid = [] #Danh sách keyword hợp lệ (không trùng)
    duplicates = [] #Danh sách keyword bị trùng

    #Duyệt từng keyword
    for kw in keyword_list:
        #Trường hợp keyword là string
        if isinstance(kw, str):
            # Tách method name, lấy format mới
            method_name = kw.split(" (")[0].strip() if " (" in kw else kw.strip()

        #Trường hợp keyword là dict
        elif isinstance(kw, dict):
            # Tách method name, lấy format cũ
            method_name = kw.get("method_name")
            #Kiểm tra thiếu method_name thì sẽ bỏ kw này
            if not method_name:
                print(f"WARNING: Keyword thiếu 'method_name': {kw}")
                continue

        #Trường hợp keyword sai kiểu thì bỏ qua
        else:
            print(f"WARNING: Keyword không hợp lệ: {kw}")
            continue

        #Kiểm tra keyword trùng, Keyword sẽ được đưa vào danh sách trùng
        if method_name in seen:
            duplicates.append(kw)
        else:
            seen.add(method_name) #lưu method_name vào set
            valid.append(kw) #thêm keyword vào danh sách hợp lệ

    return valid, duplicates