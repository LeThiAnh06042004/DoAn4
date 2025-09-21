import csv
import json
import yaml
import os
import pandas as pd


class DataManager:

    @staticmethod
    def read_csv(file_path):
        with open(file_path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    @staticmethod
    def read_json(file_path):
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def read_yaml(file_path):
        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def read_excel(file_path, sheet_name=0):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df.to_dict(orient="records")

    @staticmethod
    def read_txt(file_path):
        with open(file_path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    @staticmethod
    def load_data(file_path, sheet_name=0):
        """Tự động detect loại file"""
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == ".csv":
            return DataManager.read_csv(file_path)
        elif ext == ".json":
            return DataManager.read_json(file_path)
        elif ext in [".yaml", ".yml"]:
            return DataManager.read_yaml(file_path)
        elif ext in [".xlsx", ".xls"]:
            return DataManager.read_excel(file_path, sheet_name)
        elif ext == ".txt":
            return DataManager.read_txt(file_path)
        else:
            raise ValueError(f"Định dạng file {ext} không được hỗ trợ!")
