# tách Use Case thành các execution paths, mỗi path sẽ được dùng để AI sinh test case
import re


def build_execution_paths(usecase_text):
    #Tách Use Case thành từng dòng, Xóa khoảng trắng đầu/cuối, Bỏ dòng rỗng
    lines = [
        line.strip()
        for line in usecase_text.splitlines()
        if line.strip()
    ]

    basic_steps = [] # Lưu các bước của Basic Flow
    alternate_flows = [] # Lưu các Alternate Flow

    in_basic = False # Đang đọc phần Basic Flow hay không
    in_alternate = False # Đang đọc phần Alternate Flow hay không
    current_af = None # Alternate Flow hiện tại đang xử lý

    for line in lines:
        lower = line.lower()

        # Nếu đọc đến phần hậu điều kiện thì dừng lại.
        if lower.startswith("postcondition"):
            break

        # Khi gặp dòng có chữ Basic Flow, chương trình bắt đầu lấy các bước chính.
        if "basic flow" in lower:
            in_basic = True
            in_alternate = False
            continue

        # Khi gặp Alternate Flow, chương trình chuyển sang đọc các luồng thay thế.
        if "alternate flow" in lower:
            in_basic = False
            in_alternate = True
            continue

        # Lấy step trong Basic Flow. ^\d+\. nghĩa là lấy dòng bắt đầu từ 1. 2. 3.
        if in_basic:
            if re.match(r"^\d+\.", line):
                basic_steps.append(line)

        # Nhận diện từng AF. ^AF\d+ nghĩa là dòng bđ = AF1 AF2 AF3
        if in_alternate:
            if re.match(r"^AF\d+", line, flags=re.IGNORECASE):
                if current_af:
                    alternate_flows.append(current_af)

                # Khi gặp AF mới, code tạo title, step
                current_af = {
                    "title": line,
                    "steps": []
                }
                continue

            # Các dòng sau tiêu đề AF sẽ được đưa vào steps
            if current_af:
                current_af["steps"].append(line)

    if current_af:
        alternate_flows.append(current_af)

    execution_paths = []

    # Tạo PATH_001 cho Basic Flow
    execution_paths.append({
        "path_id": "PATH_001",
        "type": "basic",
        "title": "Basic Flow",
        "steps": clean_path_steps(basic_steps), # ds bước đã được làm sạch
        "expected_messages": extract_expected_messages(basic_steps) #các message mong đợi được trích ra
    })

    # Tạo path cho Alternate Flow, AF flow ắt đầu từ PATH_002
    # Mỗi AF sẽ được ghép với Basic Flow bằng hàm build_alternate_path_steps
    for i, af in enumerate(alternate_flows, start=2):
        af_steps = build_alternate_path_steps(
            basic_steps,
            af["steps"]
        )

        execution_paths.append({
            "path_id": f"PATH_{i:03}",
            "type": "alternate",
            "title": af["title"],
            "steps": clean_path_steps(af_steps),
            "expected_messages": extract_expected_messages(af_steps)
        })

    return execution_paths


# tạo path hoàn chỉnh cho alternate flow: Một phần Basic Flow + bước Alternate Flow
def build_alternate_path_steps(basic_steps, alternate_steps):
    branch_steps = get_alternate_step_numbers(
        alternate_steps
    )

    result = []

    if not branch_steps:
        for step in basic_steps:
            if is_user_step(step):
                result.append(step)

        result.extend(alternate_steps)
        return result

    replaced_numbers = set(branch_steps.keys())

    for basic_step in basic_steps:
        step_number = get_step_number(basic_step)

        if not step_number:
            continue

        if step_number in replaced_numbers:
            result.extend(branch_steps[step_number])
            continue

        if is_user_step(basic_step):
            result.append(basic_step)

    existing = set(result)

    for alt_step in alternate_steps:
        if alt_step not in existing:
            result.append(alt_step)

    return result


# Hàm này tìm các bước dạng 1a 2a 3a, lấy ra số và thay thế/gán với bước t.ư vs số đố trong basic flow
def get_alternate_step_numbers(steps):
    result = {}

    for step in steps:
        match = re.match(r"^(\d+)a", step.strip())

        if match:
            number = match.group(1)

            if number not in result:
                result[number] = []

            result[number].append(step)

    return result


# Hàm này loại bỏ bước postcondition và bước xử lý nội bộ của hệ thống
def clean_path_steps(steps):
    cleaned = []

    for step in steps:
        if is_postcondition_step(step):
            continue

        if is_internal_system_step(step):
            continue

        cleaned.append(step)

    return cleaned


# Lấy số thứ tự của step
def get_step_number(step):
    match = re.match(r"^(\d+)", step.strip())

    if match:
        return match.group(1)

    return None


# Hàm này kiểm tra một step có phải hành động của người dùng không.
def is_user_step(step):
    text = step.lower()

    return (
        "người dùng" in text
        or "user" in text
    )


# Nếu step chứa các cụm này thì được xem là bước xử lý nội bộ.
def is_internal_system_step(step):
    text = step.lower()

    internal_keywords = [
        "hệ thống kiểm tra",
        "hệ thống xử lý",
        "system checks",
        "system processes"
    ]

    return any(
        keyword in text
        for keyword in internal_keywords
    )


# Nhận diện postcondition
def is_postcondition_step(step):
    text = step.lower()

    return (
        text.startswith("postcondition")
        or text.startswith("- ")
    )


# lấy message mong đợi từ step. Nó chỉ xét các step có từ khóa bên dưới, sau đó tìm nội dung trong dấu ngoặc kép
def extract_expected_messages(steps):
    messages = []

    for step in steps:
        lower = step.lower()

        if (
            "thông báo" not in lower
            and "message" not in lower
            and "hiển thị" not in lower
            and "có chứa" not in lower
            and "contains" not in lower
        ):
            continue

        found = re.findall(
            r'[\"“]([^\"”]+)[\"”]',
            step
        )

        for message in found:
            if message:
                messages.append(message.strip())

    return messages