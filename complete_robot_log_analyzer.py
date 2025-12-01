import os
import json
from config import LOG_DIRECTORY, TEMP_REPORTS_DIRECTORY, REPORTS_DIRECTORY

class CompleteRobotLogAnalyzer:
    def __init__(self, log_directory=None):
        self.log_directory = log_directory or LOG_DIRECTORY

    def generate_integrated_report(self):
        # 简单假数据，后续再替换为真分析
        return {
            "summary": "Mock analysis summary",
            "log_directory": self.log_directory,
            "task_count": 0,
            "error_count": 0
        }

    def save_reports(self, temp_output_dir=None):
        temp_output_dir = temp_output_dir or TEMP_REPORTS_DIRECTORY
        os.makedirs(temp_output_dir, exist_ok=True)
        os.makedirs(REPORTS_DIRECTORY, exist_ok=True)

        report_data = self.generate_integrated_report()
        report_id = "report_mock_1"
        json_path = os.path.join(temp_output_dir, f"{report_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        # 同时在 reports/ 写入一个简单 txt
        txt_path = os.path.join(REPORTS_DIRECTORY, f"{report_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Mock report\n")
        return {
            "report_id": report_id,
            "json_path": json_path,
            "txt_path": txt_path
        }