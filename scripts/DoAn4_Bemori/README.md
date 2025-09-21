1. Xây dựng nền tảng Core
- base_driver.py: khởi tạo WebDriver (đa trình duyệt, đọc config).
- base_page.py: class gốc cho tất cả Page Object (click, send_keys, get_text, wait…).
- base_test.py: class gốc cho test case (setup/teardown driver).
- data_manager.py: đọc dữ liệu CSV, Excel, JSON, YAML…
- logger.py: ghi log.

2. Tạo cấu hình & locator
- config/config.yaml: URL, timeout, browser mặc định.
- locators/*.yaml: quản lý locator tập trung.

3. Xây dựng Pages (POM)
- pages/base_page.py: lớp cha.
- pages/login_page.py: ví dụ login.
- pages/dashboard_page.py: ví dụ dashboard.

4. Viết test case mẫu (pytest)
- tests/functional/test_login.py: test login dùng data-driven.

5. Quản lý Test Suite
- suites/smoke_suite.py: gom test case thành suite.
- Có thể chạy bằng marker pytest -m smoke.

6. Báo cáo
- Tích hợp pytest-html hoặc allure.
- Thêm hook screenshot (trong conftest.py) khi test fail.

7. Data-driven nâng cao
- Hỗ trợ nhiều định dạng file (csv, json, yaml, xlsx, xls, txt).
- Đặt dữ liệu vào data/.

8. AI Generator (sau cùng)
- Module ai/ để sinh test case .py dựa trên dữ liệu hoặc mô tả.
- Dùng openai + jinja2 template để sinh file Python.