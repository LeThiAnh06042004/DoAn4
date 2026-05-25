# ỨNG DỤNG AI SINH TESTCASE CHO FRAMEWORK KIỂM THỬ TỰ ĐỘNG WEB

---

# Giới thiệu

Đây là framework kiểm thử tự động Web được xây dựng theo mô hình Hybrid-Driven Testing, kết hợp giữa:

- Keyword-Driven Testing (KDT)
- Data-Driven Testing (DDT)
- Page Object Model (POM)

Framework được phát triển bằng:

- Python
- Selenium WebDriver
- Pytest

Ngoài ra, hệ thống còn tích hợp AI nhằm hỗ trợ:

- Sinh test case từ Use Case
- Sinh execution path
- Chuyển đổi test case thành keyword script thông qua cơ chế ánh xạ

---

# Các chức năng chính

## AI Generate Test Case

- Phân tích Use Case
- Sinh execution path
- Sinh test case tự động bằng AI
- Validate test case
- Export JSON / Excel

## Generate Test Script

Framework sử dụng cơ chế ánh xạ để sinh test script tự động:

- Keyword Mapping
- Semantic Locator Mapping
- Data Binding

## Automation Execution

- Selenium WebDriver
- Pytest Execution
- HTML Report
- Screenshot khi fail
- Logging

---

# Công nghệ sử dụng

| Công nghệ | Vai trò |
| --- | --- |
| Python | Ngôn ngữ chính |
| Selenium WebDriver | Tự động hóa trình duyệt |
| Pytest | Tổ chức và thực thi kiểm thử |
| Pandas | Đọc dữ liệu Excel |
| Sentence Transformers | Semantic Locator Mapping |
| LM Studio | Chạy mô hình AI local |
| openai/gpt-oss-20b | Sinh test case |

---

# Kiến trúc hệ thống

```text
Use Case
    ↓
AI Generate Test Case
    ↓
Generate Test Script
(Keyword + Locator + Data Mapping)
    ↓
Pytest + Selenium Execution
    ↓
HTML Report
```

---

# Cấu trúc thư mục

```text
project/
│
├── AI/
│   └── TestCase/
│       ├── TC/
│       ├── UC/
│       ├── scripts/
│       ├── testcase_generator.py
│       ├── script_generator.py
│       ├── testcase_validator.py
│       ├── execution_path_builder.py
│       ├── run_testcase_generation.py
│       └── ai_client.py
│
├── core/
│   ├── base_driver.py
│   ├── keyword_dispatcher.py
│   └── kw_common.py
│
├── pages/
│
├── reports/
│
├── resources/
│   ├── data/
│   └── locators/
│
├── test/
│   ├── cases/
│   └── suites/
│
├── utils/
│
├── conftest.py
├── pytest.ini
└── requirements.txt
```

---

# Cài đặt môi trường

## Clone project

```bash
git clone <repository-url>
cd project-name
```

---

## Tạo virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / MacOS

```bash
source venv/bin/activate
```

---

# Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

# requirements.txt

```text
selenium
pytest
pytest-html
pandas
pyyaml
sentence-transformers
torch
openpyxl
requests
```

---

# Cài đặt ChromeDriver

- Tải ChromeDriver phù hợp với phiên bản Chrome
- Cấu hình đường dẫn trong framework

---

# Cấu hình AI với LM Studio

## Bước 1: Cài đặt LM Studio

Tải tại:

```text
https://lmstudio.ai/
```

---

## Bước 2: Tải model

```text
openai/gpt-oss-20b
```

---

## Bước 3: Start Local Server

- Mở LM Studio
- Chọn tab Developer
- Start Server

Mặc định:

```text
http://localhost:1234
```

---

# Cấu hình AI Client

File:

```text
AI/TestCase/ai_client.py
```

Ví dụ:

```python
import requests

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "local-model"


def call_llm(prompt: str) -> str:

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "Bạn là Tester chuyên nghiệp"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        LM_STUDIO_URL,
        json=payload
    )

    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]
```

---

# Hướng dẫn quản lý locator

Locator được quản lý tại:

```text
resources/locators/
```

Ví dụ:

```yaml
GuiBinhLuan:
  by: xpath
  value: //button[@type='submit']
  type: button
  semantic:
    - gửi bình luận
    - submit comment
    - nút gửi
```

---

# Hướng dẫn thêm locator mới

Ví dụ:

```yaml
InputHoTen:
  by: xpath
  value: //input[@name='name']
  type: input
  semantic:
    - nhập họ tên
    - ô họ tên
    - name input
```

