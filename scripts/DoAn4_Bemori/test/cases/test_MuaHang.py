import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon

cases = data_loader.load_txt_data(
    r"/resources/data/data_MuaHang_Bemori.txt"
)

LOCATOR_FILE = r"/resources/locators/MuaHang_Bemori_locators.yaml"


class TestMuaHang:

    @pytest.mark.parametrize(
        "case",
        cases,
        ids=[
            f"TEN='{c['ten']}', SDT='{c['sdt']}', DC='{c['dc']}', YC='{c['yc']}'"
            for c in cases
        ]
    )
    def test_mua_hang(self, driver, case):

        ten = case["ten"].strip()
        sdt = case["sdt"].strip()
        dc = case["dc"].strip()
        yc = case["yc"].strip()

        locator_reader = LocatorReader(LOCATOR_FILE)

        kw = KWCommon(driver, locator_reader=locator_reader)
        dispatcher = KeywordDispatcher(kw)

        dispatcher.execute("OPEN_URL", ["https://gaubongonline.vn/"])

        dispatcher.execute("WAIT_FOR_ELEMENT_VISIBLE", ["lnkSanPham", 10])

        dispatcher.execute("CLICK", ["lnkSanPham"])

        dispatcher.execute("CLICK", ["btnMuaHang"])

        dispatcher.execute("INPUT_TEXT", ["txtTenNguoiMua", ten])

        dispatcher.execute("INPUT_TEXT", ["txtSoDienThoaiNguoiMua", sdt])

        dispatcher.execute("INPUT_TEXT", ["txtDiaChiNhanHang", dc])

        dispatcher.execute("INPUT_TEXT", ["txtYeuCauThem", yc])

        dispatcher.execute("CLICK", ["btnMua"])

        # ===== VALIDATION =====

        if ten == "":

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["lblThongBaoNhapTen", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["lblThongBaoNhapTen", "Bạn chưa nhập họ và tên người mua."]
            ), "Không hiển thị lỗi thiếu họ tên người mua"

        elif sdt == "":

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["lblThongBaoNhapSoDienThoai", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["lblThongBaoNhapSoDienThoai", "Bạn chưa nhập số điện thoại người mua."]
            ), "Không hiển thị lỗi thiếu số điện thoại người mua"

        elif not sdt.isdigit():

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["lblThongBaoDienThoaiChiCoSo", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["lblThongBaoDienThoaiChiCoSo", "Số điện thoại chỉ bao gồm những số."]
            ), "Không hiển thị lỗi SDT chỉ gồm số"

        elif len(sdt) < 10:

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["lblThongBaoDienThoai10so", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["lblThongBaoDienThoai10so", "Số điện thoại phải có ít nhất 10 số."]
            ), "Không hiển thị lỗi SDT < 10 số"

        elif dc == "":

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["lblThongBaoNhapDiaChi", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["lblThongBaoNhapDiaChi", "Bạn chưa nhập địa chỉ nhận hàng."]
            ), "Không hiển thị lỗi thiếu địa chỉ nhận hàng"

        else:

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["lblThongBaoThanhCong", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["lblThongBaoThanhCong", "ng trong messenger."]
            ), "Đặt hàng không thành công"