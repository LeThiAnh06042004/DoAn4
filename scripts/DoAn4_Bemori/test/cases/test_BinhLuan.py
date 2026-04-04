import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon

cases = data_loader.load_csv_data(
    r"D:/Đồ án 4/DoAn4/scripts/DoAn4_Bemori/resources/data/data_BinhLuan.csv"
)

LOCATOR_FILE = r"D:/Đồ án 4/DoAn4/scripts/DoAn4_Bemori/resources/locators/BinhLuan_locators.yaml"

class TestBinhLuan:
    @pytest.mark.parametrize(
        "case",
        cases,
        ids=[f"ND='{c['nd']}', TEN='{c['ten']}', SDT='{c['sdt']}'" for c in cases]
    )
    def test_binh_luan(self, driver, case):
        nd = case["nd"]
        ten = case["ten"]
        sdt = case["sdt"]

        locator_reader = LocatorReader(LOCATOR_FILE)
        kw = KWCommon(driver, locator_reader=locator_reader)
        dispatcher = KeywordDispatcher(kw)

        # ===== ACTION =====
        dispatcher.execute("OPEN_URL", ["https://gaubongonline.vn/"])
        dispatcher.execute("WAIT_FOR_ELEMENT_VISIBLE", ["txtSP", 10])
        dispatcher.execute("CLICK", ["txtSP"])

        dispatcher.execute("INPUT_TEXT", ["txtNoiDungBL", nd])
        dispatcher.execute("INPUT_TEXT", ["txtHoTen", ten])
        dispatcher.execute("INPUT_TEXT", ["txtSDT", sdt])
        dispatcher.execute("CLICK", ["btnBinhLuan"])

        # Chờ thông báo hiện (rất quan trọng!)
        dispatcher.execute("WAIT_FOR_SECONDS", [3])  # chờ 3 giây cho thông báo load

        # ===== VERIFY (kiểm tra thực tế trên trang) =====
        if nd == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBNhapBL", "Bạn chưa nhập bình luận."]), \
                "Không thấy thông báo thiếu nội dung bình luận"

        elif ten == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBNhapTen", "Bạn chưa nhập tên."]), \
                "Không thấy thông báo thiếu họ tên"

        elif sdt == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBNhapSDT", "Bạn chưa nhập số điện thoại."]), \
                "Không thấy thông báo thiếu số điện thoại"

        elif not sdt.isdigit():
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBChiCoSo", "Số điện thoại chỉ bao gồm những số."]), \
                "Không thấy thông báo SDT chỉ chứa số"

        elif len(sdt) < 10:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TB10so", "Số điện thoại phải có ít nhất 10 số."]), \
                "Không thấy thông báo SDT dưới 10 số"

        else:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["TBThanhCong", "Gửi bình luận thành công."]), \
                "Không thấy thông báo gửi bình luận thành công"