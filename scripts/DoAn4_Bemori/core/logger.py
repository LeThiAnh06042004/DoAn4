import logging
import os
from datetime import datetime


class Logger:
    @staticmethod
    def get_logger(name="framework"):
        # Tạo folder logs nếu chưa có
        log_dir = "reports/logs"
        os.makedirs(log_dir, exist_ok=True)

        # Đặt tên file log theo ngày giờ
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

        # Cấu hình logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Ghi ra file
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(file_formatter)

        # Ghi ra console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)

        # Gắn handler
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger
