from utils.action_patterns import ACTION_PATTERNS

# Chuẩn hoá câu input trước khi match
def normalize_text(text):
    return text.lower().strip()


# Nhận 1 step -> 1 kw phù hợp nhất
def extract_action(step_text):

    text = normalize_text(step_text) #chuẩn hoá input

    # kw phù hợp nhất sẽ được lưu ở biến này và score cao nhất sẽ thắng
    best_keyword = None
    best_score = 0

    # Duệt toàn bộ rule và tính điểm
    for keyword, patterns in ACTION_PATTERNS.items():

        score = 0

        for pattern in patterns:
            # Kiểm tra xem pattern có xuất hiện không
            # Nếu có cộng “mức độ quan trọng” cho keyword đó và = độ dài chuỗi pattern
            if pattern in text:
                score += len(pattern)

        # keyword nào match nhiều pattern hơn sẽ chọn
        if score > best_score:
            best_score = score
            best_keyword = keyword

    return best_keyword

