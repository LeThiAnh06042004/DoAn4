# #sinh dữ liệu kiểm thử và ghi dữ liệu đó ra nhiều định dạng file
#
# import json
# import os
# import pandas as pd
# import yaml
# import xml.etree.ElementTree as ET
# from AI.ai_client import call_llm
#
# #gửi prompt cho AI và lấy dữ liệu test dưới dạng list dictionary
# def generate_ai_data(prompt: str):
#     #Gửi prompt đến AI.
#     raw = call_llm(prompt)
#     #Làm sạch dữ liệu: bỏ khoảng trắng đầu, cuối và xuống dòng
#     raw = raw.strip()
#
#     # chặn expression kiểu JS
#     if ".repeat(" in raw:
#         print("AI sinh expression repeat - bỏ vòng")
#         return []
#
#     try:
#         data = json.loads(raw) #Chuyển JSON string thành Python object.
#
#     #nếu JSON lỗi
#     except Exception:
#         #Tìm JSON trong text
#         start = raw.find("[")
#         end = raw.rfind("]")
#
#         if start != -1 and end != -1:
#             json_text = raw[start:end + 1] #Cắt phần JSON
#
#             try:
#                 data = json.loads(json_text) #Parse lại JSON
#             except Exception:
#                 print("\nAI trả JSON lỗi - bỏ vòng")
#                 print(raw)
#                 return []
#         else:
#             print("\nAI trả JSON lỗi - bỏ vòng")
#             print(raw)
#             return []
#
#     #Nếu AI trả dictionary, code sẽ thêm [] Để đồng bộ format list.
#     if isinstance(data, dict):
#         data = [data]
#
#     #Nếu AI trả list string
#     if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
#         data = [{"value": v} for v in data]
#
#     return data #trả về dl
#
#
# #ghi dữ liệu test ra nhiều định dạng file khác nhau
# def write_files(data, folder, formats):
#     #Xác định thư mục project để lấy đường dẫn gốc
#     base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
#
#     #Tạo thư mục output
#     output_dir = os.path.join(
#         base_dir,
#         "data",
#         folder
#     )
#     #Tạo thư mục nếu chưa tồn tại
#     os.makedirs(output_dir, exist_ok=True)
#
#     #Tạo DataFrame
#     df = pd.DataFrame(data)
#     #Ghi file theo từng format
#     for ext in formats:
#         #Tạo đường dẫn file
#         path = os.path.join(
#             output_dir,
#             f"data_{folder}_ai.{ext}"
#         )
#
#         #ghi csv
#         if ext == "csv":
#             df.to_csv(path, index=False, encoding="utf-8-sig")
#
#         elif ext == "xlsx":
#             df.to_excel(path, index=False)
#
#         elif ext == "json":
#             with open(path, "w", encoding="utf-8") as f:
#                 json.dump(data, f, ensure_ascii=False, indent=2)
#
#         elif ext in ["yaml", "yml"]:
#             with open(path, "w", encoding="utf-8") as f:
#                 yaml.safe_dump(data, f, allow_unicode=True)
#
#         elif ext == "txt":
#             with open(path, "w", encoding="utf-8") as f:
#                 for row in data:
#                     f.write(",".join(str(v) for v in row.values()) + "\n")
#
#         elif ext == "xml":
#             root = ET.Element("data")
#             for row in data:
#                 item = ET.SubElement(root, "item") #tạo item
#                 for k, v in row.items():
#                     #Thêm field
#                     child = ET.SubElement(item, k)
#                     child.text = str(v)
#
#             tree = ET.ElementTree(root)
#             tree.write(path, encoding="utf-8", xml_declaration=True) #Lưu XML
#
#         print("Saved:", path)