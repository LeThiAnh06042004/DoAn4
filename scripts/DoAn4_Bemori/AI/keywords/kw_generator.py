# #sinh file keyword tự động từ danh sách keyword (dạng JSON/dict) do AI sinh ra trước đó.
#
# import os
#
# # các template để tạo class
# CLASS_TEMPLATE = """class {class_name}:
#     \"\"\"
#     {description_en}
#     Nghĩa tiếng Việt: {description_vi}
#     \"\"\"
# {methods}
# """
#
# # các template để tạo method
# METHOD_TEMPLATE = """
#     def {method_name}(self{arguments_signature}):
#         \"\"\"
#         {display_name_vi}
#         \"\"\"
#         pass
# """
#
# #Hàm Nhận danh sách keyword và Sinh file Python keyword
# def generate_keyword_file(keyword_list, output_dir):
#     #Kiểm tra danh sách keyword
#     if not keyword_list: # nếu ds rỗng thì ko lmj
#         return
#
#     class_name = keyword_list[0]["class_name"] #Lấy tên class từ keyword đầu tiên
#
#     # Khởi tạo biến chứa các method, Biến này sẽ nối tất cả method lại thành một chuỗi.
#     methods_str = ""
#
#     #duyệt từng kw
#     for kw in keyword_list:
#         arguments_signature = "" #Tạo chữ ký tham số
#
#         #Kiểm tra arguments
#         if kw["arguments"]:
#             arguments_signature = ", " + ", ".join(kw["arguments"]) #Ghép danh sách tham số
#
#         #sinh method từ template: Thay giá trị vào template đã gọi ở trên
#         methods_str += METHOD_TEMPLATE.format(
#             method_name=kw["method_name"],
#             arguments_signature=arguments_signature,
#             display_name_vi=kw["display_name_vi"]
#         )
#
#     #Sinh nội dung class: Thay các giá trị vào template class.
#     content = CLASS_TEMPLATE.format(
#         class_name=class_name,
#         description_en=keyword_list[0]["description_en"],
#         description_vi=keyword_list[0]["description_vi"],
#         methods=methods_str
#     )
#
#     #Tạo thư mục output nếu chưa tồn tại
#     os.makedirs(output_dir, exist_ok=True)
#
#     #Tạo đường dẫn file
#     file_path = os.path.join(output_dir, f"{class_name}.py")
#
#     #ghi file: Mở file ở chế độ write, Sau đó ghi toàn bộ nội dung class vào file.
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(content)
#
#     print(f"[CREATED] {file_path}")