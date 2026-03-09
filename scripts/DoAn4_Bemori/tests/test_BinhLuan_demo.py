import pytest
from utils import data_loader
from utils.locator_reader import LocatorReader
from core.kw_dispatcher import KeywordDispatcher
from core.kw_common import KWCommon
from AI.keywords.kw.keyword_BinhLuan.BinhluanKeywords import BinhLuanKeywords

cases = data_loader.load_csv_data(
    r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_BinhLuan.csv"
)

LOCATOR_FILE = r"D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\locators\BinhLuan_locators.yaml"

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

        # Dispatcher cho KWCommon (action cơ bản)
        kw_common = KWCommon(driver, locator_reader=locator_reader)
        dispatcher_common = KeywordDispatcher(kw_common)

        # Dispatcher cho BinhLuanKeywords (verify chuyên biệt)
        kw_binhluan = BinhLuanKeywords(driver, locator_reader=locator_reader)
        dispatcher_binhluan = KeywordDispatcher(kw_binhluan)

        # ===== ACTION =====
        dispatcher_common.execute("OPEN_URL", ["https://gaubongonline.vn/"])
        dispatcher_common.execute("WAIT_FOR_ELEMENT_VISIBLE", ["txtSP", 10])
        dispatcher_common.execute("CLICK", ["txtSP"])

        dispatcher_common.execute("INPUT_TEXT", ["txtNoiDungBL", nd])
        dispatcher_common.execute("INPUT_TEXT", ["txtHoTen", ten])
        dispatcher_common.execute("INPUT_TEXT", ["txtSDT", sdt])
        dispatcher_common.execute("CLICK", ["btnBinhLuan"])

        # Chờ thông báo hiện
        dispatcher_common.execute("WAIT_FOR_SECONDS", [4])  # tăng lên 4 giây cho an toàn

        # ===== VERIFY =====
        if nd == "":
            assert dispatcher_binhluan.execute("VERIFY_EMPTY_COMMENT_ERROR"), \
                "Không thấy thông báo 'Bạn chưa nhập bình luận.'"

        elif ten == "":
            assert dispatcher_binhluan.execute("VERIFY_EMPTY_NAME_ERROR"), \
                "Không thấy thông báo 'Bạn chưa nhập tên.'"

        elif sdt == "":
            assert dispatcher_binhluan.execute("VERIFY_EMPTY_PHONE_ERROR"), \
                "Không thấy thông báo 'Bạn chưa nhập số điện thoại.'"

        elif not sdt.isdigit():
            assert dispatcher_binhluan.execute("VERIFY_PHONE_NON_DIGIT_CHARACTERS"), \
                "Không thấy thông báo 'Số điện thoại chỉ bao gồm những số.'"

        elif len(sdt) < 10:
            assert dispatcher_binhluan.execute("VERIFY_PHONE_MIN_LENGTH"), \
                "Không thấy thông báo 'Số điện thoại phải có ít nhất 10 số.'"

        else:
            assert dispatcher_binhluan.execute("SUBMIT_VALID_COMMENT_SUCCESS"), \
                "Không thấy thông báo 'Gửi bình luận thành công.'"
