import pytest
import os

test_suite = [
    "test_TimKiem.py",
    "test_BinhLuan.py"
]

def test_run_suite():
    #xác định thư mục chứa test
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests"))
    test_paths = [os.path.join(base_dir, f) for f in test_suite] #tạo ds đg dẫn đến từng test

    #gọi pytest để chạy toàn bộ test suite
    pytest.main(test_paths + [
        "-v",
        f"--html=reports/report.html",
        "--self-contained-html"
    ])
