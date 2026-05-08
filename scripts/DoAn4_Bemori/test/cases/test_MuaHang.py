import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon

cases = data_loader.load_txt_data(
    r"D:/Đồ án 4/DoAn4/scripts/DoAn4_Bemori/resources/data/data_MuaHang.txt"
)

LOCATOR_FILE = r"D:/Đồ án 4/DoAn4/scripts/DoAn4_Bemori/resources/locators/MuaHang_locators.yaml"


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

        dispatcher.execute("WAIT_FOR_ELEMENT_VISIBLE", ["txtSP", 10])

        dispatcher.execute("CLICK", ["txtSP"])

        dispatcher.execute("CLICK", ["btnMuaHang"])

        dispatcher.execute("INPUT_TEXT", ["txtTenNM", ten])

        dispatcher.execute("INPUT_TEXT", ["txtSDT_NM", sdt])

        dispatcher.execute("INPUT_TEXT", ["txtDiaChiNH", dc])

        dispatcher.execute("INPUT_TEXT", ["txtYCThem", yc])

        dispatcher.execute("CLICK", ["btnMua"])

        # ===== VALIDATION =====

        if ten == "":

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["TBNhapTen", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["TBNhapTen", "Bạn chưa nhập họ và tên người mua."]
            ), "Không hiển thị lỗi thiếu họ tên người mua"

        elif sdt == "":

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["TBNhapSDT", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["TBNhapSDT", "Bạn chưa nhập số điện thoại người mua."]
            ), "Không hiển thị lỗi thiếu số điện thoại người mua"

        elif not sdt.isdigit():

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["TBChiCoSo", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["TBChiCoSo", "Số điện thoại chỉ bao gồm những số."]
            ), "Không hiển thị lỗi SDT chỉ gồm số"

        elif len(sdt) < 10:

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["TB10so", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["TB10so", "Số điện thoại phải có ít nhất 10 số."]
            ), "Không hiển thị lỗi SDT < 10 số"

        elif dc == "":

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["TBNhapDC", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["TBNhapDC", "Bạn chưa nhập địa chỉ nhận hàng."]
            ), "Không hiển thị lỗi thiếu địa chỉ nhận hàng"

        else:

            dispatcher.execute(
                "WAIT_FOR_ELEMENT_VISIBLE",
                ["TBThanhCong", 10]
            )

            assert dispatcher.execute(
                "VERIFY_TEXT_CONTAINS",
                ["TBThanhCong", "ng trong messenger."]
            ), "Đặt hàng không thành công"