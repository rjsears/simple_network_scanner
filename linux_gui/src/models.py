"""Data models for network scanner"""
from dataclasses import dataclass
from enum import Enum
from typing import List


class HostStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"
    NETWORK = "NTWRK"
    BROADCAST = "BCAST"


class IPType(Enum):
    HOST = "HOST"
    NETWORK = "NETWORK"
    BROADCAST = "BROADCAST"


@dataclass
class IPInfo:
    ip: str
    ip_type: IPType
    ip_int: int


@dataclass
class HostResult:
    ip: str
    status: HostStatus
    hostname: str
    ip_int: int

    def __lt__(self, other):
        return self.ip_int < other.ip_int


@dataclass
class ScanRequest:
    start_ip: str
    host_count: int
    cidr: int
    ip_list: List[IPInfo]


def ip_to_int(ip: str) -> int:
    """Convert IP address string to integer."""
    parts = ip.split(".")
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def int_to_ip(num: int) -> str:
    """Convert integer to IP address string."""
    return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"


def get_ip_type(ip_int: int, cidr: int) -> IPType:
    """Determine if IP is network, broadcast, or host address."""
    if cidr >= 31:
        return IPType.HOST

    block_size = 1 << (32 - cidr)
    network = (ip_int // block_size) * block_size
    broadcast = network + block_size - 1

    if ip_int == network:
        return IPType.NETWORK
    elif ip_int == broadcast:
        return IPType.BROADCAST
    return IPType.HOST


def is_valid_ip(ip: str) -> bool:
    """Validate IP address format."""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except ValueError:
        return False


def generate_ip_list(start_ip: str, num_hosts: int, cidr: int) -> List[IPInfo]:
    """Generate list of IP addresses to scan."""
    if not is_valid_ip(start_ip):
        return []

    ip_list = []
    current = ip_to_int(start_ip)
    hosts_found = 0

    while hosts_found < num_hosts:
        if current > 0xFFFFFFFF:
            break

        ip_type = get_ip_type(current, cidr)
        ip_list.append(IPInfo(
            ip=int_to_ip(current),
            ip_type=ip_type,
            ip_int=current
        ))

        if ip_type == IPType.HOST:
            hosts_found += 1

        current += 1

    return ip_list


def create_scan_request(start_ip: str, host_count: str, cidr: str) -> ScanRequest | None:
    """Create a ScanRequest from user input, or None if invalid."""
    try:
        host_count_int = int(host_count)
        cidr_int = int(cidr)
    except ValueError:
        return None

    if host_count_int <= 0 or not (8 <= cidr_int <= 32):
        return None

    if not is_valid_ip(start_ip):
        return None

    ip_list = generate_ip_list(start_ip, host_count_int, cidr_int)
    if not ip_list:
        return None

    return ScanRequest(
        start_ip=start_ip,
        host_count=host_count_int,
        cidr=cidr_int,
        ip_list=ip_list
    )
