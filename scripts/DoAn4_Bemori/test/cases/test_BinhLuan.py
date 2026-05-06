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

        dispatcher.execute("OPEN_URL", ["https://gaubongonline.vn/"])
        dispatcher.execute("WAIT_FOR_ELEMENT_VISIBLE", ["lnkSanPham", 10])
        dispatcher.execute("CLICK", ["lnkSanPham"])

        dispatcher.execute("INPUT_TEXT", ["txtNoiDungBinhLuan", nd])
        dispatcher.execute("INPUT_TEXT", ["txtHoTen", ten])
        dispatcher.execute("INPUT_TEXT", ["txtSoDienThoai", sdt])
        dispatcher.execute("CLICK", ["btnGuiBinhLuan"])

        dispatcher.execute("WAIT_FOR_SECONDS", [3])  # chờ 3 giây cho thông báo load

        if nd == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoNhapBinhLuan", "Bạn chưa nhập bình luận."]), \
                "Không thấy thông báo thiếu nội dung bình luận"

        elif ten == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoNhapTen", "Bạn chưa nhập tên."]), \
                "Không thấy thông báo thiếu họ tên"

        elif sdt == "":
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoNhapSoDienThoai", "Bạn chưa nhập số điện thoại."]), \
                "Không thấy thông báo thiếu số điện thoại"

        elif not sdt.isdigit():
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoSoDienThoaiChiCoSo", "Số điện thoại chỉ bao gồm những số."]), \
                "Không thấy thông báo SDT chỉ chứa số"

        elif len(sdt) < 10:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoSoDienThoai10so", "Số điện thoại phải có ít nhất 10 số."]), \
                "Không thấy thông báo SDT dưới 10 số"

        else:
            assert dispatcher.execute("VERIFY_TEXT_CONTAINS", ["lblThongBaoThanhCong", "Gửi bình luận thành công."]), \
                "Không thấy thông báo gửi bình luận thành công"