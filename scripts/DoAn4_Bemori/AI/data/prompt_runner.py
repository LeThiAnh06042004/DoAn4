import os
import re
from AI.data.ai_generator import generate_ai_data, write_files
from AI.data.data_validator import validate_data
from AI.data.coverage_checker import check_coverage
from AI.data.ai_prompt_template import BASE_PROMPT_TEMPLATE

def extract_folder(prompt):
    match = re.search(r"Tên folder:\s*(\w+)", prompt)
    if not match:
        raise ValueError("Prompt thiếu: Tên folder")
    return match.group(1)

def extract_formats(prompt):
    match = re.search(r"Sinh các file dữ liệu:\s*([^\n]+)", prompt)
    if not match:
        raise ValueError("Prompt thiếu: Sinh các file dữ liệu")
    return [f.strip() for f in match.group(1).split(",")]

def extract_schema_from_prompt(prompt: str):
    """ Trích xuất schema từ phần 'Cấu trúc mỗi item' trong prompt """
    schema = {}
    lines = prompt.splitlines()
    in_structure = False
    for line in lines:
        line = line.strip()
        if "Cấu trúc mỗi item" in line or "Cấu trúc dữ liệu" in line:
            in_structure = True
            continue
        if in_structure and line.startswith("- "):
            # Match cả có ngoặc và không ngoặc
            # Ví dụ: - noi_dung (nội dung bình luận): string
            # hoặc - keyword: string
            match = re.match(r'-\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(\w+)?', line)
            if match:
                field = match.group(1)
                field_type = match.group(3) or "string"
                schema[field] = {"type": field_type}
        if in_structure and not line.startswith("- ") and line:
            in_structure = False

    # Tìm max_length chung (áp dụng cho tất cả field)
    max_matches = re.findall(r'tối đa\s*(\d+)\s*ký tự', prompt, re.IGNORECASE)
    if max_matches:
        max_len = int(max_matches[0])
        for field in schema:
            schema[field]["max_length"] = max_len

    # Fallback nếu không extract được
    if not schema:
        schema = {"keyword": {"type": "string", "max_length": 255}}

    return schema

def extract_coverage_rules_from_prompt(prompt: str):
    """ Tự động trích xuất các loại coverage cần check từ prompt """
    coverage = {
        "empty": False,
        "number": False,
        "special": False,
        "unicode": False,
        "max_length": 255
    }

    lower_prompt = prompt.lower()
    if "rỗng" in lower_prompt or "trống" in lower_prompt:
        coverage["empty"] = True
    if "số" in lower_prompt or "chữ số" in lower_prompt or "digit" in lower_prompt:
        coverage["number"] = True
    if "ký tự đặc biệt" in lower_prompt or "special" in lower_prompt or "!@#" in lower_prompt:
        coverage["special"] = True
    if "tiếng việt" in lower_prompt or "có dấu" in lower_prompt or "unicode" in lower_prompt:
        coverage["unicode"] = True

    max_match = re.search(r'tối đa\s*(\d+)\s*ký tự', lower_prompt)
    if max_match:
        coverage["max_length"] = int(max_match.group(1))

    return coverage

def build_prompt(user_prompt):
    """ Ghép prompt user vào template chuẩn """
    return BASE_PROMPT_TEMPLATE.format(USER_PROMPT=user_prompt.strip())

def run_prompt(user_prompt):
    folder = extract_folder(user_prompt)
    formats = extract_formats(user_prompt)

    # Tự động lấy schema và coverage từ prompt
    schema = extract_schema_from_prompt(user_prompt)
    coverage_rules = extract_coverage_rules_from_prompt(user_prompt)

    print("DEBUG - Schema tự động:", schema)
    print("DEBUG - Coverage rules tự động:", coverage_rules)

    # đường dẫn root project
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    output_dir = os.path.join(base_dir, "data", folder)
    os.makedirs(output_dir, exist_ok=True)

    all_data = []
    prompt = build_prompt(user_prompt)

    for round_i in range(5):
        print(f"\nROUND {round_i+1}")
        data = generate_ai_data(prompt)
        all_data.extend(data)

        valid, invalid = validate_data(all_data, schema)
        print("VALID:", len(valid))
        print("INVALID:", len(invalid))

        coverage, missing = check_coverage(valid, coverage_rules)
        print("COVERAGE:", coverage)

        if not missing and len(invalid) == 0:
            write_files(valid, folder, formats)
            print("\nDONE - Coverage OK")
            return

        if missing:
            print("MISSING COVERAGE:", missing)
            user_prompt += f"\nBổ sung dữ liệu còn thiếu coverage: {missing}"
            prompt = build_prompt(user_prompt)

    write_files(valid, folder, formats)
    print("\nSTOP - đạt giới hạn vòng lặp")