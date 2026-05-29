import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon

cases = data_loader.load_json_data(
    r"/resources/data/data_DatHangNhanh_Bemori.json"
)

LOCATOR_FILE = r"/resources/locators/DatHangNhanh_Bemori_locators.yaml"

class TestDatHangNhanh:
    @pytest.mark.parametrize(
        "case",
        cases,
        ids=[c["sdt"] if c["sdt"] != "" else "EMPTY" for c in cases]
    )
    def test_dat_hang_nhanh(self, driver, case):
        sdt = case["sdt"]

        locator_reader = LocatorReader(LOCATOR_FILE)

        kw = KWCommon(driver, locator_reader=locator_reader)
        dispatcher = KeywordDispatcher(kw)

        dispatcher.execute("OPEN_URL", ["https://gaubongonline.vn/"])
        dispatcher.execute("WAIT_FOR_ELEMENT_VISIBLE", ["lnkSanPham", 10])
        dispatcher.execute("CLICK", ["lnkSanPham"])
        dispatcher.execute("INPUT_TEXT", ["txtDatHangNhanh", sdt])
        dispatcher.execute("CLICK", ["btnGui"])

        dispatcher.execute("WAIT_FOR_SECONDS", [3])

        if sdt == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoNhapSoDienThoai", "Bạn chưa nhập số điện thoại."]), \
                "Không hiển thị lỗi SĐT rỗng"

        elif not sdt.isdigit():
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoSoDienThoaiChiCoSo", "Số điện thoại chỉ bao gồm những số."]), \
                "Không hiển thị lỗi SĐT chỉ gồm số"

        elif len(sdt) < 10:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoSoDienThoai10so", "Số điện thoại phải có ít nhất 10 số."]), \
                "Không hiển thị lỗi SĐT < 10 số"

        else:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThanhCong", "ng trong messenger."]), \
                "Đặt hàng nhanh không thành công"