from openpyxl import Workbook
import re


def safe_sheet_name(name):
    return re.sub(r'[\\/*?:\[\]]', '', name)[:31]


def auto_adjust(ws):
    for col in ws.columns:
        max_len = 0
        letter = col[0].column_letter

        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))

        ws.column_dimensions[letter].width = max_len + 5


def export_script_to_excel(keyword_steps, output_path):

    wb = Workbook()
    wb.remove(wb.active)

    for tc in keyword_steps:

        ws = wb.create_sheet(title=safe_sheet_name(tc["test_case_id"]))

        ws.append(["STEP", "KEYWORD", "LOCATOR", "VALUE"])

        for i, step in enumerate(tc.get("steps", []), start=1):
            ws.append([
                i,
                step.get("keyword", ""),
                step.get("locator", ""),
                step.get("value", "")
            ])

        auto_adjust(ws)

    wb.save(output_path)