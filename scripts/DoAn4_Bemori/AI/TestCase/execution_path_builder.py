import re


def build_execution_paths(usecase_text):
    lines = [
        line.strip()
        for line in usecase_text.splitlines()
        if line.strip()
    ]

    basic_steps = []
    alternate_flows = []

    in_basic = False
    in_alternate = False
    current_af = None

    for line in lines:
        lower = line.lower()

        if lower.startswith("postcondition"):
            break

        if "basic flow" in lower:
            in_basic = True
            in_alternate = False
            continue

        if "alternate flow" in lower:
            in_basic = False
            in_alternate = True
            continue

        if in_basic:
            if re.match(r"^\d+\.", line):
                basic_steps.append(line)

        if in_alternate:
            if re.match(r"^AF\d+", line, flags=re.IGNORECASE):
                if current_af:
                    alternate_flows.append(current_af)

                current_af = {
                    "title": line,
                    "steps": []
                }
                continue

            if current_af:
                current_af["steps"].append(line)

    if current_af:
        alternate_flows.append(current_af)

    execution_paths = []

    execution_paths.append({
        "path_id": "PATH_001",
        "type": "basic",
        "title": "Basic Flow",
        "steps": clean_path_steps(basic_steps),
        "expected_messages": extract_expected_messages(basic_steps)
    })

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


def clean_path_steps(steps):
    cleaned = []

    for step in steps:
        if is_postcondition_step(step):
            continue

        if is_internal_system_step(step):
            continue

        cleaned.append(step)

    return cleaned


def get_step_number(step):
    match = re.match(r"^(\d+)", step.strip())

    if match:
        return match.group(1)

    return None


def is_user_step(step):
    text = step.lower()

    return (
        "người dùng" in text
        or "user" in text
    )


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


def is_postcondition_step(step):
    text = step.lower()

    return (
        text.startswith("postcondition")
        or text.startswith("- ")
    )


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