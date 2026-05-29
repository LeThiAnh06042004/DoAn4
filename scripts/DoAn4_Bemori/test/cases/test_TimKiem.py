import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon
import time

cases = data_loader.load_json_data(
    r"/resources/data/data_TimKiem_Bemori.yaml"
)

LOCATOR_FILE = r"/resources/locators/TimKiem_Bemori_locators.yaml"


class TestSearch:
    @pytest.mark.parametrize("case", cases, ids=[c["keyword"] for c in cases])
    def test_search(self, driver, case):
        keyword = case["keyword"]

        # Load locator từ YAML
        locator_reader = LocatorReader(LOCATOR_FILE)

        # Khởi tạo KWCommon chung
        kw = KWCommon(driver, locator_reader=locator_reader)
        dispatcher = KeywordDispatcher(kw)

        dispatcher.execute("OPEN_URL", ["https://gaubongonline.vn/"])
        dispatcher.execute("INPUT_TEXT", ["txtTimKiem", keyword])
        dispatcher.execute("CLICK", ["btnTimKiem"])

        timeout = 10
        poll = 0.5
        end_time = time.time() + timeout

        has_result = False
        has_no_result = False

        while time.time() < end_time:
            try:
                has_result = dispatcher.execute("VERIFY_ELEMENT_PRESENT", ["cboTimThay"])
            except:
                has_result = False

            try:
                has_no_result = dispatcher.execute("VERIFY_ELEMENT_PRESENT", ["lblKoTimThay"])
            except:
                has_no_result = False

            if has_result or has_no_result:
                break

            time.sleep(poll)

        print(f"DEBUG: has_result={has_result}, has_no_result={has_no_result}")

        if has_result:
            print("→ Có kết quả tìm kiếm (combobox sắp xếp hiện)")
            assert True
        elif has_no_result:
            print("→ Không có sản phẩm (thông báo lỗi hiện)")
            assert True
        else:
            pytest.fail(f"Không xác định được kết quả cho keyword: {keyword}. Cả hai locator đều False.")