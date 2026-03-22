import json
from AI.ai_client import call_llm


PROMPT = """
Bạn là chuyên gia kiểm thử phần mềm.

Hãy chuyển test case thành keyword-driven steps.

Yêu cầu:

- Sử dụng keyword từ KWCommon (INPUT_TEXT, CLICK...)
- Mỗi step gồm: keyword, locator, value

QUAN TRỌNG:

1. Không hardcode locator → phải lấy từ danh sách locator
2. Locator phải khớp EXACT với file locator
3. Chỉ dùng placeholder theo tên field trong data:
   - ví dụ: ${{keyword}}, ${{ho_ten}}
4. Không tạo biến sai:
   - ${{validKeyword}}
   - ${{click}}
5. Nếu keyword không cần data → value = ""

Output JSON:

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

Testcases:
{testcases}

Locators:
{locators}

Data:
{data}
"""


def generate_keyword_steps(testcases, locator_path, data_path=None):
    with open(locator_path, "r", encoding="utf-8") as f:
        locators = f.read()

    data_content = ""
    if data_path:
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data_content = f.read()
        except:
            pass

    prompt = PROMPT.format(
        testcases=json.dumps(testcases, ensure_ascii=False, indent=2),
        locators=locators,
        data=data_content
    )

    raw = call_llm(prompt).strip()

    try:
        return json.loads(raw)
    except:
        start = raw.find("[")
        end = raw.rfind("]")
        return json.loads(raw[start:end + 1])