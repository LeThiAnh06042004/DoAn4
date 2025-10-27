import os
import logging

#truyền vào đg dẫn thư mục chứa log
def init_logger(logs_dir: str):
    log_file = os.path.join(logs_dir, "log.txt") #tạo file log mỗi lần chạy

    logger = logging.getLogger("TestLogger") #tạo hoặc lấy 1 logger
    logger.setLevel(logging.DEBUG) #cho phép ghi tất cả các cấp độ log

    # nếu logger này đã có handler thì Xóa handler cũ tránh lặp log
    if logger.hasHandlers():
        logger.handlers.clear()

    # Ghi log ra file, w là ghi đè file cũ mỗi lần chạy test mới
    fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG) #ghi toàn bộ log từ mức độ debug


    ch = logging.StreamHandler() #ghi log ra console
    ch.setLevel(logging.INFO) #chỉ hiển thị log từ mức độ info

    # Định dạng log
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s") #time - caaps độ - nd
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh) #xuất ra file
    logger.addHandler(ch) #xuất ra console

    logger.info(f"File log đã được tạo. File log: {log_file}")
    return logger, log_file #logger: ghi log trong frame, log_file đính kèm vào report
