import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from copy import copy
from unidecode import unidecode


TESTER_NAME = "Lê Thị Ánh"


def normalize_sheet_name(name: str):
    return unidecode(name).replace(" ", "")[:31]


def apply_wrap_text(cell):
    cell.alignment = Alignment(wrap_text=True, vertical="top")


def auto_adjust_column_width(ws):
    column_widths = {
        "A": 12, "B": 40, "C": 30,
        "D": 45, "E": 45, "F": 25,
        "G": 12, "H": 15, "I": 25
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width


def copy_style(src, dest):
    dest.font = copy(src.font)
    dest.border = copy(src.border)
    dest.fill = copy(src.fill)
    dest.number_format = src.number_format
    dest.alignment = copy(src.alignment)


# 🔥 CLEAR DATA – KHÔNG PHÁ FORMAT
def clear_old_data(ws, start_row=5):
    for row in range(start_row, ws.max_row + 1):
        for col in range(1, 10):
            ws.cell(row=row, column=col).value = None


def update_case_count(ws, count):
    ws["E3"] = f"Number of cases: {count}"
    ws["F3"] = f"Number of cases: {count}"


def export_testcases_to_excel(testcases, module_name, template_path):

    wb = load_workbook(template_path)

    sheet_name = normalize_sheet_name(module_name)

    if sheet_name not in wb.sheetnames:
        ws = wb.create_sheet(sheet_name)
    else:
        ws = wb[sheet_name]

    ws["B2"] = sheet_name
    ws["B3"] = TESTER_NAME

    start_row = 5
    template_row = 5

    clear_old_data(ws, start_row)

    test_date = datetime.today().strftime("%d/%m/%Y")

    for i, tc in enumerate(testcases):

        row = start_row + i

        ws.cell(row=row, column=1, value=tc.get("test_case_id"))
        ws.cell(row=row, column=2, value=tc.get("scenario"))
        ws.cell(row=row, column=3, value="\n".join(tc.get("precondition", [])))
        ws.cell(row=row, column=4, value="\n".join(tc.get("steps", [])))
        ws.cell(row=row, column=5, value="\n".join(tc.get("expected_result", [])))
        ws.cell(row=row, column=8, value=test_date)

        # copy style chuẩn
        for col in range(1, 10):
            copy_style(
                ws.cell(row=template_row, column=col),
                ws.cell(row=row, column=col)
            )

        for col in range(1, 6):
            apply_wrap_text(ws.cell(row=row, column=col))

    update_case_count(ws, len(testcases))
    auto_adjust_column_width(ws)

    wb.save(template_path)