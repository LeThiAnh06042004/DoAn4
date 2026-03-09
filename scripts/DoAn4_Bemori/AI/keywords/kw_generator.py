#sinh file keyword tự động từ danh sách keyword (dạng JSON/dict) do AI sinh ra trước đó.

import os

# các template để format
CLASS_TEMPLATE = """class {class_name}:
    \"\"\"
    {description_en}
    Nghĩa tiếng Việt: {description_vi}
    \"\"\"
{methods}
"""

METHOD_TEMPLATE = """
    def {method_name}(self{arguments_signature}):
        \"\"\"
        {display_name_vi}
        \"\"\"
        pass
"""


def generate_keyword_file(keyword_list, output_dir):
    if not keyword_list: # nếu ds rỗng thì ko lmj
        return

    class_name = keyword_list[0]["class_name"] #Lấy tên class từ keyword đầu tiên

    # duyệt qua từng keyword
    methods_str = ""

    for kw in keyword_list:
        arguments_signature = ""
        if kw["arguments"]:
            arguments_signature = ", " + ", ".join(kw["arguments"])

        methods_str += METHOD_TEMPLATE.format(
            method_name=kw["method_name"],
            arguments_signature=arguments_signature,
            display_name_vi=kw["display_name_vi"]
        )

    content = CLASS_TEMPLATE.format(
        class_name=class_name,
        description_en=keyword_list[0]["description_en"],
        description_vi=keyword_list[0]["description_vi"],
        methods=methods_str
    )

    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"{class_name}.py")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[CREATED] {file_path}")