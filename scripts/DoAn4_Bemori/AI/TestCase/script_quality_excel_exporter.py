# from openpyxl import Workbook
# from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
# from openpyxl.utils import get_column_letter
#
#
# def set_title(ws, title, end_col):
#     ws.merge_cells(
#         start_row=1,
#         start_column=1,
#         end_row=1,
#         end_column=end_col
#     )
#
#     cell = ws.cell(row=1, column=1)
#     cell.value = title
#     cell.font = Font(
#         bold=True,
#         size=16,
#         color="FFFFFF"
#     )
#     cell.fill = PatternFill(
#         fill_type="solid",
#         fgColor="1F4E78"
#     )
#     cell.alignment = Alignment(
#         horizontal="center",
#         vertical="center"
#     )
#
#     ws.row_dimensions[1].height = 28
#
#
# def style_header(row):
#     for cell in row:
#         cell.font = Font(
#             bold=True,
#             color="FFFFFF"
#         )
#         cell.fill = PatternFill(
#             fill_type="solid",
#             fgColor="5B9BD5"
#         )
#         cell.alignment = Alignment(
#             horizontal="center",
#             vertical="center",
#             wrap_text=True
#         )
#
#
# def apply_border(ws):
#     thin = Side(
#         border_style="thin",
#         color="BFBFBF"
#     )
#
#     border = Border(
#         left=thin,
#         right=thin,
#         top=thin,
#         bottom=thin
#     )
#
#     for row in ws.iter_rows():
#         for cell in row:
#             cell.border = border
#             cell.alignment = Alignment(
#                 vertical="top",
#                 wrap_text=True
#             )
#
#
# def auto_width(ws, max_width=60):
#     for col in ws.columns:
#         col_letter = get_column_letter(col[0].column)
#         max_len = 0
#
#         for cell in col:
#             if cell.value is not None:
#                 max_len = max(
#                     max_len,
#                     len(str(cell.value))
#                 )
#
#         ws.column_dimensions[col_letter].width = min(
#             max_len + 4,
#             max_width
#         )
#
#
# def status_fill(status):
#     if status == "Đạt":
#         return PatternFill(
#             fill_type="solid",
#             fgColor="C6EFCE"
#         )
#
#     if status == "Cần xem lại":
#         return PatternFill(
#             fill_type="solid",
#             fgColor="FFEB9C"
#         )
#
#     return PatternFill(
#         fill_type="solid",
#         fgColor="FFC7CE"
#     )
#
#
# def score_fill(score):
#     try:
#         score = float(score)
#     except Exception:
#         score = 0
#
#     if score >= 90:
#         return PatternFill(
#             fill_type="solid",
#             fgColor="C6EFCE"
#         )
#
#     if score >= 80:
#         return PatternFill(
#             fill_type="solid",
#             fgColor="FFEB9C"
#         )
#
#     return PatternFill(
#         fill_type="solid",
#         fgColor="FFC7CE"
#     )
#
#
# def format_percent(cell):
#     try:
#         value = float(cell.value)
#         cell.value = value / 100
#         cell.number_format = "0.00%"
#     except Exception:
#         pass
#
#
# def create_method_sheet(wb, function_name, web_name):
#     ws = wb.active
#     ws.title = "Evaluation_Method"
#
#     set_title(
#         ws,
#         "TEST SCRIPT QUALITY EVALUATION MODEL",
#         4
#     )
#
#     ws.append([])
#     ws.append(["Function", function_name])
#     ws.append(["Website", web_name])
#     ws.append(["Evaluation Target", "Keyword-driven test scripts"])
#     ws.append(["Evaluation Method", "Weighted combination of Coverage, Completeness, Accuracy, Consistency and Execution Success Rate"])
#
#     ws.append([])
#     ws.append([
#         "Metric",
#         "Weight",
#         "Purpose",
#         "Formula"
#     ])
#
#     rows = [
#         [
#             "Coverage",
#             "20%",
#             "Đánh giá số lượng script được sinh",
#             "Generated Scripts / Total Test Cases"
#         ],
#         [
#             "Completeness",
#             "25%",
#             "Đánh giá script có đủ bước hay không",
#             "Generated Steps / Required Steps"
#         ],
#         [
#             "Accuracy",
#             "30%",
#             "Đánh giá keyword, locator, value có hợp lệ không",
#             "Valid Generated Steps / Generated Steps"
#         ],
#         [
#             "Consistency",
#             "10%",
#             "Đánh giá cùng một action có mapping nhất quán không",
#             "Consistent Mapping Groups / Repeated Mapping Groups"
#         ],
#         [
#             "Execution Success Rate",
#             "15%",
#             "Đánh giá script có khả năng thực thi hoặc chạy thành công không",
#             "Executable or Passed Scripts / Generated Scripts"
#         ]
#     ]
#
#     for row in rows:
#         ws.append(row)
#
#     style_header(ws[7])
#     apply_border(ws)
#     auto_width(ws)
#     ws.freeze_panes = "A8"
#
#     return ws
#
#
# def create_summary_sheet(wb, summary_report):
#     ws = wb.create_sheet("Evaluation_Summary")
#
#     set_title(
#         ws,
#         "EVALUATION SUMMARY",
#         7
#     )
#
#     ws.append([])
#     ws.append([
#         "Metric",
#         "Description",
#         "Formula",
#         "Weight (%)",
#         "Score (%)",
#         "Weighted Score",
#         "Note"
#     ])
#
#     for row in summary_report:
#         ws.append([
#             row.get("metric", ""),
#             row.get("description", ""),
#             row.get("formula", ""),
#             row.get("weight", 0),
#             row.get("score", 0),
#             row.get("weighted_score", 0),
#             row.get("note", "")
#         ])
#
#     style_header(ws[3])
#
#     for row in range(4, ws.max_row + 1):
#         format_percent(ws.cell(row=row, column=4))
#         format_percent(ws.cell(row=row, column=5))
#
#         score_cell = ws.cell(row=row, column=5)
#         score_cell.fill = score_fill(
#             float(score_cell.value) * 100
#         )
#
#         if ws.cell(row=row, column=1).value == "Final Score":
#             ws.cell(row=row, column=6).fill = score_fill(
#                 ws.cell(row=row, column=6).value
#             )
#             ws.cell(row=row, column=6).font = Font(bold=True)
#
#     apply_border(ws)
#     auto_width(ws)
#     ws.freeze_panes = "A4"
#
#     return ws
#
#
# def create_detail_sheet(wb, detail_report):
#     ws = wb.create_sheet("Script_Detail")
#
#     set_title(
#         ws,
#         "TEST SCRIPT DETAIL",
#         11
#     )
#
#     ws.append([])
#     headers = [
#         "Test Case ID",
#         "Path ID",
#         "Required Steps",
#         "Generated Steps",
#         "Completeness (%)",
#         "Accuracy (%)",
#         "Has Verify",
#         "Executable",
#         "Errors",
#         "Score",
#         "Status"
#     ]
#
#     ws.append(headers)
#
#     for row in detail_report:
#         ws.append([
#             row.get("test_case_id", ""),
#             row.get("path_id", ""),
#             row.get("required_steps", 0),
#             row.get("generated_steps", 0),
#             row.get("completeness", 0),
#             row.get("accuracy", 0),
#             "Yes" if row.get("has_verify") else "No",
#             "Yes" if row.get("executable") else "No",
#             "\n".join(row.get("errors", [])),
#             row.get("score", 0),
#             row.get("status", "")
#         ])
#
#     style_header(ws[3])
#
#     for row in range(4, ws.max_row + 1):
#         format_percent(ws.cell(row=row, column=5))
#         format_percent(ws.cell(row=row, column=6))
#
#         score_cell = ws.cell(row=row, column=10)
#         score_cell.fill = score_fill(score_cell.value)
#         score_cell.font = Font(bold=True)
#
#         status_cell = ws.cell(row=row, column=11)
#         status_cell.fill = status_fill(status_cell.value)
#         status_cell.font = Font(bold=True)
#
#     apply_border(ws)
#     auto_width(ws)
#     ws.freeze_panes = "A4"
#
#     return ws
#
#
# def export_script_quality_evaluation_to_excel(
#         summary_report,
#         detail_report,
#         output_path,
#         function_name="",
#         web_name=""
# ):
#     wb = Workbook()
#
#     create_method_sheet(
#         wb,
#         function_name,
#         web_name
#     )
#
#     create_summary_sheet(
#         wb,
#         summary_report
#     )
#
#     create_detail_sheet(
#         wb,
#         detail_report
#     )
#
#     wb.save(output_path)