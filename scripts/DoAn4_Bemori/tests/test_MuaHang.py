import pytest
from utils import data_loader
from pages.OrderPage import OrderPage
from utils.config_loader import load_config

#nạp dữ liệu vào test
cases = data_loader.load_txt_data("D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_MuaHang.txt")

class TestComment:
#para.. chạy nhiều bộ dl khác nhau, case là 1 dict duy 1 trong cases khi mỗi vòng lặp test chạy, id là tên mô tả cho từng TC
    @pytest.mark.parametrize("case", cases, ids=[f"TEN='{c['ten']}', SDT='{c['sdt']}', DC='{c['dc']}', YC='{c['yc']}'" for c in cases])
    def test_comment(self, driver, case):
        ten = case["ten"]
        sdt = case["sdt"]
        dc = case["dc"]
        yc = case["yc"]

        #cb môi trg test
        config = load_config()
        driver.get(config["base_url"])
        page = OrderPage(driver)

        # Thao tác nhập liệu
        page.click_SP()
        page.click_MuaHang()
        page.nhapTen(ten)
        page.nhapSDT(sdt)
        page.nhapDC(dc)
        page.nhapYCThem(yc)
        page.click_Mua()


        # Lấy các thông báo hiển thị
        tb_thanh_cong = page.get_TBThanhCong()
        tb_nhapTen = page.get_TBNhapTen()
        tb_nhapSDT = page.get_TBNhapSDT()
        tb_nhapDC = page.get_TBNhapDC()
        tb_ChiCoSo = page.get_TBChiCoSo()
        tb_duoi10 = page.get_TB10So()
        tb_loi = page.get_Error()

        if ten == "":
            assert "Bạn chưa nhập họ và tên người mua." in tb_nhapTen, f"Thực tế: {tb_nhapTen}"
            assert "Bạn chưa nhập họ và tên người mua." in tb_loi, f"Thực tế: {tb_loi}"
        elif sdt == "":
            assert "Bạn chưa nhập số điện thoại người mua." in tb_nhapSDT, f"Thực tế: {tb_nhapSDT}"
            assert "Bạn chưa nhập số điện thoại người mua." in tb_loi, f"Thực tế: {tb_loi}"
        elif dc == "" and ten == "" and len(sdt) >= 10 and sdt.isdigit():
            assert "Bạn chưa nhập địa chỉ nhận hàng." in tb_nhapDC, f"Thực tế: {tb_nhapDC}"
            assert "Bạn chưa nhập địa chỉ nhận hàng." in tb_loi, f"Thực tế: {tb_loi}"
        elif not sdt.isdigit():
            assert "Số điện thoại chỉ bao gồm những số." in tb_ChiCoSo, f"Thực tế: {tb_ChiCoSo}"
            assert "Số điện thoại chỉ bao gồm những số." in tb_loi, f"Thực tế: {tb_loi}"
        elif len(sdt) < 10 and sdt.isdigit():
            assert "Số điện thoại phải có ít nhất 10 số." in tb_duoi10, f"Thực tế: {tb_duoi10}"
            assert "Số điện thoại phải có ít nhất 10 số." in tb_loi, f"Thực tế: {tb_loi}"
        else:
            assert "Cảm ơn bạn đã đặt hàng, vui lòng check lại đơn hàng trong messenger" in tb_thanh_cong, f"Thực tế: {tb_thanh_cong}"
            assert "Cảm ơn bạn đã đặt hàng, vui lòng check lại đơn hàng trong messenger" in tb_loi, f"Thực tế: {tb_loi}"



