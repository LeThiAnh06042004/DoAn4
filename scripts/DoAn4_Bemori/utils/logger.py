import os
import logging


# Khai báo hàm
def init_logger(
        logs_dir: str, # Thư mục chứa log
        log_file_name: str = "log.txt" # Tên file log mặc định
):
    # Tạo đường dẫn file log
    log_file = os.path.join(
        logs_dir,
        log_file_name
    )

    # Lấy logger chung
    logger = logging.getLogger("TestLogger")
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers(): # Xóa handler cũ
        logger.handlers.clear()

    # ghi log ra file
    fh = logging.FileHandler( #Tạo FileHandler
        log_file,
        mode="w",
        encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG) # Thiết lập mức log

    # Tạo StreamHandler: ghi log ra console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) #Level cho console

    # Tạo format log
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Gán format
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Gắn handler vào logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(
        f"File log đã được tạo: {log_file}"
    )

    return logger, log_file