import json
from AI.ai_client import call_llm


# Structured Prompt Engineering
TESTCASE_PROMPT_TEMPLATE = """
================ VAI TRÒ ================

Bạn là Senior QA Engineer chuyên thiết kế test case cho hệ thống kiểm thử tự động.
Bạn có kinh nghiệm:
- ISTQB
- Thiết kế test case theo execution path
- Thiết kế test case phục vụ automation testing
- Keyword-Driven Testing (KDT)

================ BỐI CẢNH HỆ THỐNG ================

- Hệ thống cần kiểm thử là website thương mại điện tử bán gấu bông.
- Các chức năng được kiểm thử gồm:
  + Tìm kiếm sản phẩm
  + Bình luận sản phẩm
  + Đặt hàng nhanh
  + Mua hàng

- Input đầu vào của AI là các execution path đã được chuẩn hóa từ Use Case.
- Mỗi execution path đại diện cho một luồng nghiệp vụ độc lập.

- Framework kiểm thử sử dụng mô hình Keyword-Driven Testing.

- Mục tiêu:
  + đảm bảo coverage cho execution path
  + đảm bảo traceability giữa execution path và test case
  + phục vụ kiểm thử tự động

================ NGÔN NGỮ ================

- Toàn bộ nội dung test case phải được viết bằng TIẾNG VIỆT:
  + scenario
  + precondition
  + steps
  + expected_result

- Riêng tên field JSON phải giữ nguyên tiếng Anh.
- Không tự ý đổi tên field JSON.

================ YÊU CẦU CHUNG ================

1. Chỉ trả về JSON hợp lệ.
2. Không thêm giải thích bên ngoài JSON.
3. Mỗi execution path phải sinh đúng 1 test case.
4. Mỗi test case phải có các trường:
   - test_case_id
   - path_id
   - scenario
   - precondition
   - steps
   - expected_result

================ TRACEABILITY ================

- Mỗi test case phải giữ đúng path_id từ execution path đầu vào.
- Không được tự tạo path_id mới.
- Không được bỏ path_id.

- test_case_id đánh số lần lượt:
  + TC_001
  + TC_002
  + TC_003

================ QUY TẮC VIẾT TEST CASE ================

Scenario:
- Mô tả ngắn gọn mục tiêu kiểm thử.
- Phải phản ánh đúng execution path.
- Không dài dòng.

Precondition:
- Chỉ mô tả trạng thái ban đầu của hệ thống.
- Không đưa thao tác người dùng vào precondition.

- Các hành động như:
  + truy cập trang
  + điều hướng
  + mở màn hình
  + mở chức năng

  phải được viết trong steps,
  KHÔNG được viết trong precondition.

Steps:
- Chỉ mô tả hành động của người dùng hoặc bước kiểm tra trên giao diện.
- Không mô tả xử lý nội bộ hệ thống.

- Không sử dụng dữ liệu cụ thể như:
  + "abc"
  + "123"
  + "Linh"
  + "0912345678"

- Sử dụng mô tả tổng quát như:
  + dữ liệu hợp lệ
  + dữ liệu rỗng
  + dữ liệu không hợp lệ
  + số điện thoại dưới 10 chữ số

- Mỗi step chỉ chứa DUY NHẤT 1 hành động.
- Không gộp nhiều hành động trong một step.

================ BUSINESS RULES / QUY TẮC KIỂM THỬ ================

- Không được viết step chung chung.

Ví dụ sai:
- Nhập dữ liệu
- Nhập thông tin
- Nhấn nút
- Kiểm tra kết quả

- Step nhập liệu phải nêu rõ:
  + nhập trường nào
  + loại dữ liệu gì

Ví dụ đúng:
- Nhập số điện thoại hợp lệ vào ô số điện thoại
- Không nhập nội dung bình luận vào ô bình luận

- Step nhấn nút phải ghi rõ tên nút.

Ví dụ:
- Nhấn nút "Gửi"
- Nhấn nút "Tìm kiếm"

- Step kiểm tra phải ghi rõ đối tượng kiểm tra.

Ví dụ:
- Kiểm tra thông báo "Bạn chưa nhập số điện thoại." hiển thị
- Kiểm tra danh sách sản phẩm phù hợp với từ khóa được hiển thị

================ QUY TẮC ĐÁNH SỐ STEP ================

- Bắt buộc format:
  "Step 1: ..."
  "Step 2: ..."

- Không bỏ số thứ tự.

================ EXPECTED RESULT ================

- Chỉ mô tả kết quả quan sát được trên UI.
- Không mô tả logic xử lý nội bộ.

- Nếu execution path có thông báo hệ thống:
  → expected_result phải chứa đúng thông báo đó.

- Nếu execution path có thông báo trong dấu ngoặc kép hoặc ngoặc kép tiếng Việt:
  → expected_result phải lấy đúng nội dung trong dấu ngoặc đó.
  → Không được tự viết mô tả chung chung.

- Nếu execution path có cụm "có chứa" hoặc "contains":
  → expected_result vẫn phải chứa đúng phần nội dung thông báo được đặt trong dấu ngoặc.

- Không viết chung chung như:
  + Thông báo lỗi hiển thị
  + Hệ thống báo lỗi
  + Hiển thị thông báo phù hợp
  + Thông báo xác nhận được hiển thị

================ QUY TẮC COVERAGE ================

- Basic Flow tạo ra 1 test case.
- Mỗi Alternate Flow tạo ra 1 test case riêng.
- Không tạo test case từ Post Condition.
- Không merge nhiều Alternate Flow vào cùng một test case.

- Alternate Flow phải giữ lại các bước Basic Flow cần thiết trước điểm rẽ nhánh.

- Không được bỏ bước nhập dữ liệu nếu execution path có bước nhập.
- Không được bỏ bước nhấn nút submit/gửi/xác nhận nếu execution path có bước đó.

- Không được bỏ bước:
  + truy cập trang
  + điều hướng
  + mở chức năng
  + chọn sản phẩm
  nếu execution path có các bước này.

================ NEGATIVE TESTING ================

- Mỗi test case lỗi chỉ kiểm thử DUY NHẤT 1 điều kiện lỗi.
- Không được kết hợp nhiều lỗi đầu vào trong cùng một test case.
- Không được merge nhiều Alternate Flow vào một test case.

QUY TẮC CỰC KỲ QUAN TRỌNG:

1. Nếu execution path là Basic Flow:
   - Tất cả dữ liệu nhập phải là dữ liệu hợp lệ.
   - Không được dùng các cụm:
     + không nhập
     + rỗng
     + để trống
     + không hợp lệ
     + ký tự không phải số
     + ít hơn
     + dưới
     + vượt quá

2. Nếu execution path là Alternate Flow:
   - Chỉ được sử dụng đúng 1 điều kiện lỗi được mô tả trong execution path đó.
   - Các trường dữ liệu khác phải được viết là dữ liệu hợp lệ.

Ví dụ SAI:
- Không nhập số điện thoại và nhập số điện thoại chứa ký tự không phải số.
- Không nhập số điện thoại và nhập số điện thoại ít hơn 10 chữ số.

Ví dụ ĐÚNG:
- Test case lỗi rỗng: Không nhập số điện thoại.
- Test case lỗi ký tự: Nhập số điện thoại chứa ký tự không phải số.
- Test case lỗi độ dài: Nhập số điện thoại có ít hơn 10 chữ số.

================ QUY TẮC PHỤC VỤ AUTOMATION ================

- Steps phải rõ ràng để có thể mapping sang automation keyword.

- Không viết:
  + "Người dùng thao tác"
  + "Hệ thống xử lý"
  + "Kiểm tra kết quả"

- Mỗi expected_result phải có ít nhất một step kiểm tra tương ứng.

- Nếu expected_result là:
  + thông báo
  + kết quả hiển thị
  + danh sách
  + màn hình

  thì steps phải có bước:

  "Kiểm tra ... hiển thị"

Ví dụ:
- Kiểm tra thông báo "Bạn chưa nhập tên." hiển thị
- Kiểm tra danh sách sản phẩm được hiển thị

{extra_instruction}

================ FORMAT OUTPUT ================

Chỉ trả về JSON array theo đúng định dạng sau:

[
  {{
    "test_case_id": "TC_001",
    "path_id": "PATH_001",
    "scenario": "...",
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