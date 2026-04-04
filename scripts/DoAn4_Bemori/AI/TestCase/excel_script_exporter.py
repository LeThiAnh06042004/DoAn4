from openpyxl import Workbook
import re


# Excel có rule thì Xoá ký tự invalid, Cắt 31 ký tự
def safe_sheet_name(name):
    return re.sub(r'[\\/*?:\[\]]', '', name)[:31]


# Tự động chỉnh độ rộng cột cho dễ đọc
def auto_adjust(ws):
    # duyệt từng cột -> tìm độ dài lớn nhất -> set width
    for col in ws.columns:
        max_len = 0
        letter = col[0].column_letter

        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))

        ws.column_dimensions[letter].width = max_len + 5


# Xuất keyword steps thành file Excel
# Mỗi test case = 1 sheet
# Mỗi step = 1 dòng
def export_script_to_excel(keyword_steps, output_path):

    # Tạo workbook -> xoá sheet mặc định
    wb = Workbook()
    wb.remove(wb.active)

    # Duyệt từng test case
    for tc in keyword_steps:
        # Tạo sheet: Mỗi test case = 1 sheet
        ws = wb.create_sheet(title=safe_sheet_name(tc["test_case_id"]))

        #Header
        ws.append(["STEP", "KEYWORD", "LOCATOR", "VALUE"])

        # Ghi steps
        for i, step in enumerate(tc.get("steps", []), start=1):
            ws.append([
                i,
                step.get("keyword", ""),
                step.get("locator", ""),
                step.get("value", "")
            ])

        auto_adjust(ws)

    wb.save(output_path)