# import os
# import yaml
#
# from utils.action_extractor import extract_action
# from utils.data_binding_utils import normalize_key
#
#
# SETUP_TEARDOWN_KEYWORDS = {
#     "OPEN_URL",
#     "CLOSE_BROWSER"
# }
#
#
# VERIFY_KEYWORDS = {
#     "VERIFY_ELEMENT_TEXT_EQUALS",
#     "VERIFY_TEXT_CONTAINS",
#     "VERIFY_ELEMENT_VISIBLE",
#     "VERIFY_ELEMENT_PRESENT",
#     "VERIFY_URL",
#     "VERIFY_PAGE_TITLE"
# }
#
#
# LOCATOR_REQUIRED_KEYWORDS = {
#     "CLICK",
#     "DOUBLE_CLICK",
#     "RIGHT_CLICK",
#     "HOVER",
#     "INPUT_TEXT",
#     "CLEAR_TEXT",
#     "SEND_KEYS",
#     "PRESS_ENTER",
#     "UPLOAD_FILE",
#     "SELECT_BY_TEXT",
#     "SELECT_BY_VALUE",
#     "SELECT_BY_INDEX",
#     "CHECK_CHECKBOX",
#     "UNCHECK_CHECKBOX",
#     "SCROLL_TO_ELEMENT",
#     "DRAG_AND_DROP",
#     "CLICK_JS",
#     "FOCUS_ELEMENT",
#     "VERIFY_ELEMENT_TEXT_EQUALS",
#     "VERIFY_TEXT_CONTAINS",
#     "VERIFY_ELEMENT_VISIBLE",
#     "VERIFY_ELEMENT_PRESENT",
#     "WAIT_FOR_ELEMENT_VISIBLE",
#     "WAIT_FOR_ELEMENT_PRESENT",
#     "WAIT_FOR_ELEMENT_CLICKABLE"
# }
#
#
# VALUE_REQUIRED_KEYWORDS = {
#     "OPEN_URL",
#     "INPUT_TEXT",
#     "VERIFY_ELEMENT_TEXT_EQUALS",
#     "VERIFY_TEXT_CONTAINS"
# }
#
#
# WEIGHTS = {
#     "coverage": 0.20,
#     "completeness": 0.25,
#     "accuracy": 0.30,
#     "consistency": 0.10,
#     "execution_success_rate": 0.15
# }
#
#
# def percent(numerator, denominator):
#     if denominator == 0:
#         return 100.0
#
#     return round((numerator / denominator) * 100, 2)
#
#
# def get_status(score):
#     if score >= 90:
#         return "Đạt"
#     if score >= 80:
#         return "Cần xem lại"
#     return "Không đạt"
#
#
# def load_locator_names(locator_path):
#     if not locator_path or not os.path.exists(locator_path):
#         return set()
#
#     with open(locator_path, "r", encoding="utf-8") as f:
#         data = yaml.safe_load(f) or {}
#
#     return set(data.keys())
#
#
# def get_testcase_required_keywords(testcase):
#     required = []
#
#     for step in testcase.get("steps", []):
#         keyword = extract_action(step)
#
#         if not keyword:
#             continue
#
#         required.append({
#             "raw_step": step,
#             "keyword": keyword
#         })
#
#     return required
#
#
# def get_generated_runtime_steps(script):
#     return [
#         step for step in script.get("steps", [])
#         if step.get("keyword") not in SETUP_TEARDOWN_KEYWORDS
#     ]
#
#
# def find_script_by_testcase(keyword_steps, testcase, index):
#     tc_id = testcase.get("test_case_id", "")
#     path_id = testcase.get("path_id", "")
#
#     for script in keyword_steps:
#         if script.get("test_case_id") == tc_id:
#             return script
#
#         if script.get("path_id") == path_id:
#             return script
#
#     if index < len(keyword_steps):
#         return keyword_steps[index]
#
#     return None
#
#
# def check_step_executable(step, locator_names):
#     errors = []
#
#     keyword = step.get("keyword", "")
#     locator = step.get("locator", "")
#     value = step.get("value", "")
#
#     if keyword in LOCATOR_REQUIRED_KEYWORDS:
#         if not locator:
#             errors.append(f"{keyword}: thiếu locator")
#         elif locator not in locator_names:
#             errors.append(f"{keyword}: locator không tồn tại: {locator}")
#
#     if keyword in VALUE_REQUIRED_KEYWORDS:
#         if value is None or str(value).strip() == "":
#             errors.append(f"{keyword}: thiếu value")
#
#     return errors
#
#
# def evaluate_accuracy(generated_steps, locator_names):
#     if not generated_steps:
#         return 0.0, ["Không có generated steps"]
#
#     valid_count = 0
#     errors = []
#
#     for index, step in enumerate(generated_steps, start=1):
#         step_errors = check_step_executable(
#             step,
#             locator_names
#         )
#
#         if step_errors:
#             errors.extend([
#                 f"Step {index}: {err}"
#                 for err in step_errors
#             ])
#         else:
#             valid_count += 1
#
#     return percent(valid_count, len(generated_steps)), errors
#
#
# def build_consistency_items(testcases, keyword_steps):
#     items = []
#
#     for index, testcase in enumerate(testcases):
#         script = find_script_by_testcase(
#             keyword_steps,
#             testcase,
#             index
#         )
#
#         if not script:
#             continue
#
#         required = get_testcase_required_keywords(testcase)
#         generated = get_generated_runtime_steps(script)
#
#         pair_count = min(
#             len(required),
#             len(generated)
#         )
#
#         for i in range(pair_count):
#             raw_step = required[i].get("raw_step", "")
#             generated_step = generated[i]
#
#             signature = normalize_key(raw_step)
#
#             items.append({
#                 "signature": signature,
#                 "keyword": generated_step.get("keyword", ""),
#                 "locator": generated_step.get("locator", "")
#             })
#
#     return items
#
#
# def evaluate_consistency(testcases, keyword_steps):
#     items = build_consistency_items(
#         testcases,
#         keyword_steps
#     )
#
#     if not items:
#         return 100.0, []
#
#     group_map = {}
#
#     for item in items:
#         signature = item.get("signature", "")
#
#         if not signature:
#             continue
#
#         group_map.setdefault(
#             signature,
#             []
#         ).append(item)
#
#     total_groups = 0
#     consistent_groups = 0
#     errors = []
#
#     for signature, group in group_map.items():
#         if len(group) < 2:
#             continue
#
#         total_groups += 1
#
#         first = group[0]
#         first_pair = (
#             first.get("keyword"),
#             first.get("locator")
#         )
#
#         is_consistent = True
#
#         for item in group[1:]:
#             current_pair = (
#                 item.get("keyword"),
#                 item.get("locator")
#             )
#
#             if current_pair != first_pair:
#                 is_consistent = False
#                 break
#
#         if is_consistent:
#             consistent_groups += 1
#         else:
#             errors.append(
#                 f"Không nhất quán mapping cho step: {signature}"
#             )
#
#     if total_groups == 0:
#         return 100.0, []
#
#     return percent(
#         consistent_groups,
#         total_groups
#     ), errors
#
#
# def evaluate_script_detail(
#         testcase,
#         script,
#         locator_names
# ):
#     required = get_testcase_required_keywords(testcase)
#
#     generated = (
#         get_generated_runtime_steps(script)
#         if script
#         else []
#     )
#
#     required_count = len(required)
#     generated_count = len(generated)
#
#     completeness = percent(
#         min(generated_count, required_count),
#         required_count
#     )
#
#     accuracy, accuracy_errors = evaluate_accuracy(
#         generated,
#         locator_names
#     )
#
#     has_verify = any(
#         step.get("keyword", "") in VERIFY_KEYWORDS
#         for step in generated
#     )
#
#     executable_errors = []
#
#     for index, step in enumerate(generated, start=1):
#         executable_errors.extend([
#             f"Step {index}: {err}"
#             for err in check_step_executable(
#                 step,
#                 locator_names
#             )
#         ])
#
#     executable = len(executable_errors) == 0
#
#     detail_score = round(
#         (
#             completeness * 0.35
#             + accuracy * 0.45
#             + (100 if has_verify else 0) * 0.10
#             + (100 if executable else 0) * 0.10
#         ),
#         2
#     )
#
#     return {
#         "test_case_id": testcase.get("test_case_id", ""),
#         "path_id": testcase.get("path_id", ""),
#         "required_steps": required_count,
#         "generated_steps": generated_count,
#         "completeness": completeness,
#         "accuracy": accuracy,
#         "has_verify": has_verify,
#         "executable": executable,
#         "errors": accuracy_errors + executable_errors,
#         "score": detail_score,
#         "status": get_status(detail_score)
#     }
#
#
# def evaluate_test_script_quality(
#         execution_paths,
#         testcases,
#         keyword_steps,
#         locator_path,
#         execution_results=None
# ):
#     locator_names = load_locator_names(locator_path)
#
#     detail_report = []
#
#     for index, testcase in enumerate(testcases):
#         script = find_script_by_testcase(
#             keyword_steps,
#             testcase,
#             index
#         )
#
#         detail = evaluate_script_detail(
#             testcase,
#             script,
#             locator_names
#         )
#
#         detail_report.append(detail)
#
#     coverage = percent(
#         len(keyword_steps),
#         len(testcases)
#     )
#
#     completeness = percent(
#         sum(item.get("generated_steps", 0) for item in detail_report),
#         sum(item.get("required_steps", 0) for item in detail_report)
#     )
#
#     accuracy = percent(
#         sum(item.get("accuracy", 0) for item in detail_report),
#         len(detail_report) * 100
#     )
#
#     consistency, consistency_errors = evaluate_consistency(
#         testcases,
#         keyword_steps
#     )
#
#     if execution_results:
#         passed = sum(
#             1 for item in execution_results
#             if item.get("status") == "PASS"
#         )
#
#         execution_success_rate = percent(
#             passed,
#             len(execution_results)
#         )
#
#         execution_note = "Tính theo kết quả thực thi test script"
#     else:
#         executable_count = sum(
#             1 for item in detail_report
#             if item.get("executable")
#         )
#
#         execution_success_rate = percent(
#             executable_count,
#             len(detail_report)
#         )
#
#         execution_note = "Chưa có kết quả chạy thực tế, tạm tính theo khả năng thực thi tĩnh"
#
#     final_score = round(
#         coverage * WEIGHTS["coverage"]
#         + completeness * WEIGHTS["completeness"]
#         + accuracy * WEIGHTS["accuracy"]
#         + consistency * WEIGHTS["consistency"]
#         + execution_success_rate * WEIGHTS["execution_success_rate"],
#         2
#     )
#
#     summary_report = [
#         {
#             "metric": "Coverage",
#             "description": "Tỷ lệ test script được sinh so với tổng số test case",
#             "formula": "Generated Scripts / Total Test Cases",
#             "weight": 20,
#             "score": coverage,
#             "weighted_score": round(coverage * WEIGHTS["coverage"], 2),
#             "note": ""
#         },
#         {
#             "metric": "Completeness",
#             "description": "Tỷ lệ bước được sinh so với số bước cần có",
#             "formula": "Generated Steps / Required Steps",
#             "weight": 25,
#             "score": completeness,
#             "weighted_score": round(completeness * WEIGHTS["completeness"], 2),
#             "note": ""
#         },
#         {
#             "metric": "Accuracy",
#             "description": "Đánh giá tính hợp lệ của keyword, locator và value",
#             "formula": "Valid Generated Steps / Generated Steps",
#             "weight": 30,
#             "score": accuracy,
#             "weighted_score": round(accuracy * WEIGHTS["accuracy"], 2),
#             "note": ""
#         },
#         {
#             "metric": "Consistency",
#             "description": "Đánh giá sự nhất quán khi cùng một action xuất hiện nhiều lần",
#             "formula": "Consistent Mapping Groups / Repeated Mapping Groups",
#             "weight": 10,
#             "score": consistency,
#             "weighted_score": round(consistency * WEIGHTS["consistency"], 2),
#             "note": "\n".join(consistency_errors)
#         },
#         {
#             "metric": "Execution Success Rate",
#             "description": "Tỷ lệ script có khả năng thực thi hoặc chạy thành công",
#             "formula": "Executable or Passed Scripts / Generated Scripts",
#             "weight": 15,
#             "score": execution_success_rate,
#             "weighted_score": round(execution_success_rate * WEIGHTS["execution_success_rate"], 2),
#             "note": execution_note
#         },
#         {
#             "metric": "Final Score",
#             "description": "Điểm đánh giá tổng hợp",
#             "formula": "Weighted average of 5 metrics",
#             "weight": 100,
#             "score": final_score,
#             "weighted_score": final_score,
#             "note": get_status(final_score)
#         }
#     ]
#
#     return summary_report, detail_report