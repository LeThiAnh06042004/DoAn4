import pytest
from utils import data_loader
from pages.CommentPage import CommentPage
from utils.config_loader import load_config

cases = data_loader.load_sqlite_data("D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_BinhLuan.sqlite", "BinhLuan")

class TestComment:

    @pytest.mark.parametrize("case", cases, ids=[f"ND='{c['nd']}', TEN='{c['ten']}', SDT='{c['sdt']}'" for c in cases])
    def test_comment(self, driver, case):
        noi_dung = case["nd"]
        ho_ten = case["ten"]
        so_dien_thoai = case["sdt"]

        config = load_config()
        driver.get(config["base_url"])
        page = CommentPage(driver)

        # Thao tác nhập liệu
        page.click_SP()
        page.nhapND(noi_dung)
        page.nhapHoTen(ho_ten)
        page.nhapSDT(so_dien_thoai)
        page.click_BinhLuan()

        # Lấy các thông báo hiển thị
        tb_thanh_cong = page.get_TBThanhCong()
        tb_nhapBL = page.get_TBNhapBL()
        tb_nhapTen = page.get_TBNhapTen()
        tb_nhapSDT = page.get_TBNhapSDT()
        tb_ChiCoSo = page.get_TBChiCoSo()
        tb_duoi10 = page.get_TB10So()

        # Kiểm tra điều kiện
        if noi_dung == "":
            assert "Bạn chưa nhập bình luận." in tb_nhapBL, f"Thực tế: {tb_nhapBL}"
        elif ho_ten == "":
            assert "Bạn chưa nhập tên." in tb_nhapTen, f"Thực tế: {tb_nhapTen}"
        elif so_dien_thoai == "":
            assert "Bạn chưa nhập số điện thoại." in tb_nhapSDT, f"Thực tế: {tb_nhapSDT}"
        elif not so_dien_thoai.isdigit():
            assert "Số điện thoại chỉ bao gồm những số." in tb_ChiCoSo, f"Thực tế: {tb_ChiCoSo}"
        elif len(so_dien_thoai) < 10:
            assert "Số điện thoại phải có ít nhất 10 số." in tb_duoi10, f"Thực tế: {tb_duoi10}"
        else:
            assert "Gửi bình luận thành công." in tb_thanh_cong, f"Thực tế: {tb_thanh_cong}"

