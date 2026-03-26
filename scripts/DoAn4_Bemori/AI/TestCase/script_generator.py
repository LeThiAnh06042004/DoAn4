import json
import re
import yaml
import inspect

from AI.ai_client import call_llm
from core.kw_common import KWCommon
from utils.config_loader import load_config


# ===== LOAD KEYWORDS =====
def load_keywords_with_desc():
    keyword_docs = []

    for name, func in inspect.getmembers(KWCommon, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue

        doc = inspect.getdoc(func) or ""
        keyword_docs.append(f"{name}: {doc}")

    return keyword_docs


# ===== PARSE JSON =====
def extract_json(raw: str):
    raw = raw.strip()
    raw = re.sub(r"```json", "", raw)
    raw = re.sub(r"```", "", raw)

    match = re.search(r"\[.*\]", raw, re.DOTALL)

    if match:
        return json.loads(match.group(0))

    raise Exception("Không parse được JSON từ AI")


# ===== INJECT SETUP / TEARDOWN =====
def inject_setup_teardown(result):

    config = load_config()
    base_url = config.get("base_url", "")

    if not base_url:
        print("⚠ base_url chưa được cấu hình!")

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


# ===== PROMPT =====
PROMPT = """
Bạn là chuyên gia kiểm thử phần mềm.

Hãy chuyển test case thành keyword-driven steps.

================ KEYWORDS =================
{keywords}

================ YÊU CẦU =================
1. Chỉ được dùng keyword trong danh sách trên
2. Keyword phải EXACT với tên method
3. Không được tự tạo keyword mới
4. Không bỏ qua bước VERIFY
5. Locator phải lấy từ danh sách
6. Value dùng biến dạng ${{field}} nếu là input

================ OUTPUT =================
[
  {{
    "test_case_id": "...",
    "steps": [
      {{
        "keyword": "...",
        "locator": "...",
        "value": "..."
      }}
    ]
  }}
]

================ INPUT =================
Testcases:
{testcases}

Locators:
{locators}

Data:
{data}
"""


# ===== MAIN =====
def generate_keyword_steps(testcases, locator_path, data_path=None):

    # ===== KEYWORDS =====
    keyword_docs = load_keywords_with_desc()
    keyword_str = "\n".join(keyword_docs)

    # ===== LOCATORS =====
    with open(locator_path, "r", encoding="utf-8") as f:
        locators = yaml.safe_load(f)

    locator_keys = list(locators.keys())
    locators_str = json.dumps(locator_keys, ensure_ascii=False, indent=2)

    # ===== DATA =====
    data_content = ""
    if data_path:
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data_content = f.read()
        except:
            pass

    # ===== PROMPT =====
    prompt = PROMPT.format(
        keywords=keyword_str,
        testcases=json.dumps(testcases, indent=2, ensure_ascii=False),
        locators=locators_str,
        data=data_content
    )

    raw = call_llm(prompt)

    print("===== RAW AI OUTPUT =====")
    print(raw)

    # ===== PARSE =====
    result = extract_json(raw)

    # ===== INJECT SETUP =====
    result = inject_setup_teardown(result)

    # ===== VALIDATION =====
    valid_keywords = set([
        name for name, _ in inspect.getmembers(KWCommon, predicate=inspect.isfunction)
        if not name.startswith("_")
    ])

    for tc in result:
        has_verify = False

        for step in tc["steps"]:
            kw = step.get("keyword", "")

            if kw not in valid_keywords:
                print(f"❌ Sai keyword: {kw}")

            if "VERIFY" in kw:
                has_verify = True

        if not has_verify:
            print(f"⚠ Missing VERIFY: {tc['test_case_id']}")

    return result