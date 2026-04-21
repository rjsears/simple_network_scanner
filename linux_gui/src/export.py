"""Export functionality for scan results"""
import csv
import json
from typing import List

from .models import HostResult


def export_to_csv(results: List[HostResult], file_path: str):
    """Export results to CSV file."""
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["IP Address", "Status", "Hostname"])
        for result in sorted(results):
            writer.writerow([result.ip, result.status.value, result.hostname])


def export_to_json(results: List[HostResult], file_path: str):
    """Export results to JSON file."""
    data = {
        "scan_results": [
            {
                "ip": result.ip,
                "status": result.status.value,
                "hostname": result.hostname
            }
            for result in sorted(results)
        ],
        "summary": {
            "total": len(results),
            "up": sum(1 for r in results if r.status.value == "UP"),
            "down": sum(1 for r in results if r.status.value == "DOWN"),
            "network": sum(1 for r in results if r.status.value == "NTWRK"),
            "broadcast": sum(1 for r in results if r.status.value == "BCAST"),
        }
    }

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
