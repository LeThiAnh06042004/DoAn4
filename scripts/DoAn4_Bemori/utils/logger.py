import os
import logging

def init_logger(logs_dir: str):
    log_file = os.path.join(logs_dir, "log.txt") #xđ file log

    logger = logging.getLogger("TestLogger") #lấy logger chung
    logger.setLevel(logging.DEBUG) #cấu hình level cho log, nhận mọi log từ DEBUG trở lên

    if logger.hasHandlers(): #xoá handler cũ, tránh log bị in lặp nhiều lần
        logger.handlers.clear()

    #ghi log ra file
    fh = logging.FileHandler(log_file, mode="w", encoding="utf-8") #mỗi lần chạy test tạo ra log mới
    fh.setLevel(logging.DEBUG) #ghi tất cả log

    #ghi log ra console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) #chỉ in INFO, WARNING, ERROR

    #Cấu hình thời gian cho log
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    #gán format cho handler đảm bảo file và console log cùng format
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    #thêm handler vào log
    logger.addHandler(fh) #thêm vào file
    logger.addHandler(ch) #thêm vào console

    logger.info(f"File log đã được tạo: {log_file}")
    return logger, log_file
