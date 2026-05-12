import json
import re
import yaml
import inspect

from AI.ai_client import call_llm
from core.kw_common import KWCommon
from utils.config_loader import load_config
from utils.locator_utils import normalize_locator_name
from utils.semantic_locator_mapper import map_locator_semantic
from utils.action_extractor import extract_action



# ================= LOAD KEYWORD =================
def load_keywords_with_desc():
    keyword_docs = []

    for name, func in inspect.getmembers(KWCommon, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue

        doc = inspect.getdoc(func) or ""
        keyword_docs.append(f"{name}: {doc}")

    return keyword_docs


# ================= PARSE JSON =================
def extract_json(raw: str):
    raw = raw.strip()

    raw = re.sub(r"```json", "", raw)
    raw = re.sub(r"```", "", raw)
    raw = re.sub(r"//.*", "", raw)
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    raw = re.sub(r",\s*}", "}", raw)
    raw = re.sub(r",\s*]", "]", raw)

    match = re.search(r"\[.*\]", raw, re.DOTALL)

    if match:
        return json.loads(match.group(0))

    raise Exception("Không parse được JSON từ AI")


# ================= SETUP =================
def inject_setup_teardown(result):
    config = load_config()
    base_url = config.get("base_url", "")

    for tc in result:
        steps = tc.get("steps", [])

        keywords = [s.get("keyword", "") for s in steps]

        # thêm OPEN_URL
        if "OPEN_URL" not in keywords:
            steps.insert(0, {
                "keyword": "OPEN_URL",
                "locator": "",
                "value": base_url
            })

        # thêm CLOSE_BROWSER
        if "CLOSE_BROWSER" not in keywords:
            steps.append({
                "keyword": "CLOSE_BROWSER",
                "locator": "",
                "value": ""
            })

    return result


# ================= PROMPT =================
PROMPT = """
Bạn là chuyên gia kiểm thử phần mềm.

================ CHỦ ĐỀ HỆ THỐNG =================
{topic}

Hãy chuyển test case thành keyword-driven steps.

================ KEYWORDS =================
{keywords}

================ QUY TẮC CHỌN KEYWORD (RẤT QUAN TRỌNG) =================

Dựa vào Ý NGHĨA của step để chọn đúng keyword:

1. Nhập liệu (input):
→ dùng:
- INPUT_TEXT
- CLEAR_TEXT
- SEND_KEYS
- PRESS_ENTER

2. Click / thao tác:
→ dùng:
- CLICK
- DOUBLE_CLICK
- RIGHT_CLICK
- CLICK_JS

3. Chọn (dropdown):
→ dùng:
- SELECT_BY_TEXT
- SELECT_BY_VALUE
- SELECT_BY_INDEX

4. Điều hướng:
→ dùng:
- OPEN_URL
- GO_BACK
- REFRESH_PAGE

5. Kiểm tra hiển thị:
→ dùng:
- VERIFY_ELEMENT_VISIBLE
- VERIFY_ELEMENT_PRESENT

6. Kiểm tra nội dung cụ thể:
→ CHỈ dùng khi Expected Output có TEXT RÕ RÀNG
→ dùng:
- VERIFY_ELEMENT_TEXT_EQUALS
- VERIFY_TEXT_CONTAINS

================ QUY TẮC BẮT BUỘC =================

- Nếu step là "nhập" → PHẢI dùng INPUT_TEXT
- Nếu step là "click" → PHẢI dùng CLICK
- Nếu step là "kiểm tra hiển thị" → dùng VERIFY_ELEMENT_VISIBLE
- Nếu step có thông báo cụ thể → PHẢI dùng VERIFY_ELEMENT_TEXT_EQUALS + value

QUAN TRỌNG:

- Nếu locator là dropdown/list (cbo, list, dropdown)
→ KHÔNG được dùng verify text
→ CHỈ dùng VERIFY_ELEMENT_VISIBLE

- Nếu Expected Output KHÔNG có text cụ thể
→ KHÔNG được dùng VERIFY_ELEMENT_TEXT_EQUALS

- Nếu Expected Output CÓ text cụ thể
→ BẮT BUỘC phải:
  + dùng VERIFY_ELEMENT_TEXT_EQUALS
  + value = chính xác nội dung đó

================ YÊU CẦU =================
1. Chỉ được dùng keyword trong danh sách trên
2. Keyword phải EXACT với tên method
3. Không được tự tạo keyword mới
4. Không bỏ qua bước VERIFY
5. Locator phải lấy từ danh sách

6. PHẢI sinh dữ liệu THỰC (value)
   - Phù hợp với test case
   - Phù hợp với ngữ cảnh

7. Quy tắc dữ liệu:
   - valid → dữ liệu hợp lệ
   - invalid → dữ liệu sai
   - empty → ""
   - boundary → giá trị biên

8. KHÔNG dùng placeholder (<valid>, <invalid>...)

9. TẤT CẢ dữ liệu PHẢI liên quan đến CHỦ ĐỀ
   - Value phải là thực thể, từ khóa hoặc nội dung thuộc domain của hệ thống
   - Không được dùng dữ liệu chung chung hoặc không liên quan

10. KHÔNG được sử dụng dữ liệu thuộc domain khác
    - Ví dụ:
      Nếu hệ thống là ecommerce → không dùng dữ liệu về ngân hàng
      Nếu hệ thống là giáo dục → không dùng dữ liệu về sản phẩm

11. Dữ liệu phải có ý nghĩa thực tế với người dùng cuối
    - Không dùng chuỗi vô nghĩa như: "abc123", "qwerty"

================ LOCATORS =================
{locators}

Mỗi locator gồm:
- name: tên locator
- type: loại element (input, button, dropdown...)
- desc: mô tả chức năng

→ Chọn locator phù hợp nhất với step dựa trên desc và type
→ Không chọn sai locator

================ OUTPUT =================
[
  {{
    "test_case_id": "...",
    "steps": [
      {{
        "keyword": "...",
        "locator": "...",
        "value": "dữ liệu thực tế đúng chủ đề"
      }}
    ]
  }}
]

================ INPUT =================
Testcases:
{testcases}

Locators:
{locators}
"""


# ================= VALID KEYWORD =================
# lấy danh sách keyword hợp lệ
def get_all_valid_keywords():

    # Lấy tất cả function trong class KWCommon
    # và loại bỏ các hàm private
    return set([

        name

        for name, _ in inspect.getmembers(
            KWCommon,
            predicate=inspect.isfunction
        )

        if not name.startswith("_")
    ])


# ================= AUTO FIX KEYWORD =================
def auto_fix_keyword(step_text):

    keyword = extract_action(step_text)

    if keyword:
        return keyword

    return None


# ================= VALIDATE =================
def validate_and_fix(
        result,
        testcases,
        locator_context
):

    # Duyệt TC để mỗi TC AI được ghép với TC gốc tương ứng
    for tc, original_tc in zip(
            result,
            testcases
    ):
        # LẤY DATA TRONG 1 TESTCASE
        ai_steps = tc.get("steps", []) # step AI sinh ra
        raw_steps = original_tc.get("steps", []) # câu gốc
        expected_results = original_tc.get("expected_result", []) # expected output để validate VERIFY

        idx = 0

        # Duyệt từng step
        for step_obj in list(ai_steps):

            keyword = step_obj.get("keyword", "")

            # Bỏ qua step system
            if keyword in ["OPEN_URL", "CLOSE_BROWSER"]:
                continue

            if idx >= len(raw_steps):
                break

            # Lấy câu gốc để phân tích
            raw_step = raw_steps[idx]

            # FIX KEYWORD
            # CHUYỂN câu text (raw_step) → keyword
            old_kw = step_obj.get("keyword", "")
            new_kw = auto_fix_keyword(raw_step)

            if new_kw:
                if new_kw != old_kw:
                    print(f"[Fix Keyword] {old_kw} -> {new_kw} | step: {raw_step}")

                step_obj["keyword"] = new_kw #update lại
            else:
                new_kw = old_kw


            # BUILD LOCATOR TEXT: Tạo input cho semantic locator mapping
            locator_text = raw_step

            # Nếu là VERIFY thì Thêm expected_result vào context
            if "VERIFY" in new_kw and expected_results:
                locator_text += " " + " ".join(expected_results)


            # FIX LOCATOR
            # Lấy locator hiện tại
            old_locator = step_obj.get("locator", "")

            # danh sách hợp lệ
            valid_locator_names = {
                loc["name"] for loc in locator_context
            }

            # kiểm tra có cần sửa không
            need_fix_locator = (
                    not old_locator
                    or old_locator not in valid_locator_names
            )

            if need_fix_locator:
                # nếu cần fix
                new_locator = map_locator_semantic(
                    locator_text,
                    locator_context
                )

                if new_locator and new_locator != old_locator:
                    print(f"[Fix Locator] {old_locator} -> {new_locator} | step: {locator_text}")

                step_obj["locator"] = new_locator or old_locator


            # FIX VALUE CHO VERIFY TEXT
            # Chuẩn hoá expected text cho verify
            if new_kw in [
                "VERIFY_ELEMENT_TEXT_EQUALS",
                "VERIFY_TEXT_CONTAINS"
            ] and expected_results:

                # lấy expected
                expected_text = expected_results[0]

                # clean text để bỏ rác ngôn từ UI
                expected_text = (
                    expected_text
                    .replace("Hệ thống hiển thị", "")
                    .replace("xuất hiện", "")
                    .replace("thông báo", "")
                    .strip()
                    .strip('"')
                    .strip("'")
                )

                step_obj["value"] = expected_text

            # ==================================================
            # XOÁ VERIFY TRÙNG
            # ==================================================
            if new_kw in [
                "VERIFY_ELEMENT_TEXT_EQUALS",
                "VERIFY_TEXT_CONTAINS"
            ]:

                current_locator = step_obj.get("locator", "")
                current_value = str(step_obj.get("value", "")).strip()

                duplicated = False

                # kiểm tra toàn bộ step
                for other_step in list(ai_steps):

                    if other_step is step_obj:
                        continue

                    if (
                        other_step.get("keyword") == new_kw
                        and other_step.get("locator") == current_locator
                        and str(other_step.get("value", "")).strip() == current_value
                    ):
                        duplicated = True
                        break

                # nếu trùng
                if duplicated:
                    print(f"[REMOVE DUPLICATE VERIFY] {current_locator}")
                    ai_steps.remove(step_obj)
                    continue

            idx += 1 # chuyển sang step tiếp theo

    return result


# ================= MAIN =================
def generate_keyword_steps(
        testcases,
        locator_path,
        topic
):

    # load keyword docs
    keyword_docs = load_keywords_with_desc()

    keyword_str = "\n".join(
        keyword_docs
    )

    # load locator yaml
    with open(
            locator_path,
            "r",
            encoding="utf-8"
    ) as f:

        locators = yaml.safe_load(f)

    # ==================================================
    # BUILD LOCATOR CONTEXT
    # ==================================================
    locator_context = []

    for key, value in locators.items():

        locator_context.append({

            "name": key,

            "type": normalize_locator_name(
                key
            ),

            "semantic": value.get(
                "semantic",
                ""
            ),

            "by": value.get(
                "by",
                ""
            )
        })

    locators_str = json.dumps(
        locator_context,
        ensure_ascii=False,
        indent=2
    )

    # ==================================================
    # BUILD PROMPT
    # ==================================================
    prompt = PROMPT.format(

        keywords=keyword_str,

        testcases=json.dumps(
            testcases,
            indent=2,
            ensure_ascii=False
        ),

        locators=locators_str,

        topic=topic
    )

    # ==================================================
    # CALL AI
    # ==================================================
    raw = call_llm(prompt)

    print("===== RAW AI OUTPUT =====")
    print(raw)

    # parse JSON
    result = extract_json(raw)

    # inject setup / teardown
    result = inject_setup_teardown(
        result
    )

    # validate & fix
    result = validate_and_fix(
        result,
        testcases,
        locator_context
    )

    return result