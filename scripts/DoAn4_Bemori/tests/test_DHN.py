import pytest
from utils import data_loader
from pages.QuickOrderPage import QuickOrderPage


cases = data_loader.load_json_data("D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_DatHangNhanh.json")

class TestSearch:

    @pytest.mark.parametrize("case", cases, ids=[c["sdt"] for c in cases] )# Đặt tên test theo sdt
    def test_search(self, driver, case):
        sdt = case["sdt"]

        driver.get("https://gaubongonline.vn/")
        page = QuickOrderPage(driver)
        page.click_SP()
        page.nhapDHN(sdt)
        page.click_Gui()

        tb_thanh_cong = page.get_TBThanhCong()
        tb_rong = page.get_TBrong()
        tb_chicoso = page.get_TBChiCoSo()
        tb_duoi10 = page.get_TBduoi10()

        if len(sdt) >= 10 and sdt.isdigit():
            assert "Cảm ơn bạn đã đặt hàng, vui lòng check lại đơn hàng trong messenger.\nGấu Bông Online sẽ hoàn thiện thông tin và cập nhật hành trình đơn hàng cho bạn qua messenger nha!" in tb_thanh_cong, f"Kết quả thực tế: {tb_thanh_cong}"
        elif sdt == "":
            assert "Bạn chưa nhập số điện thoại." in tb_rong,f"Kết quả thực tế: {tb_rong}"
        elif not sdt.isdigit():
            assert "Số điện thoại chỉ bao gồm những số." in tb_chicoso, f"Kết quả thực tế: {tb_chicoso}"
        elif len(sdt) < 10 and sdt.isdigit():
            assert "Số điện thoại phải có ít nhất 10 số." in tb_duoi10, f"Kết quả thực tế: {tb_duoi10}"
        else:
            pytest.fail(f"Không xác định được kết quả với dữ liệu: {sdt}")
