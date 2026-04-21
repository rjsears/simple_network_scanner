"""Network scanner with Qt threading support"""
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtCore import QObject, Signal, QThread

from .models import IPInfo, IPType, HostResult, HostStatus, ScanRequest


class NetworkScanner(QObject):
    """Performs network scanning operations."""

    progress_updated = Signal(int, int)  # current, total
    result_ready = Signal(HostResult)
    scan_complete = Signal()
    scan_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False

    def cancel(self):
        """Request scan cancellation."""
        self._cancelled = True

    def scan(self, request: ScanRequest):
        """Run the scan. Call from a worker thread."""
        self._cancelled = False
        total = len(request.ip_list)
        completed = 0

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {
                executor.submit(self._scan_host, ip_info): ip_info
                for ip_info in request.ip_list
            }

            for future in as_completed(futures):
                if self._cancelled:
                    executor.shutdown(wait=False, cancel_futures=True)
                    self.scan_cancelled.emit()
                    return

                result = future.result()
                self.result_ready.emit(result)
                completed += 1
                self.progress_updated.emit(completed, total)

        self.scan_complete.emit()

    def _scan_host(self, ip_info: IPInfo) -> HostResult:
        """Scan a single host."""
        if ip_info.ip_type == IPType.NETWORK:
            return HostResult(
                ip=ip_info.ip,
                status=HostStatus.NETWORK,
                hostname="-",
                ip_int=ip_info.ip_int
            )

        if ip_info.ip_type == IPType.BROADCAST:
            return HostResult(
                ip=ip_info.ip,
                status=HostStatus.BROADCAST,
                hostname="-",
                ip_int=ip_info.ip_int
            )

        is_up = self._ping_host(ip_info.ip)
        hostname = self._reverse_dns(ip_info.ip)

        return HostResult(
            ip=ip_info.ip,
            status=HostStatus.UP if is_up else HostStatus.DOWN,
            hostname=hostname,
            ip_int=ip_info.ip_int
        )

    def _ping_host(self, ip: str) -> bool:
        """Ping host and return True if it responds."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3
            )
            return result.returncode == 0
        except Exception:
            return False

    def _reverse_dns(self, ip: str) -> str:
        """Get hostname via reverse DNS lookup."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except (socket.herror, socket.gaierror):
            return "-"
        except Exception:
            return "-"


class ScannerThread(QThread):
    """Worker thread for running scans."""

    def __init__(self, scanner: NetworkScanner, request: ScanRequest, parent=None):
        super().__init__(parent)
        self.scanner = scanner
        self.request = request

    def run(self):
        self.scanner.scan(self.request)
