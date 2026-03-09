import yaml
from pathlib import Path
import logging


class LocatorReader:
    """
    Class đọc locator từ file YAML (hoặc các định dạng khác nếu mở rộng).
    Dùng để cung cấp locator cho KWCommon trong framework KDT.
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.locators = self._load_locators()
        logging.info(f"Đã load {len(self.locators)} locator từ {self.file_path}")

    def _load_locators(self) -> dict:
        """Đọc file YAML và trả về dict locator"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File locator không tồn tại: {self.file_path}")

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ValueError("File YAML phải là dict (key: locator name)")
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Lỗi đọc YAML: {e}")
        except Exception as e:
            raise RuntimeError(f"Lỗi khi load locator file: {e}")

    def get(self, key: str) -> dict:
        """
        Lấy locator theo key (ví dụ: 'txtTimKiem')
        Trả về dict {'strategy': ..., 'value': ...}
        """
        if key not in self.locators:
            raise KeyError(f"Locator key '{key}' không tồn tại trong file YAML")
        return self.locators[key]

    def __contains__(self, key: str) -> bool:
        """Kiểm tra key có tồn tại không"""
        return key in self.locators

    def __len__(self) -> int:
        """Số lượng locator"""
        return len(self.locators)

    def keys(self):
        """Trả về tất cả các key locator"""
        return self.locators.keys()