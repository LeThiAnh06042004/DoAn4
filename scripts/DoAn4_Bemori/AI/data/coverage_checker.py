# #kiểm tra mức độ bao phủ (coverage) của dữ liệu kiểm thử
#
# def check_coverage(data, rules):
#     """
#     Kiểm tra độ bao phủ dữ liệu kiểm thử dựa trên rules.
#     - Tự động detect field từ data (không hardcode "keyword").
#     - Check các loại: empty, number, special, unicode, max_length.
#     """
#
#     #nếu dữ liệu trống -> all coverage đều chưa đạt
#     if not data:
#         return {"empty": False, "number": False, "special": False, "unicode": False, "max_length": False}, ["all"]
#
#     # Lấy danh sách field từ item đầu tiên (giả định tất cả item có cùng cấu trúc)
#     fields = list(data[0].keys()) if data else []
#
#     #Khởi tạo biến coverage
#     #sau khi quét data, nếu phát hiện loại nào → chuyển thành True.
#     coverage = {
#         "empty": False,
#         "number": False,
#         "special": False,
#         "unicode": False,
#         "max_length": False
#     }
#
#
#     #Duyệt từng item
#     for item in data:
#         #Duyệt từng field
#         for field in fields:
#             value = item.get(field, "") #Lấy giá trị của field. Nếu field không tồn tại → trả ""
#
#             # Kiểm tra giá trị rỗng
#             if value == "":
#                 coverage["empty"] = True
#
#             # Kiểm tra có số
#             if any(c.isdigit() for c in str(value)):
#                 coverage["number"] = True
#
#             # Kiểm tra ký tự đặc biệt
#             if any(not c.isalnum() for c in str(value)):
#                 coverage["special"] = True
#
#             # Kiểm tra Unicode
#             if any(ord(c) > 127 for c in str(value)):
#                 coverage["unicode"] = True
#
#             # Kiểm tra độ dài tối đa: lấy gt từ rules, nếu ko có thì mặc định là 255
#             max_len = rules.get("max_length", 255)
#             if len(str(value)) == max_len:
#                 coverage["max_length"] = True
#
#     #Xác định coverage còn thiếu
#     missing = [k for k, v in coverage.items() if not v]
#     return coverage, missing #trả về trạng thái coverage và danh sách loại dữ liệu còn thiếu