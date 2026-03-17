# File điều phối toàn bộ quá trình từ Use Case → AI → Test Case → xuất Excel

import os
import testcase_generator
from AI.TestCase.testcase_excel_exporter import export_testcases_to_excel


#hàm điều khiển toàn bộ quy trình sinh test case tự động
def run_generation():
    #Lấy đường dẫn thư mục chứa file Python đang chạy.
    base_dir = os.path.dirname(os.path.abspath(__file__))

    #Xác định đường dẫn Use Case
    uc_path = os.path.join(base_dir, "UC", "UC_TimKiem.txt")

    #Đọc nội dung Use Case
    with open(uc_path, "r", encoding="utf-8") as f:
        use_case_text = f.read()

    # Sinh test case bằng AI
    testcases = testcase_generator.generate_testcases_from_usecase(use_case_text)

    # Tạo tên file JSON
    uc_filename = os.path.basename(uc_path)
    tc_filename = uc_filename.replace("UC_", "TC_").replace(".txt", ".json")

    #Tạo đường dẫn output
    output_path = os.path.join(base_dir, "TC", tc_filename)

    #Lưu test case vào JSON
    testcase_generator.save_testcases(testcases, output_path)

    # Chuẩn bị export sang Excel
    module_name = uc_filename.replace("UC_", "").replace(".txt", "")

    #Đường dẫn file Excel template
    template_path = os.path.join(base_dir, "Sample_TestCase.xlsx")

    #Xuất test case ra Excel
    export_testcases_to_excel(
        testcases=testcases,
        module_name=module_name,
        template_path=template_path
    )

    print("Sinh test case thành công!")
    print("JSON Output:", output_path)
    print("Excel đã được cập nhật:", template_path)


if __name__ == "__main__":
    run_generation()