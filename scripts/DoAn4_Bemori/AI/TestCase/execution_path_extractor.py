#
# #→ tách Basic Flow và Alternate Flow
# #→ tạo các Execution Paths
#
# def extract_execution_paths(use_case_text: str):
#     """
#     Trích xuất execution paths từ Use Case.
#
#     - Path 1: Basic Flow
#     - Path 2..n: Basic Flow + Alternate Flow
#     """
#
#     lines = use_case_text.split("\n") #Chuyển Use Case thành list các dòng
#
#     # Khởi tạo các biến
#     basic_flow = [] #các bước luồng chính
#     alternate_flows = [] #các bước luồng thay thế
#
#     mode = None #Biến xác định đang đọc phần nào của Use Case
#
#     # Duyệt từng dòng của Use Case
#     for line in lines:
#
#         line = line.strip() #Duyệt từng dòng của Use Case
#
#         # Bỏ qua dòng rỗng
#         if not line:
#             continue
#
#         # Phát hiện Basic Flow
#         if line.lower().startswith("basic flow"):
#             mode = "basic"
#             continue
#
#         # Phát hiện Alternate Flow
#         if line.lower().startswith("alternate flow"):
#             mode = "alternate"
#             continue
#
#         # Phát hiện Post Condition
#         if line.lower().startswith("post condition"):
#             mode = None
#             continue
#
#         # Lưu Basic Flow
#         if mode == "basic":
#             basic_flow.append(line)
#
#         # Lưu Alternate Flow
#         elif mode == "alternate":
#             alternate_flows.append(line)
#
#     execution_paths = [] #Biến lưu tất cả các path thực thi
#
#     # tạo path chính
#     if basic_flow:
#         execution_paths.append(basic_flow)
#
#     # tạo path thay thế
#     for alt in alternate_flows: #Duyệt từng alternate flow.
#         path = basic_flow.copy() #Copy Basic Flow
#         path.append(alt) #Thêm bước Alternate Flow
#         execution_paths.append(path) # Thêm vào execution paths
#
#     return execution_paths # trả về execution paths
