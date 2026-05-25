# Đọc file Excel keyword-driven script → convert thành structure để framework execute

import pandas as pd


def read_excel_to_testcases(file_path):
    xls = pd.ExcelFile(file_path) # Đọc file Excel
    testcases = [] # Khởi tạo danh sách testcases

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name) # Parse sheet thành DataFrame

        steps = [] # khởi tạo step
        for _, row in df.iterrows(): # Duyệt từng dòng Excel và Build step object
            steps.append({
                "keyword": str(row["KEYWORD"]).strip(),
                "locator": "" if pd.isna(row["LOCATOR"]) else str(row["LOCATOR"]).strip(),
                "value": "" if pd.isna(row["VALUE"]) else str(row["VALUE"]).strip()
            })

        # Build testcase object
        testcases.append({
            "name": sheet_name,
            "steps": steps
        })

    return testcases