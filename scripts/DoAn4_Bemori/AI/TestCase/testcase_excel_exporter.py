# File module xuất test case ra Excel

import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from unidecode import unidecode


TESTER_NAME = "Lê Thị Ánh"


# ================= NORMALIZE =================
def normalize_sheet_name(name: str):
    name = unidecode(name)
    return name.replace(" ", "")


# ================= WRAP TEXT =================
def apply_wrap_text(cell):
    cell.alignment = Alignment(
        wrap_text=True,
        vertical="top"
    )


# ================= COLUMN WIDTH =================
def auto_adjust_column_width(ws):
    column_widths = {
        "A": 12,
        "B": 40,
        "C": 30,
        "D": 45,
        "E": 45,
        "F": 25,
        "G": 12,
        "H": 15,
        "I": 25
    }

    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width


# ================= CREATE SHEET =================
def create_sheet_structure(ws):
    ws["A1"] = "Back to TestReport"
    ws["B1"] = "To Buglist"

    ws["A2"] = "Module Code"
    ws["A3"] = "Tester"

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
        ws.cell(row=4, column=col, value=header)


# ================= ROW CONTROL =================
def copy_row_style(ws, source_row, target_row):
    for col in range(1, 10):
        s = ws.cell(row=source_row, column=col)
        t = ws.cell(row=target_row, column=col)

        if s.has_style:
            t._style = s._style


def adjust_table_rows(ws, start_row, testcase_count):
    expected_last_row = start_row + testcase_count - 1
    current_last_row = ws.max_row

    if current_last_row < expected_last_row:
        ws.insert_rows(current_last_row + 1, expected_last_row - current_last_row)

        for row in range(current_last_row + 1, expected_last_row + 1):
            copy_row_style(ws, current_last_row, row)

    elif current_last_row > expected_last_row:
        ws.delete_rows(expected_last_row + 1, current_last_row - expected_last_row)


# ================= COUNT =================
def update_case_count(ws):
    count = 0
    row = 5

    while ws.cell(row=row, column=1).value:
        count += 1
        row += 1

    ws["E3"] = f"Number of cases: {count}"
    ws["F3"] = f"Number of cases: {count}"


# ================= MAIN EXPORT =================
def export_testcases_to_excel(testcases, module_name, template_path):
    wb = load_workbook(template_path)

    sheet_name = normalize_sheet_name(module_name)

    if sheet_name not in wb.sheetnames:
        ws = wb.create_sheet(sheet_name)
        create_sheet_structure(ws)
    else:
        ws = wb[sheet_name]

    # Header info
    ws["B2"] = sheet_name
    ws["B3"] = TESTER_NAME

    start_row = 5

    adjust_table_rows(ws, start_row, len(testcases))

    test_date = datetime.today().strftime("%d/%m/%Y")

    for index, tc in enumerate(testcases):
        row = start_row + index

        # ✅ ưu tiên lấy từ AI, nếu không có thì tự generate
        test_case_id = tc.get("test_case_id", f"TC_{index+1:03d}")

        # ✅ FIX CHÍNH Ở ĐÂY
        scenario = tc.get("scenario", "")
        precondition = "\n".join(tc.get("precondition", []))
        steps = "\n".join(tc.get("steps", []))
        expected = "\n".join(tc.get("expected_result", []))

        # Ghi Excel
        ws.cell(row=row, column=1, value=test_case_id)
        ws.cell(row=row, column=2, value=scenario)
        ws.cell(row=row, column=3, value=precondition)
        ws.cell(row=row, column=4, value=steps)
        ws.cell(row=row, column=5, value=expected)

        # ngày test
        ws.cell(row=row, column=8, value=test_date)

        # wrap text (giữ nguyên logic cũ của bạn)
        for col in range(1, 6):
            apply_wrap_text(ws.cell(row=row, column=col))

    auto_adjust_column_width(ws)
    update_case_count(ws)

    wb.save(template_path)

