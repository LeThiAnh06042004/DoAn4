# import os
# import re
# from AI.data.ai_generator import generate_ai_data, write_files
# from AI.data.data_validator import validate_data
# from AI.data.coverage_checker import check_coverage
# from AI.data.ai_prompt_template import BASE_PROMPT_TEMPLATE
#
#
# #tìm tên thư mục output trong prompt
# def extract_folder(prompt):
#     match = re.search(r"Tên folder:\s*(\w+)", prompt)
#     if not match:
#         raise ValueError("Prompt thiếu: Tên folder")
#     return match.group(1)
#
#
# #lấy danh sách định dạng file cần sinh
# def extract_formats(prompt):
#     match = re.search(r"Sinh các file dữ liệu:\s*([^\n]+)", prompt)
#     if not match:
#         raise ValueError("Prompt thiếu: Sinh các file dữ liệu")
#     return [f.strip() for f in match.group(1).split(",")]
#
#
# #Tự động đọc prompt của người dùng để tạo schema dữ liệu
# def extract_schema_from_prompt(prompt: str):
#     """ Trích xuất schema từ phần 'Cấu trúc mỗi item' trong prompt """
#     schema = {} #Khởi tạo schema rỗng
#     lines = prompt.splitlines() #Tách prompt thành từng dòng
#     in_structure = False #Biến xác định đang ở phần structure
#
#
#     for line in lines:
#         line = line.strip() #Xóa khoảng trắng
#
#         #Phát hiện bắt đầu phần structure
#         if "Cấu trúc mỗi item" in line or "Cấu trúc dữ liệu" in line:
#             in_structure = True #bật chế độ đọc schema
#             continue #bỏ qua dòng này
#
#         #Đọc các field
#         # đang ở phần cấu trúc, dòng bắt đầu bằng -
#         if in_structure and line.startswith("- "):
#             # Match cả có ngoặc và không ngoặc
#             # Ví dụ: - noi_dung (nội dung bình luận): string
#             # hoặc - keyword: string
#             match = re.match(r'-\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(\w+)?', line)
#
#             if match:
#                 field = match.group(1) #Lấy tên field
#                 field_type = match.group(3) or "string" #Lấy kiểu dữ liệu, nếu ko có thì mặc định là string
#                 schema[field] = {"type": field_type} #Thêm vào schema
#
#         #Phát hiện kết thúc phần cấu trúc
#         if in_structure and not line.startswith("- ") and line:
#             in_structure = False
#
#     # Tìm max_length trong prompt
#     max_matches = re.findall(r'tối đa\s*(\d+)\s*ký tự', prompt, re.IGNORECASE)
#     if max_matches:
#         max_len = int(max_matches[0])
#         #Gán max_length cho tất cả field
#         for field in schema:
#             schema[field]["max_length"] = max_len
#
#     # Fallback nếu không extract được
#     if not schema:
#         schema = {"keyword": {"type": "string", "max_length": 255}}
#
#     return schema
#
#
# #Tự động xác định loại test case cần cover
# def extract_coverage_rules_from_prompt(prompt: str):
#     """ Tự động trích xuất các loại coverage cần check từ prompt """
#
#     #khai báo
#     coverage = {
#         "empty": False,
#         "number": False,
#         "special": False,
#         "unicode": False,
#         "max_length": 255
#     }
#
#     #Chuyển prompt thành chữ thường
#     lower_prompt = prompt.lower()
#
#     #Phát hiện trường hợp trống
#     if "rỗng" in lower_prompt or "trống" in lower_prompt:
#         coverage["empty"] = True
#
#     #Phát hiện trường hợp số
#     if "số" in lower_prompt or "chữ số" in lower_prompt or "digit" in lower_prompt:
#         coverage["number"] = True
#
#     #Phát hiện trường hợp ký tự đặc biệt
#     if "ký tự đặc biệt" in lower_prompt or "special" in lower_prompt or "!@#" in lower_prompt:
#         coverage["special"] = True
#
#     #Phát hiện trường hợp unicode
#     if "tiếng việt" in lower_prompt or "có dấu" in lower_prompt or "unicode" in lower_prompt:
#         coverage["unicode"] = True
#
#     #Phát hiện max_length
#     max_match = re.search(r'tối đa\s*(\d+)\s*ký tự', lower_prompt)
#     if max_match:
#         coverage["max_length"] = int(max_match.group(1))
#
#     return coverage
#
#
# #ghép prompt người dùng vào template chuẩn cho AI
# def build_prompt(user_prompt):
#     """ Ghép prompt user vào template chuẩn """
#     return BASE_PROMPT_TEMPLATE.format(USER_PROMPT=user_prompt.strip())
#
#
#
# def run_prompt(user_prompt):
#     #Lấy Tên folder và định dạng file
#     folder = extract_folder(user_prompt)
#     formats = extract_formats(user_prompt)
#
#     # Tự động lấy schema và coverage từ prompt
#     schema = extract_schema_from_prompt(user_prompt)
#     coverage_rules = extract_coverage_rules_from_prompt(user_prompt)
#
#     print("DEBUG - Schema tự động:", schema)
#     print("DEBUG - Coverage rules tự động:", coverage_rules)
#
#     # đường dẫn root project
#     base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
#     output_dir = os.path.join(base_dir, "data", folder)
#     os.makedirs(output_dir, exist_ok=True)
#
#     all_data = []
#     prompt = build_prompt(user_prompt) #Tạo prompt chuẩn cho AI.
#
#     #Loop sinh dữ liệu và chạy tối đa 5 vòng
#     for round_i in range(5):
#         print(f"\nROUND {round_i+1}")
#         data = generate_ai_data(prompt) #gọi AI sinh test data.
#         all_data.extend(data)
#
#         #Kiểm tra: field tồn tại, kiểu dữ liệu, max_length
#         valid, invalid = validate_data(all_data, schema)
#         print("VALID:", len(valid))
#         print("INVALID:", len(invalid))
#
#         #Check coverage
#         coverage, missing = check_coverage(valid, coverage_rules)
#         print("COVERAGE:", coverage)
#
#         #Nếu đạt yêu cầu thì ghi file
#         if not missing and len(invalid) == 0:
#             write_files(valid, folder, formats)
#             print("\nDONE - Coverage OK")
#             return
#
#         #Nếu thiếu coverage: Prompt được update (Bổ sung dữ liệu còn thiếu coverage: special, unicode), AI sẽ sinh tiếp
#         if missing:
#             print("MISSING COVERAGE:", missing)
#             user_prompt += f"\nBổ sung dữ liệu còn thiếu coverage: {missing}"
#             prompt = build_prompt(user_prompt)
#
#     #ghi file
#     write_files(valid, folder, formats)
#     print("\nSTOP - đạt giới hạn vòng lặp")