Framework sẽ tự động đọc locator mới trong quá trình semantic mapping.

---

# Hướng dẫn quản lý dữ liệu kiểm thử

Dữ liệu kiểm thử được lưu tại:

```text
resources/data/
```

Framework hỗ trợ:

- CSV
- Excel
- JSON
- YAML
- TXT
- SQLite

---

# Semantic Locator Mapping

Framework sử dụng:

```text
paraphrase-multilingual-MiniLM-L12-v2
```

để thực hiện semantic similarity giữa:

- step text
- semantic locator

Framework sử dụng:

- embedding vector
- cosine similarity
- bonus rule

để chọn locator phù hợp nhất.

---

# Data Binding

Framework hỗ trợ:

- infer condition
- validate data
- tìm dòng dữ liệu phù hợp
- bind dữ liệu vào keyword step

Ví dụ:

- empty
- invalid_char
- min_length
- valid

---

# CÁCH 1 — Chạy kiểm thử tự động thông thường

Áp dụng khi đã có sẵn test case trong framework.

---

## Bước 1: Mở project bằng PyCharm

Mở project framework trong PyCharm.

---

## Bước 2: Chọn test case

Vào thư mục:

```text
test/cases/
```

Ví dụ:

```text
test_login.py
test_comment.py
```

---

## Bước 3: Chạy kiểm thử

Có thể:

- nhấn nút Run trên PyCharm

hoặc chạy bằng terminal:

```bash
pytest test/cases/test_login.py
```

---

## Bước 4: Xem kết quả

Kết quả được lưu tại:

```text
reports/
```

Bao gồm:

- HTML report
- log
- screenshot khi lỗi

---

# CÁCH 2 — Chạy kiểm thử tự động với AI

Áp dụng khi muốn sinh test case và test script tự động từ Use Case.

---

## Bước 1: Chuẩn bị Use Case

Đặt file Use Case vào:

```text
AI/TestCase/UC/
```

Ví dụ:

```text
UC_BinhLuan.txt
```

---

## Bước 2: Khởi động LM Studio

- Load model:

```text
openai/gpt-oss-20b
```

- Start Server tại:

```text
http://localhost:1234
```

---

## Bước 3: Sinh test case bằng AI

```bash
python testcase_generator.py
```

Framework sẽ:

- phân tích Use Case
- sinh execution path
- gửi prompt cho AI
- validate test case
- export JSON / Excel

Kết quả được lưu tại:

```text
AI/TestCase/TC/
```

---

## Bước 4: Sinh test script

```bash
python script_generator.py
```

Framework sẽ:

- keyword mapping
- semantic locator mapping
- data binding

Kết quả lưu tại:

```text
AI/TestCase/scripts/
```

---

## Bước 5: Thực thi test script do AI sinh ra

```bash
python run_test.py
```

Framework sẽ:

- đọc file Excel
- dispatch keyword
- thực thi Selenium
- verify kết quả
- ghi log
- sinh report HTML

---

## Bước 6: Xem kết quả

Kết quả được lưu tại:

```text
reports/
```

---

# Hướng dẫn thêm keyword mới

Keyword được quản lý tại:

```text
core/kw_common.py
```

Ví dụ:

```python
# Example keyword

def hover_element(driver, locator):
    ...
```

Sau đó đăng ký keyword trong:

```text
core/keyword_dispatcher.py
```

Ví dụ:

```text
"HOVER" -> hover_element
```

---

# Chạy kiểm thử

## Chạy toàn bộ test

```bash
pytest
```

---

## Chạy file test cụ thể

```bash
pytest test/test_login.py
```

---

## Chạy với HTML Report

```bash
pytest --html=reports/report.html
```

---

# Kết quả kiểm thử

Framework hỗ trợ:

- HTML Report
- Screenshot khi fail
- Logging
- PASS / FAIL Summary

Thư mục report:

```text
reports/
```

---

# Chức năng đã thực nghiệm

Framework đã được thực nghiệm trên website Bemori với các chức năng:

- Tìm kiếm sản phẩm
- Bình luận sản phẩm
- Đặt hàng nhanh
- Mua hàng

---

# Hướng phát triển

- Mobile Testing
- API Testing
- CI/CD Integration
- AI nâng cao
- UI quản lý test case
- Self-healing locator

---

# Tác giả

- Họ tên: Lê Thị Ánh
- Đề tài: Ứng dụng AI sinh testcase cho framework kiểm thử tự động Web