import os
from datetime import datetime


class ReportManager:
    @staticmethod
    def create_report_folder():
        base_dir = "reports"
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        folder = os.path.join(base_dir, timestamp)
        os.makedirs(folder, exist_ok=True)
        return folder
