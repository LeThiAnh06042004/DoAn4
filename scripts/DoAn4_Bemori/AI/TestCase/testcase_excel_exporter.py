# File module xuất test case ra Excel

import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from unidecode import unidecode


TESTER_NAME = "Lê Thị Ánh"


#Hàm chuẩn hóa tên sheet
def normalize_sheet_name(name: str):
    """
    Chuyển tên chức năng thành dạng:
    - không dấu
    - viết liền

    Ví dụ:
    Tìm kiếm -> TimKiem
    """
    name = unidecode(name) #Chuẩn hoá tên: vd: Tìm kiếm -> Tim Kiem
    return name.replace(" ", "") #Xoá khoảng trắng


# Hàm bật wrap text: Cho phép xuống dòng trong ô Excel.
def apply_wrap_text(cell):
    """
    Bật wrap text cho ô
    """
    cell.alignment = Alignment(
        wrap_text=True, #xuống dòng trong ô
        vertical="top" #text nằm trên
    )


#Hàm Tự động chỉnh độ rộng cột
def auto_adjust_column_width(ws):
    """
    Tự động chỉnh độ rộng cột
    """

    column_widths = {
        "A": 12, # ID
        "B": 40, # Description
        "C": 30, # Precondition
        "D": 45, # Test Steps
        "E": 45, # Expected Result
        "F": 25, # Actual Output
        "G": 12, # Status
        "H": 15, # Test date
        "I": 25  # Note
    }

    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width #đặt độ rộng.


# Tạo cấu trúc sheet nếu chưa tồn tại
def create_sheet_structure(ws):
    """
    Tạo cấu trúc sheet giống template
    """

    # dòng đầu
    ws["A1"] = "Back to TestReport"
    ws["B1"] = "To Buglist"

    # thông tin module
    ws["A2"] = "Module Code"
    ws["A3"] = "Tester"

    #header của bảng TC
    headers = [
        "ID",
        "Test Case Description",
        "Pre -Condition",
        "Test Case Procedure",
        "Expected Output",
        "Actual Output",
        "Status",
        "Test date",
        "Note"
    ]

    for col, header in enumerate(headers, start=1):
        ws.cell(row=4, column=col, value=header) #tạo header ở dòng 4


# Điều chỉnh số dòng bảng, Đảm bảo số dòng trong Excel bằng số test case.
def adjust_table_rows(ws, start_row, testcase_count):
    """
    Điều chỉnh số dòng bảng
    """

    expected_last_row = start_row + testcase_count - 1
    current_last_row = ws.max_row

    # Xóa dòng thừa
    if current_last_row > expected_last_row:
        ws.delete_rows(expected_last_row + 1, current_last_row - expected_last_row)

    # Thêm dòng thiếu
    elif current_last_row < expected_last_row:
        ws.insert_rows(current_last_row + 1, expected_last_row - current_last_row)


# Cập nhật số lượng test case
def update_case_count(ws):
    """
    Cập nhật Number of cases
    """

    count = 0
    row = 5

    # Đếm số dòng có ID test case.
    while ws.cell(row=row, column=1).value:
        count += 1
        row += 1

    #sau khi đếm thì ghi vào mục Number of cases
    ws["E3"] = f"Number of cases: {count}"
    ws["F3"] = f"Number of cases: {count}"


# Hàm chính export Excel: truyền vào ds TC, tên chức năng, file Excel template
def export_testcases_to_excel(testcases, module_name, template_path):
    """
    Export test case vào Excel template
    """

    wb = load_workbook(template_path) # Mở file Excel

    sheet_name = normalize_sheet_name(module_name) # Tạo tên sheet

    # Nếu sheet chưa tồn tại -> tạo mới
    if sheet_name not in wb.sheetnames:

        ws = wb.create_sheet(sheet_name)

        create_sheet_structure(ws)

    else:
        ws = wb[sheet_name]

    # Điền header
    ws["B2"] = sheet_name
    ws["B3"] = TESTER_NAME

    start_row = 5 #xác định dòng bắt đầu

    adjust_table_rows(ws, start_row, len(testcases)) # Điều chỉnh số dòng

    # Lấy ngày hiện tại
    test_date = datetime.today().strftime("%d/%m/%Y")

    # Lặp qua danh sách test case.
    for index, tc in enumerate(testcases):

        row = start_row + index
        # Tạo ID
        test_case_id = f"TC_{index+1:03d}"

        # Lấy dữ liệu test case
        scenario = tc.get("scenario", "") # Test case description.
        precondition = "\n".join(tc.get("precondition", [])) # Test case description.
        steps = "\n".join(tc.get("steps", []))
        expected = "\n".join(tc.get("expected_result", []))

        # Ghi vào Excel
        ws.cell(row=row, column=1, value=test_case_id)
        ws.cell(row=row, column=2, value=scenario)
        ws.cell(row=row, column=3, value=precondition)
        ws.cell(row=row, column=4, value=steps)
        ws.cell(row=row, column=5, value=expected)

        # Ghi ngày test
        ws.cell(row=row, column=8, value=test_date)

        for col in range(1, 6):
            apply_wrap_text(ws.cell(row=row, column=col)) # Bật wrap text

    auto_adjust_column_width(ws) # Chỉnh độ rộng cột

    update_case_count(ws) # Cập nhật số lượng test case

    wb.save(template_path) # Lưu file Excel