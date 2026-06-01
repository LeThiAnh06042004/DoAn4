import os
import re


# tìm file log tương ứng với chức năng và website
def find_log_file_by_function_web(
        reports_dir,
        function_name,
        web_name
):
    # Kiểm tra thư mục reports có tồn tại không
    if not os.path.exists(reports_dir):
        return None

    # Tạo tên file log cần tìm
    target_file = f"log_{function_name}_{web_name}.txt"

    # Tạo danh sách lưu các file log tìm được
    matched_logs = []

    # Duyệt toàn bộ thư mục reports
    for root, dirs, files in os.walk(reports_dir):
        # Tìm file đúng tên
        for file in files:
            if file == target_file:
                # lưu đường dẫn đầy đủ
                matched_logs.append(
                    os.path.join(root, file)
                )

    # Nếu không tìm thấy log
    if not matched_logs:
        return None

    # Sắp xếp theo thời gian sửa đổi mới nhất
    matched_logs.sort(
        key=lambda p: os.path.getmtime(p),
        reverse=True
    )

    # Trả về file mới nhất (lấy log lần chạy gần nhất)
    return matched_logs[0]


# đọc file log và trích xuất kết quả test case
def parse_execution_log(log_file):
    # Kiểm tra file log: Nếu không có file log thì trả về danh sách rỗng
    if not log_file or not os.path.exists(log_file):
        return []

    # Đọc nội dung file log
    with open(
            log_file,
            "r",
            encoding="utf-8"
    ) as f:
        content = f.read()

    # Dictionary lưu trạng thái testcase
    testcase_status = {}

    # Tìm testcase PASS
    passed_cases = re.findall(
        r"TESTCASE PASSED:\s*(TC_\d+)",
        content
    )

    # Tìm testcase FAIL
    failed_cases = re.findall(
        r"TESTCASE FAILED:\s*(TC_\d+)",
        content
    )

    # Ghi testcase PASS vào dictionary
    for tc in passed_cases:
        testcase_status[tc] = {
            "test_case_id": tc,
            "status": "PASS",
            "error": ""
        }

    # Ghi testcase FAIL vào dictionary
    for tc in failed_cases:
        testcase_status[tc] = {
            "test_case_id": tc,
            "status": "FAIL",
            "error": ""
        }

    return list(testcase_status.values()) # ds kq