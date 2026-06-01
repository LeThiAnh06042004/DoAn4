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
2. Giữ đầy đủ TẤT CẢ user action quan trọng trong execution path.
3. Đặc biệt KHÔNG được bỏ các bước điều hướng/mở trang/truy cập trang như:
   - Người dùng truy cập vào trang ...
   - Người dùng mở trang ...
   - Người dùng vào trang ...
   - Người dùng nhấn vào link ...
4. Xây dựng:
   - precondition
   - scenario
   - steps
   - expected_result
5. Tự kiểm tra nghiêm ngặt trước khi output.

================ QUY TẮC CỰC KỲ QUAN TRỌNG ================

**Coverage Rule:**
- Không được bỏ bất kỳ user action quan trọng nào trong execution path.
- Bước điều hướng/truy cập trang là user action quan trọng, bắt buộc phải giữ lại trong steps.
- Phải giữ đúng thứ tự nghiệp vụ của execution path.
- Không được tự thêm bước mới không tồn tại trong execution path.
- Không được tự bỏ bước.

**Negative Testing Rule:**
- Basic Flow:
  + Chỉ dùng dữ liệu hợp lệ
  + KHÔNG có bất kỳ lỗi nào

- Alternate Flow:
  + CHỈ KIỂM TRA DUY NHẤT 1 ĐIỀU KIỆN LỖI
  + Các trường còn lại phải dùng dữ liệu hợp lệ
  + Tuyệt đối không kết hợp 2 lỗi trong cùng 1 test case

**Steps Requirements:**
- Mỗi step chỉ đúng 1 hành động.
- KHÔNG được gộp nhiều hành động trong 1 step.
- Steps phải rõ ràng, dễ mapping semantic.

**Expected Result Rule:**
- expected_result PHẢI được lấy trực tiếp từ execution path.
- Nếu execution path có expected_messages thì expected_result phải lấy đúng expected_messages.
- Không được tự sáng tạo expected_result.
- Không được tự tạo thông báo mới.
- Không được thay đổi nội dung thông báo trong execution path.

**Verify Rule:**
- Mỗi expected_result phải có ít nhất 1 verify step tương ứng trong steps.
- Verify step phải mô tả rõ đối tượng cần kiểm tra.

Ví dụ đúng:
- Kiểm tra thông báo "Bạn chưa nhập số điện thoại." hiển thị
- Kiểm tra thông báo "Số điện thoại chỉ bao gồm những số." hiển thị
- Kiểm tra trang chủ được hiển thị
- Kiểm tra trang chi tiết sản phẩm được hiển thị

Không được viết chung chung như:
- Kiểm tra thông báo lỗi
- Kiểm tra kết quả
- Kiểm tra thành công
- Kiểm tra hiển thị

**Precondition Rule:**
- Precondition chỉ mô tả trạng thái ban đầu trước khi thực hiện test.
- Không được đưa user action chính của execution path vào precondition để thay thế step.
- Nếu execution path có bước “Người dùng truy cập vào trang chi tiết sản phẩm”
  thì bước này vẫn phải nằm trong steps, không được chuyển thành precondition.

{extra_instruction}

================ TEST CASE ID RULE ================

- test_case_id bắt buộc đánh số tuần tự theo đúng thứ tự execution path:
  + TC_001
  + TC_002
  + TC_003
  + TC_004
  + TC_005

================ FORMAT OUTPUT ================

Chỉ trả về JSON array:

[
  {{
    "test_case_id": "TC_001",
    "path_id": "PATH_001",
    "scenario": "...",
    "precondition": [
      "..."
    ],
    "steps": [
      "Step 1: ..."
    ],
    "expected_result": [
      "..."
    ]
  }}
]

================ VÍ DỤ QUAN TRỌNG ================

Execution Path:
1. Người dùng truy cập vào trang chi tiết sản phẩm
2. Người dùng nhập số điện thoại
3. Người dùng nhấn nút "Gửi"
4. Hệ thống hiển thị thông báo "Bạn chưa nhập số điện thoại."

Output đúng:

[
  {{
    "test_case_id": "TC_001",
    "path_id": "PATH_001",
    "scenario": "Kiểm tra đặt hàng nhanh khi không nhập số điện thoại",
    "precondition": [
      "Người dùng đang ở trang chủ website"
    ],
    "steps": [
      "Step 1: Truy cập vào trang chi tiết sản phẩm",
      "Step 2: Không nhập số điện thoại",
      "Step 3: Nhấn nút \\"Gửi\\"",
      "Step 4: Kiểm tra thông báo \\"Bạn chưa nhập số điện thoại.\\" hiển thị"
    ],
    "expected_result": [
      "Bạn chưa nhập số điện thoại."
    ]
  }}
]

================ SELF-CHECKLIST ================

Trước khi output phải tự kiểm tra:
- Có giữ đủ bước điều hướng/truy cập trang không?
- Có giữ đủ user action quan trọng không?
- Có đúng thứ tự execution path không?
- Có verify step cụ thể không?
- expected_result có lấy trực tiếp từ execution path không?
- Alternate Flow có đúng 1 lỗi không?

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