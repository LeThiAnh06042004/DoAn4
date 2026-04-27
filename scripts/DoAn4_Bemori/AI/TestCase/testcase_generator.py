import json
from AI.ai_client import call_llm


TESTCASE_PROMPT_TEMPLATE = """
Bạn là chuyên gia kiểm thử phần mềm. Từ các execution path dưới đây hãy sinh các test case kiểm thử.

================ NGÔN NGỮ ================
- Toàn bộ nội dung test case phải được viết bằng TIẾNG VIỆT (scenario, precondition, steps, expected_result)
- Riêng tên field JSON (test_case_id, steps...) giữ nguyên tiếng Anh

================ YÊU CẦU CHUNG ================
1. Trả về kết quả dưới dạng JSON hợp lệ.
2. Mỗi test case phải có các trường sau:
   - test_case_id
   - scenario
   - precondition
   - steps
   - expected_result

================ QUY TẮC VIẾT TEST CASE ================
Scenario:
- Mô tả ngắn gọn mục tiêu kiểm thử.
- Không dài dòng.

Precondition:
- Mô tả trạng thái ban đầu của hệ thống.

Steps:
- Chỉ mô tả hành động của người dùng.
- Không mô tả xử lý nội bộ hệ thống.
- KHÔNG sử dụng dữ liệu cụ thể (không dùng giá trị thật như "gaubong", "123").
- Sử dụng mô tả tổng quát.

================ CHUẨN HÓA NGÔN NGỮ HÀNH ĐỘNG ================
- KHÔNG dùng tiếng Anh: Click, Verify, Input, Select...
- Bắt buộc dùng:
  + Nhập
  + Nhấn
  + Chọn
  + Kiểm tra
  + Điều hướng

Ví dụ đúng:
- Step 1: Nhập dữ liệu hợp lệ vào ô nhập
- Step 2: Nhấn nút
- Step 3: Kiểm tra kết quả hiển thị

- Mỗi step là 1 hành động rõ ràng.

QUY TẮC ĐÁNH SỐ STEP:
- Bắt buộc format: "Step 1: ...", "Step 2: ..."
- Không gộp nhiều hành động trong một step.
- Không bỏ số thứ tự.

Expected Result:
- Chỉ mô tả kết quả quan sát được trên UI.
- Không mô tả logic hệ thống.

================ NGOẠI LỆ QUAN TRỌNG (SYSTEM MESSAGE) ================
- Nếu execution path có chứa thông báo hệ thống:
  → PHẢI giữ nguyên nội dung thông báo
  → KHÔNG được viết lại hoặc làm chung chung

================ QUY TẮC COVERAGE ================
- Basic Flow tạo ra 1 test case
- Mỗi Alternate Flow tạo ra 1 test case riêng
- KHÔNG tạo test case từ Post Condition
- KHÔNG tạo test case trùng lặp logic

→ Tổng số test case = số Basic Flow + số Alternate Flow

================ QUY TẮC QUAN TRỌNG (PHỤC VỤ SCRIPT) ================
- Steps phải có bước kiểm tra
- Mỗi expected_result tương ứng với 1 bước kiểm tra
- Không viết mơ hồ kiểu: "User performs action", "System handles request"

================ FORMAT OUTPUT ================
Chỉ trả về JSON array theo đúng định dạng sau, không thêm bất kỳ chữ nào khác:

[
  {{
    "test_case_id": "TC_001",
    "scenario": "Short description",
    "precondition": ["..."],
    "steps": [
      "Step 1: ...",
      "Step 2: ..."
    ],
    "expected_result": ["..."]
  }}
]

================ INPUT ================
Execution Paths: 
{execution_paths}
"""


def generate_testcases_from_usecase(usecase_text: str):
    # Inject dữ liệu vào prompt
    prompt = TESTCASE_PROMPT_TEMPLATE.format(
        execution_paths=usecase_text
    )

    # gọi AI
    raw = call_llm(prompt).strip()

    # PARSE JSON
    # JSON chuẩn
    try:
        return json.loads(raw)

    except Exception:
        # Cắt phần JSON bên trong
        start = raw.find("[")
        end = raw.rfind("]")

        if start != -1 and end != -1:
            return json.loads(raw[start:end + 1])

        raise Exception("Không parse được JSON từ AI")


# Lưu JSON
def save_testcases(testcases, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(testcases, f, ensure_ascii=False, indent=2)