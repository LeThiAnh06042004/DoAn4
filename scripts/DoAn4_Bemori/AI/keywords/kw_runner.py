import os
import json
import re
import sys
import inspect
from pathlib import Path
from AI.ai_client import call_llm
from AI.keywords.kw_validator import validate_keywords
from core.kw_common import KWCommon

# ==============================
# TEMPLATE sinh file keyword class
# ==============================
CLASS_TEMPLATE = """from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class {class_name}:
    \"\"\" 
    {description_en}
    Nghĩa tiếng Việt: {description_vi}
    \"\"\"

    def __init__(self, driver, locator_reader=None):
        self.driver = driver
        self.locator_reader = locator_reader
        self.wait = WebDriverWait(driver, 10)

    {methods}
"""

METHOD_TEMPLATE = """
    def {method_name}(self{arguments_signature}):
        \"\"\" {display_name_vi} \"\"\"
        # TODO: Implement logic here
        pass
"""

def extract_folder_from_prompt(prompt_file_path: str) -> str:
    """ Sinh tên folder từ file prompt: kw_TimKiem.py → keyword_TimKiem """
    filename = Path(prompt_file_path).stem
    if not filename.startswith("kw_"):
        raise ValueError("File prompt phải bắt đầu bằng 'kw_'")
    function_name = filename.replace("kw_", "")
    return f"keyword_{function_name}"

def extract_json_from_text(text: str) -> str | None:
    """ Tìm và trích xuất JSON array từ phản hồi AI một cách linh hoạt """
    if not text:
        return None

    # Clean text trước khi tìm: loại bỏ khoảng trắng thừa, xuống dòng không cần thiết
    text = ' '.join(text.split())

    # Cách 1: Tìm khối bắt đầu bằng [ và kết thúc bằng ] (greedy để lấy hết)
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError as e:
            print(f"JSON parse lỗi: {e} - Chuỗi: {json_str[:100]}...")


def get_existing_keywords():
    """ Lấy tất cả method (keyword) hiện có trong KWCommon """
    existing = set()
    for name, obj in inspect.getmembers(KWCommon, predicate=inspect.isfunction):
        if not name.startswith("_"):
            existing.add(name)
    return existing

def run_keyword_prompt(prompt: str, prompt_file_path: str, max_retries=3):
    try:
        print(f"Đang xử lý prompt file: {prompt_file_path}")

        refined_prompt = prompt
        raw_response = None
        for attempt in range(max_retries):
            raw_response = call_llm(refined_prompt)
            print(f"RAW RESPONSE (lần {attempt+1}):")
            print(raw_response)

            json_str = extract_json_from_text(raw_response)
            if json_str:
                keyword_list = json.loads(json_str)
                if isinstance(keyword_list, list):
                    print(f"Tìm thấy {len(keyword_list)} keyword từ AI")
                    break
            refined_prompt = prompt + "\n\nCHỈ TRẢ VỀ JSON ARRAY THUẦN TÚY. KHÔNG TEXT NÀO KHÁC. Ví dụ: [\"KEYWORD (nghĩa)\"]"

        else:
            raise ValueError("AI không trả JSON đúng sau nhiều lần thử")

        # Lấy keyword đã tồn tại trong KWCommon
        existing_keywords = get_existing_keywords()
        print(f"Đã có {len(existing_keywords)} keyword trong KWCommon")

        # Lọc bỏ keyword đã tồn tại
        new_keywords = []
        for kw in keyword_list:
            if isinstance(kw, str):
                method_name = kw.split(" (")[0].strip() if " (" in kw else kw.strip()
            else:
                method_name = kw.get("method_name", "")

            if method_name and method_name not in existing_keywords:
                new_keywords.append(kw)
            else:
                print(f"Bỏ qua keyword đã tồn tại: {method_name}")

        if not new_keywords:
            print("Tất cả keyword đã tồn tại trong KWCommon. Không cần sinh mới.")
            return

        # Validate trùng lặp trong danh sách mới
        valid_keywords, duplicates = validate_keywords(new_keywords)
        print(f"Valid new keywords: {len(valid_keywords)} | Duplicates: {len(duplicates)}")

        # Tạo tên class và folder
        folder_name = extract_folder_from_prompt(prompt_file_path)
        class_name = folder_name.replace("keyword_", "").capitalize() + "Keywords"

        description_en = f"Keyword library for {folder_name.replace('keyword_', '')}"
        description_vi = f"Thư viện keyword cho chức năng {folder_name.replace('keyword_', '')}"

        # Sinh nội dung file
        methods_str = ""
        for kw in valid_keywords:
            if isinstance(kw, str):
                method_name = kw.split(" (")[0].strip() if " (" in kw else kw.strip()
                display_name_vi = kw.split(" (")[1].rstrip(")") if " (" in kw else method_name
            else:
                method_name = kw.get("method_name", "UNKNOWN")
                display_name_vi = kw.get("display_name_vi", method_name)

            methods_str += METHOD_TEMPLATE.format(
                method_name=method_name,
                arguments_signature="",
                display_name_vi=display_name_vi
            )

        content = CLASS_TEMPLATE.format(
            class_name=class_name,
            description_en=description_en,
            description_vi=description_vi,
            methods=methods_str
        )

        # LƯU VÀO THƯ MỤC ĐÃ CÓ SẴN: AI/keywords/kw/keyword_xxx/
        # Dùng đường dẫn tuyệt đối từ gốc project
        project_root = Path(__file__).parent.parent.parent  # D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori
        base_dir = project_root / "AI" / "keywords" / "kw"
        target_dir = base_dir / folder_name
        target_dir.mkdir(parents=True, exist_ok=True)

        output_file = target_dir / f"{class_name}.py"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"ĐÃ SINH THÀNH CÔNG file keyword mới:")
        print(output_file)

        # Lưu JSON raw
        json_output = target_dir / "keywords_raw.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(valid_keywords, f, ensure_ascii=False, indent=2)
        print(f"JSON tham khảo: {json_output}")

    except Exception as e:
        print("LỖI:", str(e))
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python kw_runner.py <đường_dẫn_file_prompt>")
        print("Ví dụ: python kw_runner.py AI/prompts/kw_TimKiem.py")
        sys.exit(1)

    prompt_file_path = sys.argv[1]
    if not Path(prompt_file_path).exists():
        print(f"File không tồn tại: {prompt_file_path}")
        sys.exit(1)

    with open(prompt_file_path, "r", encoding="utf-8") as f:
        prompt_content = f.read()

    run_keyword_prompt(prompt_content, prompt_file_path)