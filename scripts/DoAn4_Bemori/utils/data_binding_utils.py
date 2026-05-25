import re
import sqlite3
from unidecode import unidecode

from utils.data_loader import (
    load_json_data,
    load_csv_data,
    load_yaml_data,
    load_excel_data,
    load_txt_data,
    load_sqlite_data
)

from utils.locator_utils import normalize_locator_name
from utils.data_condition_infer import infer_condition
from utils.data_validator import validate_data_value


# lấy table đầu tiên trong SQLite database
def get_first_sqlite_table(db_path):
    conn = sqlite3.connect(db_path) # Connect SQLite
    cursor = conn.cursor()

    # Query table
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )

    # Lấy table đầu tiên
    result = cursor.fetchone()

    conn.close()

    if not result:
        raise Exception("SQLite không có table nào.")

    return result[0]


def load_test_data(data_path):
    ext = data_path.split(".")[-1].lower() # ext detection

    if ext == "json":
        return load_json_data(data_path)

    if ext == "csv":
        return load_csv_data(data_path)

    if ext in ["yaml", "yml"]:
        return load_yaml_data(data_path)

    if ext in ["xls", "xlsx"]:
        return load_excel_data(data_path)

    if ext == "txt":
        return load_txt_data(data_path)

    if ext in ["sqlite", "db"]:
        table_name = get_first_sqlite_table(data_path)
        return load_sqlite_data(data_path, table_name)

    raise Exception(f"Không hỗ trợ file data: {ext}")


# Nhiều field có thể là string hoặc list. Hàm này normalize tất cả thành list.
def ensure_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


# Chuẩn hóa text để map semantic, map column, compare field
def normalize_key(text):
    if text is None:
        return ""

    text = str(text).lower() # lowercase
    text = unidecode(text) # bỏ dấu

    return re.sub(r"[^a-z0-9]", "", text) # remove special chars


# LOCATOR DATABASE BUILDER
def build_locator_context(locators):
    locator_context = []

    for key, value in locators.items():
        locator_context.append({
            "name": key,
            "type": normalize_locator_name(key),
            "semantic": value.get("semantic", []),
            "data_key": value.get("data_key", []),
            "by": value.get("by", "")
        })

    return locator_context


# Tìm locator object theo tên
def get_locator_obj(locator_name, locator_context):
    for loc in locator_context:
        if loc.get("name") == locator_name:
            return loc

    return None


# Tìm các candidate để map locator ↔ data column
def get_data_key_candidates(locator_obj):
    if not locator_obj:
        return []

    candidates = []

    # Candidate sources: data_key
    candidates.extend(
        ensure_list(locator_obj.get("data_key", []))
    )

    locator_name = locator_obj.get("name", "")

    # Prefix stripping
    # giúp framework có thể tự suy luận data field ngay cả khi YAML chưa có data_key.
    for prefix in ["txt", "ta", "ddl", "cbo", "chk", "rb"]:
        if locator_name.startswith(prefix):
            candidates.append(locator_name[len(prefix):])
            break

    return [
        c for c in candidates
        if c
    ]


# Tìm column data phù hợp với locator + condition
def find_data_column(row, locator_obj, condition):
    candidates = get_data_key_candidates(locator_obj)

    if not candidates:
        return None

    condition_type = condition.get("type", "valid") # condition_type
    condition_norm = normalize_key(condition_type)

    candidate_norms = [
        normalize_key(c)
        for c in candidates
    ]

    for col in row.keys():
        col_norm = normalize_key(col)

        # Match ưu tiên cao nhất
        # Ví dụ: Candidate: phone, Condition: empty -> Match: Phone_Empty
        for cand in candidate_norms:
            if cand in col_norm and condition_norm in col_norm:
                return col

    for col in row.keys():
        col_norm = normalize_key(col)

        for cand in candidate_norms:
            if col_norm == cand:
                return col

    for col in row.keys():
        col_norm = normalize_key(col)

        for cand in candidate_norms:
            if cand in col_norm or col_norm in cand:
                return col

    return None


# kiểm tra field có liên quan tới text không
def field_related_to_text(locator_obj, text):
    if not locator_obj or not text:
        return False

    text_norm = normalize_key(text)

    values = []

    values.extend(
        ensure_list(locator_obj.get("data_key", []))
    )

    values.extend(
        ensure_list(locator_obj.get("semantic", []))
    )

    values.append(
        locator_obj.get("name", "")
    )

    for value in values:
        value_norm = normalize_key(value)

        if value_norm and value_norm in text_norm:
            return True

    return False


# Condition có thể nằm ở step, scenario, expected result
def infer_condition_for_input(raw_step, tc, locator_obj):
    # Step priority
    step_condition = infer_condition(raw_step)

    if step_condition.get("type") != "valid":
        return step_condition

    # Nếu step không detect được, Framework check: scenario, expected_result
    scenario = tc.get("scenario", "")

    expected_text = " ".join(
        tc.get("expected_result", [])
    )

    related_text = ""

    if field_related_to_text(locator_obj, scenario):
        related_text += " " + scenario

    if field_related_to_text(locator_obj, expected_text):
        related_text += " " + expected_text

    if related_text.strip():
        condition = infer_condition(related_text)

        if condition.get("type") != "valid":
            return condition

    return {
        "type": "valid"
    }


# Không chọn data random Mà chọn row thỏa toàn bộ condition
def find_matching_data_row(data_rows, input_infos):
    if isinstance(data_rows, dict):
        data_rows = [data_rows]

    if not input_infos:
        return None

    # Ưu tiên: dòng phải thỏa toàn bộ input
    # Duyệt từng row
    for row in data_rows:
        if not isinstance(row, dict):
            continue

        all_matched = True

        # Duyệt từng input
        for info in input_infos:
            locator_obj = info.get("locator_obj")
            condition = info.get("condition", {"type": "valid"})

            # Find column
            col = find_data_column(
                row,
                locator_obj,
                condition
            )

            if not col:
                all_matched = False
                break

            value = row.get(col, "")


            # Validate value
            if not validate_data_value(value, condition):
                all_matched = False
                break

        # Nếu tất cả match
        if all_matched:
            return row

    print("[DATA WARNING] Không tìm được dòng data thỏa toàn bộ input condition.")
    return None


# bind value
def get_value_from_row(row, locator_obj, condition=None):
    if not row or not locator_obj:
        return ""

    if condition is None:
        condition = {
            "type": "valid"
        }

    # Find đúng column
    col = find_data_column(
        row,
        locator_obj,
        condition
    )

    if not col:
        return ""

    # Return đúng value
    value = row.get(col, "")

    if value is None:
        return ""

    return value