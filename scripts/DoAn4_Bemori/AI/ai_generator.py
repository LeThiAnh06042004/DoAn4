import json
import pandas as pd
import yaml
from AI.ai_client import call_llm

#Hàm này nhận: prompt (yêu cầu gửi cho AI), output_path (đường dẫn file cần ghi)
def generate_ai_data(prompt: str, output_path: str):
    raw_text = call_llm(prompt) #gọi AI lấy dl

    #ktra AI có trả về JSON hợp lệ ko
    try:
        data = json.loads(raw_text)
    except Exception:
        raise ValueError(f"AI trả về JSON không hợp lệ:\n{raw_text}")

    #xđ định dạng file cần ghi
    ext = output_path.split(".")[-1].lower() #lấy phần đuôi file

    if ext == "csv":
        pd.DataFrame(data).to_csv(output_path, index=False, encoding="utf-8-sig") #chuyển data thành bảng, ghi ra file csv

    elif ext == "xlsx":
        pd.DataFrame(data).to_excel(output_path, index=False)

    elif ext == "json":
        #mở và ghi ra file JSON, giữ tiếng việt với fomat đẹp
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    elif ext in ["yaml", "yml"]:
        # mở và ghi ra file YAML an toàn, giữ tiếng việt có dấu
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)

    elif ext == "txt":
        with open(output_path, "w", encoding="utf-8") as f:
            for row in data:
                #lấy gt của từng field, nối = dấu , ghi mỗi dòng 1 dòng text
                f.write(",".join(str(v) for v in row.values()) + "\n")

    else:
        raise ValueError(f"Không hỗ trợ định dạng: {ext}")
