import json
from AI.ai_client import call_llm


# Structured Prompt Engineering
TESTCASE_PROMPT_TEMPLATE = """
Bạn là Senior QA Automation Engineer có 15 năm kinh nghiệm, cực kỳ nghiêm ngặt trong việc thiết kế test case cho Keyword-Driven Testing.

================ BỐI CẢNH ================

- Mục tiêu:
  + Test case phải đầy đủ bước
  + Atomic
  + Chỉ 1 lỗi mỗi Alternate Flow
  + Dễ mapping semantic
  + Dễ chuyển thành keyword test script

================ QUY TRÌNH BẮT BUỘC ================

Với mỗi execution path bạn PHẢI:
1. Xác định rõ Basic Flow hay Alternate Flow.
2. Giữ đầy đủ các user action quan trọng trong execution path.
3. Xây dựng:
   - precondition
   - scenario
   - steps
   - expected_result
4. Tự kiểm tra nghiêm ngặt trước khi output.

================ QUY TẮC CỰC KỲ QUAN TRỌNG ================

**Negative Testing Rule (BẮT BUỘC PHẢI TUÂN THỦ):**
- Basic Flow:
  + Chỉ dùng dữ liệu hợp lệ
  + KHÔNG có bất kỳ lỗi nào

- Alternate Flow:
  + CHỈ KIỂM TRA DUY NHẤT 1 ĐIỀU KIỆN LỖI
  + Nếu execution path có nhiều lỗi,
    chỉ được chọn 1 lỗi rõ nhất
  + Các trường còn lại phải dùng dữ liệu hợp lệ
  + Tuyệt đối không kết hợp 2 lỗi trong cùng 1 test case

**Coverage Rule:**
- Không được bỏ bất kỳ user action quan trọng nào trong execution path.
- Phải giữ đúng thứ tự nghiệp vụ của execution path.

**Steps Requirements:**
- Mỗi step chỉ đúng 1 hành động.
- KHÔNG được gộp nhiều hành động trong 1 step.
- Steps phải rõ ràng, dễ mapping semantic.

**Verify Rule (BẮT BUỘC):**
- Nếu execution path có expected_messages
  hoặc expected_result,
  testcase BẮT BUỘC phải có verify step tương ứng.

Ví dụ:
- Kiểm tra thông báo "xxx" hiển thị
- Kiểm tra trang chủ được hiển thị
- Kiểm tra popup được hiển thị
- Kiểm tra logo được hiển thị

- Mỗi expected_result phải có ít nhất 1 verify step tương ứng trong steps.

**Precondition Rule:**
- Precondition phải phù hợp với execution path.
- Không hardcode precondition cố định.
- Có thể dùng:
  + Người dùng đang ở trang chủ
  + Người dùng đang ở trang đăng nhập
  + Người dùng đang ở trang chi tiết sản phẩm
  + ...

{extra_instruction}

================ TEST CASE ID RULE ================

- test_case_id bắt buộc đánh số tuần tự theo đúng thứ tự execution path:
  + TC_001
  + TC_002
  + TC_003
  + TC_004
  + TC_005

- Không được dùng format khác như:
  + TC_BASIC_001
  + TC_AF1_001
  + TC_006_A1

================ FORMAT OUTPUT ================

Chỉ trả về JSON array:

[
  {{
    "test_case_id": "TC_001",
    "path_id": "PATH_001",
    "scenario": "...",
    "precondition": ["..."],
    "steps": ["Step 1: ..."],
    "expected_result": ["..."]
  }}
]

================ VÍ DỤ QUAN TRỌNG ================

**Alternate Flow chỉ 1 lỗi:**

Execution Path:
AF1 có cả:
- không nhập email
- không nhập mật khẩu

Output đúng:
- Scenario:
  Kiểm tra đăng nhập khi không nhập email

- Steps:
  + Không nhập email
  + Nhập mật khẩu hợp lệ
  + Nhấn nút đăng nhập
  + Kiểm tra thông báo lỗi hiển thị

- Expected:
  + Thông báo lỗi liên quan đến email

Không được viết cả 2 lỗi trong 1 test case.

================ INPUT ================

Execution Paths:
{execution_paths}
"""


def generate_testcases_from_usecase(
        execution_paths,
        regenerate_mode=False,
        missing_actions=None,
        validation_errors=None
):
    extra_instruction = ""

    if regenerate_mode:
        missing_actions = missing_actions or []
        validation_errors = validation_errors or []

        missing_action_text = ""

        if missing_actions:
            missing_action_text = "\n".join(
                f"- {action}"
                for action in missing_actions
            )

        validation_error_text = ""

        if validation_errors:
            validation_error_text = json.dumps(
                validation_errors,
                ensure_ascii=False,
                indent=2
            )

        extra_instruction = f"""
================ REGENERATE MODE ================

- Đây là chế độ sinh lại test case chưa đạt validation.
- Chỉ sinh test case cho đúng execution path được cung cấp.
- Không được sinh thêm test case cho path khác.
- Không được tạo lại test case cũ.
- Không được merge nhiều điều kiện lỗi.

- Nếu lỗi validation là MULTIPLE_NEGATIVE_CONDITIONS:
  + Phải sửa test case để chỉ còn DUY NHẤT 1 điều kiện lỗi.
  + Điều kiện lỗi được giữ lại phải đúng với execution path đầu vào.
  + Các điều kiện lỗi khác phải bị loại bỏ.
  + Các trường dữ liệu không liên quan phải dùng dữ liệu hợp lệ.

- Nếu execution path là Basic Flow:
  + Không được sinh bất kỳ điều kiện lỗi nào.
  + Tất cả input phải là dữ liệu hợp lệ.

- Nếu execution path là Alternate Flow:
  + Chỉ dùng đúng điều kiện lỗi trong alternate flow đó.
  + Không thêm lỗi khác.

- Nếu validator cung cấp danh sách missing action,
  test case sinh lại BẮT BUỘC phải bổ sung đầy đủ các action đó.

Missing actions:
{missing_action_text}

Validation errors:
{validation_error_text}

- Nếu chỉ có 1 execution path đầu vào thì chỉ trả về 1 test case.
"""

    prompt = TESTCASE_PROMPT_TEMPLATE.format(
        extra_instruction=extra_instruction,
        execution_paths=json.dumps(
            execution_paths,
            ensure_ascii=False,
            indent=2
        )
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


# save testcase ra file JSON.
def save_testcases(testcases, output_path):
    with open(
            output_path,
            "w",
            encoding="utf-8"
    ) as f:
        json.dump(
            testcases,
            f,
            ensure_ascii=False,
            indent=2
        )