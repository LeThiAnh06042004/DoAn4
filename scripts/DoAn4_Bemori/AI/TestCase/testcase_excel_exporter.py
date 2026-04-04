import os
import shutil
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from copy import copy
from unidecode import unidecode


TESTER_NAME = "Lê Thị Ánh"

# Chuẩn hóa tên sheet: bỏ dấu TV, xoá khoảng trắng
def normalize_sheet_name(name: str):
    return unidecode(name).replace(" ", "")[:31]


# Cho phép xuống dòng trong cell
def apply_wrap_text(cell):
    cell.alignment = Alignment(wrap_text=True, vertical="top")


# Set width cố định (tuân tuân thủ template chuẩn, ko lệch layout)
def auto_adjust_column_width(ws):
    column_widths = {
        "A": 12, "B": 40, "C": 30,
        "D": 45, "E": 45, "F": 25,
        "G": 12, "H": 15, "I": 25
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width


# Copy toàn bộ style từ dòng template (giữ nguyên format excel)
def copy_style(src, dest):
    dest.font = copy(src.font)
    dest.border = copy(src.border)
    dest.fill = copy(src.fill)
    dest.number_format = src.number_format
    dest.alignment = copy(src.alignment)


# Update số lượng test case
def update_case_count(ws, count):
    ws["E3"] = f"Number of cases: {count}"
    ws["F3"] = f"Number of cases: {count}"


# Ghi test case vào Excel theo format chuẩn dựa trên template có sẵn
def export_testcases_to_excel(testcases, module_name, template_path):
    # Load file & setup sheet: Mở file Excel template có sẵn
    wb = load_workbook(template_path)
    ws = wb.active

    # Đổi tên sheet theo module
    sheet_name = normalize_sheet_name(module_name)
    ws.title = sheet_name

    # Ghi: Tên module, Tên tester
    ws["B2"] = sheet_name
    ws["B3"] = TESTER_NAME

    # Xác định vị trí ghi data
    start_row = 5
    template_row = 5
    total_cases = len(testcases)

    # XOÁ DÒNG THỪA
    last_needed_row = start_row + total_cases - 1

    # Nếu file đang có nhiều dòng hơn cần thiết → xoá bớt
    if ws.max_row > last_needed_row:
        ws.delete_rows(last_needed_row + 1, ws.max_row - last_needed_row)

    # THÊM DÒNG THIẾU
    needed_last_row = start_row + total_cases - 1

    # Nếu chưa đủ dòng → thêm
    if ws.max_row < needed_last_row:
        for _ in range(needed_last_row - ws.max_row):
            ws.append([""] * 9) # Thêm 1 dòng trống (9 cột)

            new_row = ws.max_row
            for col in range(1, 10):
                # Copy style từ dòng template
                copy_style(
                    ws.cell(row=template_row, column=col),
                    ws.cell(row=new_row, column=col)
                )

    # Ghi dữ liệu test case
    test_date = datetime.today().strftime("%d/%m/%Y") # Lấy ngày ht

    # Duyệt từng test case
    for i, tc in enumerate(testcases):
        # Xác định dòng cần ghi
        row = start_row + i

        # Ghi từng field
        ws.cell(row=row, column=1, value=tc.get("test_case_id"))
        ws.cell(row=row, column=2, value=tc.get("scenario"))
        ws.cell(row=row, column=3, value="\n".join(tc.get("precondition", [])))
        ws.cell(row=row, column=4, value="\n".join(tc.get("steps", [])))
        ws.cell(row=row, column=5, value="\n".join(tc.get("expected_result", [])))
        ws.cell(row=row, column=8, value=test_date)

        # Copy style cho từng dòng
        for col in range(1, 10):
            copy_style(
                ws.cell(row=template_row, column=col),
                ws.cell(row=row, column=col)
            )

        # Wrap text (xuống dòng)
        for col in range(1, 6):
            apply_wrap_text(ws.cell(row=row, column=col))

    update_case_count(ws, total_cases) # Update số lượng test case
    auto_adjust_column_width(ws) # Set độ rộng cột

    wb.save(template_path)
