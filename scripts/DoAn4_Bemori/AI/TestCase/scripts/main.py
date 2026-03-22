# import os
# import json
#
# from AI.TestCase.script_generator import generate_keyword_steps
# from AI.TestCase.excel_script_exporter import export_script_to_excel
#
#
# def get_project_root():
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     return os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
#
#
# def find_data_file(data_folder, function_name):
#     possible_files = [
#         f"data_{function_name}.txt",
#         f"data_{function_name}.csv",
#         f"data_{function_name}.json",
#         f"data_{function_name}.xlsx",
#         f"data_{function_name}.xls",
#         f"data_{function_name}.yaml",
#         f"data_{function_name}.yml",
#         f"data_{function_name}.sqlite"
#     ]
#
#     for file_name in possible_files:
#         full_path = os.path.join(data_folder, file_name)
#         if os.path.exists(full_path):
#             return full_path
#
#     return None
#
#
# def main():
#     project_root = get_project_root()
#
#     # ================= FUNCTION =================
#     function_name = "TimKiem"
#
#     # ================= TESTCASE =================
#     tc_path = os.path.join(
#         project_root,
#         "AI", "TestCase", "TC",
#         function_name,
#         f"TC_{function_name}.json"
#     )
#
#     if not os.path.exists(tc_path):
#         raise FileNotFoundError(f"Không tìm thấy Test case: {tc_path}")
#
#     print(f"Test case: {tc_path}")
#
#     with open(tc_path, "r", encoding="utf-8") as f:
#         testcases = json.load(f)
#
#     # ================= LOCATOR =================
#     locator_path = os.path.join(
#         project_root,
#         "locators",
#         f"{function_name}_locators.yaml"
#     )
#
#     if not os.path.exists(locator_path):
#         raise FileNotFoundError(f"Không tìm thấy locator: {locator_path}")
#
#     print(f"Locator: {locator_path}")
#
#     # ================= DATA =================
#     data_folder = os.path.join(project_root, "data")
#     data_path = find_data_file(data_folder, function_name)
#
#     if data_path:
#         print(f"Data: {data_path}")
#     else:
#         print("Không có data (chỉ chạy logic test)")
#
#     # ================= AI CONVERT =================
#     keyword_steps = generate_keyword_steps(testcases, locator_path)
#
#     # ================= OUTPUT =================
#     output_excel = os.path.join(
#         project_root,
#         "AI", "TestCase", "scripts",
#         "SCR",
#         f"SCR_{function_name}.xlsx"
#     )
#
#     os.makedirs(os.path.dirname(output_excel), exist_ok=True)
#
#     export_script_to_excel(keyword_steps, output_excel)
#
#     print(f"Script Excel đã tạo: {output_excel}")
#
#
# if __name__ == "__main__":
#     main()