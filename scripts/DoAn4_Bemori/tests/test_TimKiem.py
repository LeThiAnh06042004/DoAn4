import pytest
from core.data_loader import DataLoader
from pages.home_page import HomePage


class TestSearch:

    @pytest.mark.parametrize("case", DataLoader.load_yaml("testdata.yaml")["search"]["valid_cases"])
    def test_search_success(self, driver, case):
        """
        Tìm kiếm từ khóa hợp lệ → tiêu đề kết quả chứa ít nhất một từ khóa
        """
        keyword = case["keyword"]

        driver.get("https://gaubongonline.vn/")
        page = HomePage(driver)
        page.nhap_tu_khoa(keyword)
        page.click_tim_kiem()

        results = page.get_search_results()
        assert results, f"Không tìm thấy sản phẩm nào cho keyword: {keyword}"

        words = keyword.lower().split()
        found = any(
            any(word in r.lower() for word in words)
            for r in results
        )
        assert found, f"Kết quả tìm kiếm không chứa từ khóa nào trong: {keyword}"

    @pytest.mark.parametrize("case", DataLoader.load_yaml("testdata.yaml")["search"]["invalid_cases"])
    def test_search_fail(self, driver, case):
        """
        Tìm kiếm từ khóa không hợp lệ → hiện thông báo 'không tìm thấy'
        """
        keyword = case["keyword"]

        driver.get("https://gaubongonline.vn/")
        page = HomePage(driver)
        page.nhap_tu_khoa(keyword)
        page.click_tim_kiem()

        message = page.get_no_result_message()
        assert "không tìm thấy" in message.lower(), \
            f"Không hiển thị thông báo mong đợi cho keyword: {keyword}"
