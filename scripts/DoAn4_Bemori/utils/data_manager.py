import csv
import json
import yaml
import os
import pandas as pd


class DataManager:

    @staticmethod
    def read_csv(file_path):
        with open(file_path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f)) #csv.DictReader đọc từng dòng và biến mỗi dòng thành dict, với header là key

    @staticmethod
    def read_json(file_path):
        with open(file_path, encoding="utf-8") as f:
            return json.load(f) #json.load() đọc và parse dữ liệu JSON. Tự động trả về dict hoặc list

    @staticmethod
    def read_yaml(file_path):
        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f) #Trả về dict hoặc list tương tự JSON.

    @staticmethod
    def read_excel(file_path, sheet_name=0): #mặc định đọc sheet đầu tiên
        df = pd.read_excel(file_path, sheet_name=sheet_name) # Dùng pandas để đọc
        return df.to_dict(orient="records") #mỗi dòng = 1 dict.

    @staticmethod
    def read_txt(file_path):
        with open(file_path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()] #Mỗi dòng trong file .txt được đọc và loại bỏ dòng trống. Trả về list chuỗi

    @staticmethod
    def load_data(file_path, sheet_name=0):
        #tách phần mở rộng file, không phân biệt hoa thường.
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
