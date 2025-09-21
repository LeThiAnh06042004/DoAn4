import pytest
from core.base_driver import BaseDriver


class BaseTest:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, request):
        """Khởi tạo và hủy driver cho mỗi test case"""
        driver_manager = BaseDriver()
        driver = driver_manager.get_driver()
        request.cls.driver = driver
        yield
        driver_manager.quit_driver()
