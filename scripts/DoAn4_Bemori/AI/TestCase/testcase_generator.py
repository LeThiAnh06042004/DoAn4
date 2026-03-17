#Sinh test case tự động từ Use Case bằng AI

import json
import os

from AI.ai_client import call_llm
from AI.TestCase.execution_path_extractor import extract_execution_paths
from AI.TestCase.prompt_template import TESTCASE_PROMPT_TEMPLATE

#Hàm chuyển Use Case → Test Cases
def generate_testcases_from_usecase(use_case_text: str):

    # 1. hàm phân tích UC để sinh execution paths
    execution_paths = extract_execution_paths(use_case_text)

    # 2. tạo prompt gửi AI
    prompt = TESTCASE_PROMPT_TEMPLATE.format(
        # Chuyển execution_paths → JSON sau đó Chèn vào prompt template
        execution_paths=json.dumps(execution_paths, ensure_ascii=False, indent=2)
    )

    # 3. gọi AI
    raw = call_llm(prompt)

    raw = raw.strip() #xoá khoảng trắng

    try:
        data = json.loads(raw) #Parse JSON từ AI (nếu AI trả về JSON chẩn thì chuyển thành Python list)

    #Xử lý khi AI trả về JSON lỗi
    except Exception:
        #Timf vị trí [ ... ]
        start = raw.find("[")
        end = raw.rfind("]")

        if start != -1 and end != -1:
            raw = raw[start:end + 1] #Cắt phần JSON
            data = json.loads(raw) #Parse lại JSON
        else:
            raise ValueError("AI response không phải JSON hợp lệ")

    return data #Trả về testcases


#Hàm lưu test case
def save_testcases(testcases, output_path):
    #Tạo thư mục nếu chưa tồn tại
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    #Ghi file JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(testcases, f, ensure_ascii=False, indent=2) #lưu TC thành JSON