import os
import yaml

def load_config():
    # Lấy đường dẫn tuyệt đối tới file config.yaml trong thư mục config/
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "config", "config.yaml")

    #mở file ở chế độ đọc và mã hoá utf8
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) #đọc nd và chuyển thành dict
