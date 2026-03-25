import json
from AI.ai_client import call_llm


TESTCASE_PROMPT_TEMPLATE = """
Bạn là chuyên gia kiểm thử phần mềm.

Từ các execution path dưới đây hãy sinh các test case kiểm thử.

================ YÊU CẦU CHUNG ================

1. Trả về kết quả dưới dạng JSON hợp lệ.

2. Mỗi test case phải có các trường:

- test_case_id
- scenario
- precondition
- steps
- expected_result

================ QUY TẮC VIẾT TEST CASE ================

Scenario:
- Mô tả ngắn gọn mục tiêu kiểm thử
- Không dài dòng

Precondition:
- Mô tả trạng thái ban đầu của hệ thống

Steps:
- Chỉ mô tả hành động của người dùng
- Không mô tả xử lý nội bộ hệ thống
- KHÔNG sử dụng dữ liệu cụ thể (không dùng giá trị thật như "iphone", "123")
- Sử dụng mô tả tổng quát:
  Ví dụ:
  - Enter valid data
  - Enter invalid data
  - Leave field empty
  - Select an option
  - Click submit button
  - Navigate to page
  - Verify displayed information

- Mỗi step là 1 hành động rõ ràng

QUY TẮC ĐÁNH SỐ STEP:
- Bắt buộc format:
  "Step 1: ..."
  "Step 2: ..."
- Không gộp nhiều hành động
- Không bỏ số thứ tự

Expected Result:
- Chỉ mô tả kết quả quan sát được trên UI
- Không mô tả logic hệ thống

================ QUY TẮC COVERAGE ================

- Mỗi execution path → ít nhất 1 test case
- Không trùng test case
- Nếu steps giống nhau → gộp
- Bao phủ các trường hợp:
  + valid
  + invalid
  + boundary (nếu có)
  + empty (nếu có)

================ QUY TẮC QUAN TRỌNG (PHỤC VỤ SCRIPT) ================

- Steps phải rõ ràng để có thể chuyển sang keyword automation
- Steps phải bao gồm cả bước kiểm tra (verify). Sau khi user thực hiện hành động, phải có bước verify
  Ví dụ:
  + Step 1: Enter valid data into the field
  + Step 2: Click button
  + Step 3: Verify that the result is displayed
- Mỗi expected_result nên tương ứng với 1 bước verify trong steps
- Mỗi hành động phải thể hiện rõ loại thao tác:
  + nhập liệu (input)
  + click
  + chọn (select)
  + kiểm tra (verify)
  + điều hướng (navigate)
- Sử dụng mô tả chung, ví dụ:
  + Enter valid input into the field
  + Enter invalid input
  + Leave the field empty
  + Click button
  + Verify element is displayed
  + Verify message is displayed
- Không viết mơ hồ kiểu:
  "User performs action"
  "System handles request"
- Expected result là một danh sách
  + Mỗi dòng là một kết quả kiểm tra riêng biệt
  + Mỗi expected result phải rõ ràng để có thể map thành một bước verify
  + KHÔNG viết mơ hồ kiểu:
    "system handles..."
    "appropriate result"

================ FORMAT OUTPUT ================

[
  {{
    "test_case_id": "TC_001",
    "scenario": "Short description",
    "precondition": ["..."],
    "steps": [
      "Step 1: ...",
      "Step 2: ..."
    ],
    "expected_result": [
      "..."
    ]
  }}
]

CHỈ trả về JSON. Không giải thích.

================ INPUT ================

Execution Paths:
{execution_paths}
"""


def generate_testcases_from_usecase(usecase_text: str):
    prompt = TESTCASE_PROMPT_TEMPLATE.format(
        execution_paths=usecase_text
    )

    raw = call_llm(prompt).strip()

    try:
        return json.loads(raw)

    except Exception:
        start = raw.find("[")
        end = raw.rfind("]")

        if start != -1 and end != -1:
            return json.loads(raw[start:end + 1])

        raise Exception("Không parse được JSON từ AI")


def save_testcases(testcases, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(testcases, f, ensure_ascii=False, indent=2)