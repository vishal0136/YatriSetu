from pathlib import Path
import json


class ValidationEngine:

    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.issues = []

    def add_issue(
        self,
        rule_id,
        severity,
        issue_type,
        description,
        **details
    ):
        issue = {
            "rule_id": rule_id,
            "severity": severity,
            "issue_type": issue_type,
            "description": description
        }

        if details:
            issue["details"] = details

        self.issues.append(issue)

    def get_status(self):
        return "PASS" if not self.issues else "FAIL"

    def create_report(
        self,
        total_records,
        valid_records,
        statistics=None
    ):

        if statistics is None:
            statistics = {}

        invalid_records = total_records - valid_records

        return {
            "dataset": self.dataset_name,

            "validation_status": self.get_status(),

            "total_records": total_records,

            "valid_records": valid_records,

            "invalid_records": invalid_records,

            "statistics": statistics,

            "issues": self.issues
        }

    def save_report(
        self,
        report,
        output_path
    ):

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                report,
                file,
                indent=4
            )

        print(
            f"Report saved to: {output_path}"
        )