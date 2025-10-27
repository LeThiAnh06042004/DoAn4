import pytest
from utils import data_loader
from pages.home_page import HomePage

cases = data_loader.load_yaml_data("D:\Đồ án 4\DoAn4\scripts\DoAn4_Bemori\data\data_TimKiem.yaml")

class TestSearch:

    @pytest.mark.parametrize("case", cases, ids=[c["keyword"] for c in cases] )
    def test_search(self, driver, case):
        keyword = case["keyword"]

        driver.get("https://gaubongonline.vn/")
        page = HomePage(driver)
        page.nhap_tu_khoa(keyword)
        page.click_tim_kiem()

        if page.get_search_results():
            assert True
        elif page.get_no_result_message():
            assert True
        else:
            pytest.fail(f"Không xác định được kết quả cho keyword: {keyword}")
