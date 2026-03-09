import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon
from AI.keywords.kw.keyword_TimKiem.TimkiemKeywords import TimkiemKeywords  # Import class keyword chuyên biệt

cases = data_loader.load_json_data(
    r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_TimKiem_json.json"
)

LOCATOR_FILE = r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\locators\TimKiem_locators.yaml"

class TestSearch:
    @pytest.mark.parametrize("case", cases, ids=[c["keyword"] for c in cases])
    def test_search(self, driver, case):
        keyword = case["keyword"]

        locator_reader = LocatorReader(LOCATOR_FILE)

        # Dispatcher cho KWCommon: dùng cho các hành động cơ bản
        kw_common = KWCommon(driver, locator_reader=locator_reader)
        dispatcher_common = KeywordDispatcher(kw_common)

        # Dispatcher cho TimkiemKeywords: dùng cho các verify chuyên biệt
        kw_timkiem = TimkiemKeywords(driver, locator_reader=locator_reader)
        dispatcher_timkiem = KeywordDispatcher(kw_timkiem)

        # ===== ACTION =====
        dispatcher_common.execute("OPEN_URL", ["https://gaubongonline.vn/"])

        # Nhập từ khóa (dùng keyword cơ bản từ KWCommon, vì TimkiemKeywords chưa có INPUT_TEXT)
        dispatcher_common.execute("INPUT_TEXT", ["txtTimKiem", keyword])
        dispatcher_common.execute("CLICK", ["btnTimKiem"])

        # Kiểm tra combobox sắp xếp (có kết quả)
        has_result = dispatcher_timkiem.execute("VERIFY_SORT_COMBOBOX_DISPLAYED")
        if not has_result:  # fallback nếu method chưa implement
            has_result = dispatcher_common.execute("VERIFY_ELEMENT_PRESENT", ["txtTimThay"])

        # Kiểm tra thông báo không có kết quả
        has_no_result = dispatcher_timkiem.execute("VERIFY_NO_RESULTS_MESSAGE_SHOWN")
        if not has_no_result:  # fallback
            has_no_result = dispatcher_common.execute("VERIFY_TEXT_CONTAINS", ["txtKoTimThay", "Không tìm thấy"])

        if has_result:
            print("→ Có kết quả tìm kiếm (combobox sắp xếp hiện)")
            assert True
        elif has_no_result:
            print("→ Không có sản phẩm (thông báo lỗi hiện)")
            assert True
        else:
            pytest.fail(f"Không xác định được kết quả cho keyword: {keyword}. Cả hai locator đều False.")

        # Chụp ảnh màn hình cuối test để debug nếu fail
        dispatcher_common.execute("TAKE_SCREENSHOT", [f"screenshot_timkiem_{keyword.replace(' ', '_')}.png"])