from openpyxl import Workbook
import re


# Excel có rule thì Xoá ký tự invalid, Tên sheet tối đa 31 ký tự
def safe_sheet_name(name):
    return re.sub(r'[\\/*?:\[\]]', '', name)[:31]


# Tự động chỉnh độ rộng cột cho dễ đọc
def auto_adjust(ws):
    # duyệt từng cột
    for col in ws.columns:
        max_len = 0
        letter = col[0].column_letter # Lấy ký tự cột

        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value))) # Tìm cell dài nhất

        ws.column_dimensions[letter].width = max_len + 5 # Set width và + 5 để nhìn thoáng hơn


# export toàn bộ keyword steps ra Excel
def export_script_to_excel(keyword_steps, output_path):

    # Tạo workbook (Tạo file Excel mới) -> xoá sheet mặc định
    wb = Workbook()
    wb.remove(wb.active)

    for tc in keyword_steps:
        # Mỗi test case = 1 sheet
        ws = wb.create_sheet(title=safe_sheet_name(tc["test_case_id"]))

        #Ghi header
        ws.append(["STEP", "KEYWORD", "LOCATOR", "VALUE"])

        # Ghi từng step
        for i, step in enumerate(tc.get("steps", []), start=1):
            # Ghi dữ liệu vào Excel
            ws.append([
                i,
                step.get("keyword", ""),
                step.get("locator", ""),
                step.get("value", "")
            ])

        auto_adjust(ws) # Tự động chỉnh width

    wb.save(output_path) # Lưu file