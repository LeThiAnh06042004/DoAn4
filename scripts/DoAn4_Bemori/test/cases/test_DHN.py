import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon

# Load data từ JSON
cases = data_loader.load_json_data(
    r"D:/Đồ án 4/DoAn4/scripts/DoAn4_Bemori/resources/data/data_DatHangNhanh.json"
)

LOCATOR_FILE = r"D:/Đồ án 4/DoAn4/scripts/DoAn4_Bemori/resources/locators/DatHangNhanh_locators.yaml"

class TestDatHangNhanh:
    @pytest.mark.parametrize(
        "case",
        cases,
        ids=[c["sdt"] if c["sdt"] != "" else "EMPTY" for c in cases]
    )
    def test_dat_hang_nhanh(self, driver, case):
        sdt = case["sdt"]

        # Load locator từ YAML
        locator_reader = LocatorReader(LOCATOR_FILE)

        # Khởi tạo KWCommon chung
        kw = KWCommon(driver, locator_reader=locator_reader)
        dispatcher = KeywordDispatcher(kw)

        # ===== ACTION =====
        dispatcher.execute("OPEN_URL", ["https://gaubongonline.vn/"])
        dispatcher.execute("WAIT_FOR_ELEMENT_VISIBLE", ["SP", 10])  # chờ sản phẩm visible
        dispatcher.execute("CLICK", ["SP"])  # click sản phẩm

        # Nhập số điện thoại
        dispatcher.execute("INPUT_TEXT", ["txtDHN", sdt])

        # Click gửi đặt hàng nhanh
        dispatcher.execute("CLICK", ["btnGui"])

        # Chờ thông báo hiện (rất quan trọng!)
        dispatcher.execute("WAIT_FOR_SECONDS", [3])  # chờ 3 giây cho thông báo load

        # ===== VERIFY (giữ nguyên rule của bạn) =====
        if sdt == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["txtTB_rong", "Bạn chưa nhập số điện thoại."]), \
                "Không hiển thị lỗi SĐT rỗng"

        elif not sdt.isdigit():
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["txtTB_chicoso", "Số điện thoại chỉ bao gồm những số."]), \
                "Không hiển thị lỗi SĐT chỉ gồm số"

        elif len(sdt) < 10:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["txtTB_duoi10", "Số điện thoại phải có ít nhất 10 số."]), \
                "Không hiển thị lỗi SĐT < 10 số"

        else:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["txtThanhCong", "ng trong messenger."]), \
                "Đặt hàng nhanh không thành công"