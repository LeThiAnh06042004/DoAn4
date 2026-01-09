BASE_PROMPT_TEMPLATE = """
Bạn là AI sinh dữ liệu kiểm thử tự động.

YÊU CẦU BẮT BUỘC:
1. Chỉ trả về JSON hợp lệ
2. JSON phải là ARRAY
3. Mỗi giá trị trong JSON:
   - Chỉ là dữ liệu chuỗi thuần (string, number, boolean)
   - Không sử dụng:
     + repeat
     + concat
     + toán tử +, *
     + hàm
     + biểu thức lập trình
4. Không markdown
5. Không mô tả
6. Không giải thích
7. Không sinh filename
8. Không sinh content file
9. Không sinh cấu trúc lồng liên quan đến file
10. Chỉ sinh dữ liệu thô phục vụ ghi file

LƯU Ý, NHẮC NHỞ:
- Bắt buộc phải khai báo:
  + Tên folder
  + Các định dạng file cần sinh (csv, txt, json, xlsx, …)
- Phải mô tả rõ cấu trúc mỗi item
- Phải mô tả rõ các rule hợp lệ / không hợp lệ

PHẦN YÊU CẦU CỤ THỂ
{USER_PROMPT}

ĐẦU RA
Chỉ trả về 1 JSON ARRAY hợp lệ.
"""
