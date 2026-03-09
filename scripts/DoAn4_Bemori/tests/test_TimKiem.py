import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon

cases = data_loader.load_json_data(
    r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_TimKiem_json.json"
)

LOCATOR_FILE = r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\locators\TimKiem_locators.yaml"


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

        has_result = dispatcher.execute("VERIFY_ELEMENT_PRESENT", ["txtTimThay"])
        has_no_result = dispatcher.execute("VERIFY_ELEMENT_PRESENT", ["txtKoTimThay"])

        if has_result:
            print("→ Có kết quả tìm kiếm (combobox sắp xếp hiện)")
            assert True
        elif has_no_result:
            print("→ Không có sản phẩm (thông báo lỗi hiện)")
            assert True
        else:
            pytest.fail(f"Không xác định được kết quả cho keyword: {keyword}. Cả hai locator đều False.")