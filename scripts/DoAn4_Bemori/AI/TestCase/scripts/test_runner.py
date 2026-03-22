# import os
# from openpyxl import load_workbook
# from selenium import webdriver
#
# from core.kw_common import KWCommon
# from core.kw_dispatcher import KeywordDispatcher
# from utils.locator_reader import LocatorReader
# from utils.data_manager import DataManager
#
#
# def load_test_data(function_name):
#     base = f"data/data_{function_name}"
#     exts = [".txt", ".csv", ".json", ".xlsx", ".xls", ".yaml"]
#
#     for ext in exts:
#         path = base + ext
#         if os.path.exists(path):
#             print(f"[DATA] Load từ: {path}")
#             return DataManager.load_data(path)
#
#     raise Exception("Không tìm thấy file data")
#
#
# def run(function_name):
#
#     driver = webdriver.Chrome()
#     driver.get("https://gaubongonline.vn/")
#     driver.maximize_window()
#
#     locator_reader = LocatorReader(f"locators/{function_name}_locators.yaml")
#
#     kw = KWCommon(driver, locator_reader)
#     dispatcher = KeywordDispatcher(kw)
#
#     # Load data
#     data = load_test_data(function_name)
#
#     # 👉 FIX: không có folder con
#     file_path = f"AI/TestCase/scripts/SCR/SCR_{function_name}.xlsx"
#
#     wb = load_workbook(file_path)
#     ws = wb.active
#
#     for row in ws.iter_rows(min_row=2, values_only=True):
#
#         tc_id, step_no, keyword, locator, value = row
#
#         print(f"[RUN] {tc_id} - Step {step_no}")
#
#         args = []
#
#         if locator:
#             args.append(locator)
#
#         if value:
#             if value == "${data}":
#                 args.append(list(data[0].values())[0])
#             else:
#                 args.append(value)
#
#         dispatcher.execute(keyword, args)
#
#     driver.quit()