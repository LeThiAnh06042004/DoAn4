import json
import re
import yaml
import inspect

from AI.ai_client import call_llm
from core.kw_common import KWCommon
from utils.config_loader import load_config
from utils.locator_utils import build_locator_hint
from utils.locator_utils import normalize_locator_name


# LOAD KEYWORD
def load_keywords_with_desc():
    keyword_docs = []

    # Lấy toàn bộ function trong class KWCommon
    for name, func in inspect.getmembers(KWCommon, predicate=inspect.isfunction):
        if name.startswith("_"): # Loại bỏ function private
            continue

        # Lấy docstring
        doc = inspect.getdoc(func) or ""
        keyword_docs.append(f"{name}: {doc}")

    return keyword_docs


# PARSE JSON
def extract_json(raw: str):
    raw = raw.strip()

    # remove markdown
    raw = re.sub(r"```json", "", raw)
    raw = re.sub(r"```", "", raw)

    # remove comment kiểu // ...
    raw = re.sub(r"//.*", "", raw)

    # remove comment kiểu /* ... */
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)

    # remove trailing commas
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)

    match = re.search(r"\[.*\]", raw, re.DOTALL)

    if match:
        json_str = match.group(0)
        return json.loads(json_str)

    raise Exception("Không parse được JSON từ AI")


# SETUP
def inject_setup_teardown(result):

    config = load_config()
    base_url = config.get("base_url", "")

    if not base_url:
        print("base_url chưa được cấu hình!")

    for tc in result:

        steps = tc.get("steps", [])

        if not steps:
            continue

        steps.insert(0, {
            "keyword": "OPEN_URL",
            "locator": "",
            "value": base_url
        })

        steps.append({
            "keyword": "CLOSE_BROWSER",
            "locator": "",
            "value": ""
        })

    return result


# PROMPT
PROMPT = """
Bạn là chuyên gia kiểm thử phần mềm.

================ CHỦ ĐỀ HỆ THỐNG =================
{topic}

Hãy chuyển test case thành keyword-driven steps.

================ KEYWORDS =================
{keywords}

================ YÊU CẦU =================
1. Chỉ được dùng keyword trong danh sách trên
2. Keyword phải EXACT với tên method
3. Không được tự tạo keyword mới
4. Không bỏ qua bước VERIFY
5. Locator phải lấy từ danh sách

6. PHẢI sinh dữ liệu THỰC (value)
   - Phù hợp với test case
   - Phù hợp với ngữ cảnh

7. Quy tắc dữ liệu:
   - valid → dữ liệu hợp lệ
   - invalid → dữ liệu sai
   - empty → ""
   - boundary → giá trị biên

8. KHÔNG dùng placeholder (<valid>, <invalid>...)

9. TẤT CẢ dữ liệu PHẢI liên quan đến CHỦ ĐỀ
   - Value phải là thực thể, từ khóa hoặc nội dung thuộc domain của hệ thống
   - Không được dùng dữ liệu chung chung hoặc không liên quan

10. KHÔNG được sử dụng dữ liệu thuộc domain khác
    - Ví dụ:
      Nếu hệ thống là ecommerce → không dùng dữ liệu về ngân hàng
      Nếu hệ thống là giáo dục → không dùng dữ liệu về sản phẩm

11. Dữ liệu phải có ý nghĩa thực tế với người dùng cuối
    - Không dùng chuỗi vô nghĩa như: "abc123", "qwerty"

================ LOCATORS =================
{locators}

Mỗi locator gồm:
- name: tên locator
- type: loại element (input, button, dropdown...)
- desc: mô tả chức năng

→ Chọn locator phù hợp nhất với step dựa trên desc và type
→ Không chọn sai locator

================ OUTPUT =================
[
  {{
    "test_case_id": "...",
    "steps": [
      {{
        "keyword": "...",
        "locator": "...",
        "value": "dữ liệu thực tế đúng chủ đề"
      }}
    ]
  }}
]

================ INPUT =================
Testcases:
{testcases}

Locators:
{locators}
"""


# MAIN
def generate_keyword_steps(testcases, locator_path, topic):

    # ===== KEYWORD =====
    keyword_docs = load_keywords_with_desc()
    keyword_str = "\n".join(keyword_docs)

    # ===== LOCATOR =====
    with open(locator_path, "r", encoding="utf-8") as f:
        locators = yaml.safe_load(f)

    # ===== BUILD LOCATOR CONTEXT =====
    locator_context = []

    for key, value in locators.items():
        desc = value.get("desc", "")
        by = value.get("by", "")

        locator_context.append({
            "name": key,
            "type": normalize_locator_name(key),  # txt -> input, btn -> button...
            "desc": desc,
            "by": by
        })

    # convert sang json để đưa vào prompt
    locators_str = json.dumps(locator_context, ensure_ascii=False, indent=2)

    # ===== BUILD PROMPT =====
    prompt = PROMPT.format(
        keywords=keyword_str,
        testcases=json.dumps(testcases, indent=2, ensure_ascii=False),
        locators=locators_str,
        topic=topic
    )

    # ===== CALL AI =====
    raw = call_llm(prompt)

    print("===== RAW AI OUTPUT =====")
    print(raw)

    result = extract_json(raw)

    # ===== SETUP =====
    result = inject_setup_teardown(result)

    # ===== VALIDATE =====
    valid_keywords = set([
        name for name, _ in inspect.getmembers(KWCommon, predicate=inspect.isfunction)
        if not name.startswith("_")
    ])

    for tc in result:
        has_verify = False

        for step in tc["steps"]:
            kw = step.get("keyword", "")

            if kw not in valid_keywords:
                print(f"Sai keyword: {kw}")

            if "VERIFY" in kw:
                has_verify = True

        if not has_verify:
            print(f"Missing VERIFY: {tc['test_case_id']}")

    return result