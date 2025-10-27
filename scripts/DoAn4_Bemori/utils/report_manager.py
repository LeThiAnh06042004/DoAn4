import os
from datetime import datetime


def get_base_reports_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports")) #đường dẫn đến folder reports


def init_report_dirs():
    """Tạo thư mục báo cáo theo timestamp."""
    base_reports = get_base_reports_dir() #đường dẫn đến folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") #tạo chuỗi time
    base_dir = os.path.join(base_reports, timestamp) #ghép lại với nhau thành vị trí lưu

    logs_dir = os.path.join(base_dir, "logs") #folder lưu file log
    screenshots_dir = os.path.join(base_dir, "screenshots") #folder lưu ảnh chụp lỗi
    html_dir = os.path.join(base_dir, "html") #folder lưu file báo cáo html

    #tạo thư mục nếu chưa tồn tại
    for d in [logs_dir, screenshots_dir, html_dir]:
        os.makedirs(d, exist_ok=True)

    #trả về 1 dict chứa các đường dẫn
    return {
        "base_dir": base_dir,
        "logs_dir": logs_dir,
        "screenshots_dir": screenshots_dir,
        "html_dir": html_dir,
    }
