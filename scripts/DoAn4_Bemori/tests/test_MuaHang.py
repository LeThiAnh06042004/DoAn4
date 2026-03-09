import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon

cases = data_loader.load_txt_data(
    r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_MH.txt"
)

LOCATOR_FILE = r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\locators\MuaHang_locators.yaml"

class TestMuaHang:
    @pytest.mark.parametrize(
        "case",
        cases,
        ids=[f"TEN='{c['ten']}', SDT='{c['sdt']}', DC='{c['dc']}', YC='{c['yc']}'" for c in cases]
    )
    def test_mua_hang(self, driver, case):
        ten = case["ten"]
        sdt = case["sdt"]
        dc = case["dc"]
        yc = case["yc"]

        # Load locator từ YAML
        locator_reader = LocatorReader(LOCATOR_FILE)

        # Khởi tạo KWCommon chung
        kw = KWCommon(driver, locator_reader=locator_reader)
        dispatcher = KeywordDispatcher(kw)

        # ===== ACTION =====
        dispatcher.execute("OPEN_URL", ["https://gaubongonline.vn/"])
        dispatcher.execute("WAIT_FOR_ELEMENT_VISIBLE", ["txtSP", 10])
        dispatcher.execute("CLICK", ["txtSP"])  # click sản phẩm

        dispatcher.execute("CLICK", ["btnMuaHang"])  # click "Mua hàng"

        # Nhập họ tên người mua
        dispatcher.execute("INPUT_TEXT", ["txtTenNM", ten])

        # Nhập số điện thoại người mua
        dispatcher.execute("INPUT_TEXT", ["txtSDT_NM", sdt])

        # Nhập địa chỉ nhận hàng
        dispatcher.execute("INPUT_TEXT", ["txtDiaChiNH", dc])

        # Nhập yêu cầu thêm
        dispatcher.execute("INPUT_TEXT", ["txtYCThem", yc])

        # Click xác nhận mua hàng
        dispatcher.execute("CLICK", ["btnMua"])

        # Chờ thông báo hiện (AJAX)
        dispatcher.execute("WAIT_FOR_SECONDS", [3])  # chờ 3 giây cho thông báo load

        # ===== VERIFY (giữ nguyên rule cũ của bạn) =====
        if ten == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBNhapTen", "Bạn chưa nhập họ và tên người mua."]), \
                "Không hiển thị lỗi thiếu họ tên người mua"

        elif sdt == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBNhapSDT", "Bạn chưa nhập số điện thoại người mua."]), \
                "Không hiển thị lỗi thiếu số điện thoại người mua"

        elif not sdt.isdigit():
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBChiCoSo", "Số điện thoại chỉ bao gồm những số."]), \
                "Không hiển thị lỗi SDT chỉ gồm số"

        elif len(sdt) < 10:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TB10so", "Số điện thoại phải có ít nhất 10 số."]), \
                "Không hiển thị lỗi SDT < 10 số"

        elif dc == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBNhapDC", "Bạn chưa nhập địa chỉ nhận hàng."]), \
                "Không hiển thị lỗi thiếu địa chỉ nhận hàng"

        else:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBThanhCong", "ng trong messenger."]), \
                "Đặt hàng không thành công"
