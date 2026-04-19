import pandas as pd


def read_excel_to_testcases(file_path):
    xls = pd.ExcelFile(file_path)
    testcases = []

    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)

        steps = []
        for _, row in df.iterrows():
            steps.append({
                "keyword": str(row["KEYWORD"]).strip(),
                "locator": "" if pd.isna(row["LOCATOR"]) else str(row["LOCATOR"]).strip(),
                "value": "" if pd.isna(row["VALUE"]) else str(row["VALUE"]).strip()
            })

        testcases.append({
            "name": sheet_name,
            "steps": steps
        })

    return testcases