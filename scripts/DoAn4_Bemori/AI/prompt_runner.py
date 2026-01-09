import os
import re
from AI.ai_prompt_template import BASE_PROMPT_TEMPLATE
from AI.ai_generator import generate_ai_data


#hàm nhận vào prompt và trả về chuỗi text
def extract_folder(prompt: str) -> str:
    match = re.search(r"Tên folder:\s*(\w+)", prompt) #Tìm và lấy tên, bỏ qua khoảng trắng, tên chỉ có chữ, số, _
    if not match:
        raise ValueError("Prompt thiếu: Tên folder")
    return match.group(1)

#hàm nhận vào prompt và trả về ds các chuỗi text
def extract_formats(prompt: str) -> list[str]:
    match = re.search(r"Sinh các file dữ liệu:\s*([^\n]+)", prompt) #lấy toàn bộ phần phía sau : đến hết dòng
    if not match:
        raise ValueError("Prompt thiếu: Sinh các file dữ liệu")

    return [f.strip() for f in match.group(1).split(",")]


def run_prompt(user_prompt: str):
    #lấy ttin từ prompt
    folder = extract_folder(user_prompt)
    formats = extract_formats(user_prompt)

    #ghép prompt hoàn chỉnh gửi cho AI
    prompt = BASE_PROMPT_TEMPLATE.format(
        USER_PROMPT=user_prompt.strip()
    )

    #xác định chỗ lưu file
    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(base_dir, "data", "ai", folder)
    os.makedirs(output_dir, exist_ok=True) #nếu chưa có thì tạo mới

    #gọi AI sinh dữ liệu và ghi file
    for ext in formats:
        output_path = os.path.join(output_dir, f"data_{folder}_ai.{ext}")
        generate_ai_data(prompt, output_path)
