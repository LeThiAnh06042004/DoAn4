# TESTCASE_PROMPT_TEMPLATE = """
# Bạn là chuyên gia kiểm thử phần mềm.
#
# Từ các execution path dưới đây hãy sinh các test case kiểm thử.
#
# Yêu cầu:
#
# 1. Trả về kết quả dưới dạng JSON hợp lệ.
#
# 2. Mỗi test case phải có các trường sau:
#
# * test_case_id
# * scenario
# * precondition
# * steps
# * expected_result
#
# 3. Quy tắc viết test case:
#
# Scenario:
#
# * Mô tả ngắn gọn mục tiêu kiểm thử.
# * Không viết quá dài.
# * Không mô tả toàn bộ luồng hành động.
#
# Steps:
#
# * Chỉ mô tả hành động của người dùng.
# * Không mô tả xử lý nội bộ của hệ thống.
# * Không ghi giá trị dữ liệu cụ thể (ví dụ: không ghi "iphone", "123456"...).
# * Chỉ mô tả chung như "Enter valid input", "Enter invalid input", "Leave the field empty".
# * Mỗi bước phải là một hành động rõ ràng của người dùng.
#
# QUY TẮC ĐÁNH SỐ STEP:
#
# * Mỗi bước phải được đánh số theo thứ tự.
# * Định dạng bắt buộc: "Step 1: ...", "Step 2: ...", "Step 3: ..."
# * Không bỏ số thứ tự.
# * Không gộp nhiều hành động trong một step.
# * Mỗi step chỉ chứa một hành động của người dùng.
#
# Expected Result:
#
# * Chỉ mô tả kết quả có thể quan sát được từ giao diện hệ thống.
# * Không viết các câu như "Hệ thống xử lý yêu cầu".
# * Không mô tả logic nội bộ.
#
# Precondition:
#
# * Mô tả trạng thái cần thiết trước khi thực hiện test case.
# * Ví dụ: người dùng đang ở trang chức năng tương ứng.
#
# 4. Quy tắc sinh test case từ Execution Path:
#
# * Mỗi execution path phải sinh ít nhất một test case.
# * Không được tạo test case trùng lặp.
# * Nếu hai test case có steps giống nhau thì phải gộp lại thành một test case.
# * Nếu một execution path dẫn đến nhiều kết quả hiển thị, hãy gộp các kết quả đó vào expected_result của cùng một test case.
#
# 5. Mỗi bước là một hành động riêng.
#
# 6. Kết quả phải trả về JSON đúng định dạng sau:
#
# [
# {{
# "test_case_id": "TC_001",
# "scenario": "Short description of the test objective",
# "precondition": [],
# "steps": [],
# "expected_result": []
# }}
# ]
#
# Chỉ trả về JSON. Không giải thích thêm.
#
# Execution Paths:
# {execution_paths}
# """