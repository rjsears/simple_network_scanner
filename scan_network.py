#!/usr/bin/env python3

# Simple IP Network Scanner
# Richard J. Sears
# richardjsears@gmail.com
# Version 1.0.0
# November 30th, 2025



import subprocess
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.panel import Panel
    from rich.text import Text
    from rich.live import Live
    from rich.layout import Layout
    from rich.align import Align
    from rich import box
except ImportError:
    print("Please install the 'rich' library: pip install rich")
    sys.exit(1)

console = Console(force_terminal=True, color_system="256")


def ping_host(ip: str) -> bool:
    """Ping a host and return True if it responds."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


def get_hostname(ip: str) -> str:
    """Get hostname for an IP address via reverse DNS."""
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return hostname
    except socket.herror:
        return "-"
    except Exception:
        return "-"


def scan_host(ip_info: dict) -> dict:
    """Scan a single host for status and hostname."""
    ip = ip_info["ip"]
    ip_type = ip_info["type"]

    # If it's a network or broadcast address, don't ping it
    if ip_type in ("NTWRK", "BCAST"):
        return {
            "ip": ip,
            "status": ip_type,
            "hostname": "-"
        }

    hostname = get_hostname(ip)
    is_up = ping_host(ip)
    return {
        "ip": ip,
        "status": "UP" if is_up else "DOWN",
        "hostname": hostname
    }


def display_banner():
    """Display the application banner."""
    banner_text = Align.center(Text("🌐  NETWORK HOST SCANNER  🌐", style="bold yellow"))

    banner = Panel(
        banner_text,
        subtitle="[bright_magenta]Python Edition[/bright_magenta]",
        border_style="bright_cyan",
        padding=(1, 2),
        width=76
    )
    console.print(banner)
    console.print()


def ip_to_int(ip: str) -> int:
    """Convert an IP address string to an integer."""
    parts = ip.split(".")
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def int_to_ip(num: int) -> str:
    """Convert an integer to an IP address string."""
    return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"


def get_ip_type(ip_int: int, cidr: int) -> str:
    """Determine if an IP is a network address, broadcast address, or host.
    Returns 'NTWRK', 'BCAST', or 'HOST'.
    """
    block_size = 2 ** (32 - cidr)
    network = (ip_int // block_size) * block_size
    broadcast = network + block_size - 1

    # Special cases for /31 and /32
    if cidr >= 31:
        return "HOST"

    if ip_int == network:
        return "NTWRK"
    elif ip_int == broadcast:
        return "BCAST"
    else:
        return "HOST"


def generate_ip_list(start_ip: str, num_hosts: int, cidr: int = 24) -> list:
    """Generate a list of IP addresses starting from start_ip for num_hosts count.
    Only counts valid HOST addresses toward num_hosts.
    Network and broadcast addresses are included but not counted.
    """
    ips = []
    block_size = 2 ** (32 - cidr)

    current_ip = ip_to_int(start_ip)
    hosts_found = 0

    while hosts_found < num_hosts:
        # Check for overflow
        if current_ip > 0xFFFFFFFF:
            break

        ip_type = get_ip_type(current_ip, cidr)
        ips.append({
            "ip": int_to_ip(current_ip),
            "type": ip_type
        })

        # Only count hosts toward our total
        if ip_type == "HOST":
            hosts_found += 1

        current_ip += 1

    return ips


def get_user_input() -> list:
    """Get the IP range from the user."""
    while True:
        console.print("[bright_yellow]Enter the starting IP address (e.g., 10.200.40.1):[/bright_yellow]")
        start_ip = console.input("[bright_green]➤ [/bright_green]").strip()

        # Validate full IP address format (4 octets)
        parts = start_ip.split(".")
        if len(parts) != 4:
            console.print(
                "[bright_red]❌ Invalid IP format. Please use format: x.x.x.x (4 octets required)[/bright_red]")
            console.print()
            continue

        # Validate each octet is a number between 0-255
        valid = True
        try:
            for i, part in enumerate(parts):
                num = int(part)
                if num < 0 or num > 255:
                    console.print("[bright_red]❌ Invalid IP format. Each octet must be between 0-255[/bright_red]")
                    console.print()
                    valid = False
                    break
        except ValueError:
            console.print("[bright_red]❌ Invalid IP format. Please use format: x.x.x.x[/bright_red]")
            console.print()
            continue

        if not valid:
            continue

        break

    while True:
        console.print()
        console.print("[bright_yellow]Enter the number of hosts to scan:[/bright_yellow]")
        try:
            num_hosts = int(console.input("[bright_green]➤ [/bright_green]").strip())
            if num_hosts < 1:
                console.print("[bright_red]❌ Number of hosts must be at least 1.[/bright_red]")
                continue
        except ValueError:
            console.print("[bright_red]❌ Invalid number. Please enter a numeric value.[/bright_red]")
            continue

        break

    while True:
        console.print()
        console.print(
            "[bright_yellow]Enter the CIDR netmask (e.g., 8, 16, 22, 23, 24, 25, 26, 27, 28):[/bright_yellow]")
        try:
            cidr = int(console.input("[bright_green]➤ /[/bright_green]").strip())
            if cidr < 8 or cidr > 32:
                console.print("[bright_red]❌ CIDR must be between 8 and 32.[/bright_red]")
                continue
        except ValueError:
            console.print("[bright_red]❌ Invalid CIDR. Please enter a number.[/bright_red]")
            continue

        break

    return generate_ip_list(start_ip, num_hosts, cidr)


def create_results_table(results: list) -> Table:
    """Create a rich table with the scan results."""
    table = Table(
        box=box.DOUBLE_EDGE,
        border_style="bright_cyan",
        header_style="bold white",
        show_lines=False,
        width=76
    )

    table.add_column("IP ADDRESS", width=17, justify="left")
    table.add_column("STATUS", width=10, justify="center")
    table.add_column("HOSTNAME", style="bright_white", width=45, justify="left")

    for result in results:
        if result["status"] == "UP":
            ip_text = Text(result["ip"], style="bright_white")
            status = Text("● UP", style="bold green")
        elif result["status"] == "DOWN":
            ip_text = Text(result["ip"], style="bright_yellow")
            status = Text("● DOWN", style="bold red")
        elif result["status"] == "NTWRK":
            ip_text = Text(result["ip"], style="bright_cyan")
            status = Text("◆ NTWRK", style="bold cyan")
        elif result["status"] == "BCAST":
            ip_text = Text(result["ip"], style="bright_magenta")
            status = Text("◆ BCAST", style="bold magenta")

        hostname = result["hostname"]
        if len(hostname) > 45:
            hostname = hostname[:42] + "..."

        table.add_row(ip_text, status, hostname)

    return table


def create_summary_panel(results: list) -> Panel:
    """Create a summary panel."""
    up_count = sum(1 for r in results if r["status"] == "UP")
    down_count = sum(1 for r in results if r["status"] == "DOWN")
    ntwrk_count = sum(1 for r in results if r["status"] == "NTWRK")
    bcast_count = sum(1 for r in results if r["status"] == "BCAST")
    total = len(results)

    summary = Text()
    summary.append("● Hosts UP:   ", style="bright_green")
    summary.append(f"{up_count}\n", style="bold bright_white")
    summary.append("● Hosts DOWN: ", style="bright_red")
    summary.append(f"{down_count}\n", style="bold bright_white")
    summary.append("◆ Network:    ", style="bright_cyan")
    summary.append(f"{ntwrk_count}\n", style="bold bright_white")
    summary.append("◆ Broadcast:  ", style="bright_magenta")
    summary.append(f"{bcast_count}\n", style="bold bright_white")
    summary.append("● Total:      ", style="bright_yellow")
    summary.append(f"{total}", style="bold bright_white")

    return Panel(
        summary,
        title="[bold bright_yellow]📈 SUMMARY[/bold bright_yellow]",
        border_style="bright_cyan",
        padding=(1, 2),
        width=76
    )


def main():
    console.clear()
    display_banner()

    ips = get_user_input()
    total = len(ips)

    # Count only actual hosts (not network/broadcast)
    host_count = sum(1 for ip in ips if ip["type"] == "HOST")

    # Get first and last IP for display
    first_ip = ips[0]["ip"]
    last_ip = ips[-1]["ip"]

    console.print()
    console.print(
        f"[bright_cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bright_cyan]")
    console.print(
        f"[bright_white]Scanning [bright_yellow]{first_ip}[/bright_yellow] to [bright_yellow]{last_ip}[/bright_yellow] ({host_count} hosts)[/bright_white]")
    console.print(
        f"[bright_cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bright_cyan]")
    console.print()

    results = []

    # Scan with progress bar and parallel execution
    with Progress(
            SpinnerColumn(spinner_name="dots12", style="bright_yellow"),
            TextColumn("[bright_white]{task.description}[/bright_white]"),
            BarColumn(bar_width=50, style="bright_blue", complete_style="bright_yellow", finished_style="bright_green"),
            TextColumn("[bright_magenta]{task.percentage:>3.0f}%[/bright_magenta]"),
            TimeElapsedColumn(),
            console=console
    ) as progress:
        task = progress.add_task("Scanning hosts...", total=total)

        # Use ThreadPoolExecutor for parallel scanning
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_ip = {executor.submit(scan_host, ip_info): ip_info for ip_info in ips}

            for future in as_completed(future_to_ip):
                result = future.result()
                results.append(result)
                progress.update(task, advance=1)

    # Sort results by IP address
    results.sort(key=lambda x: [int(p) for p in x["ip"].split(".")])

    console.print()

    # Display results banner and table
    banner_text = Text()
    banner_text.append(" " * 30, style="on white")
    banner_text.append("📊 ", style="on white")
    banner_text.append("SCAN RESULTS", style="bold black on white")
    banner_text.append(" " * 30, style="on white")
    console.print(banner_text)
    table = create_results_table(results)
    console.print(table)

    console.print()

    # Display summary
    summary = create_summary_panel(results)
    console.print(summary)

    console.print()
    console.print("[bold bright_green]✅ Scan complete![/bold bright_green]")
    console.print()


if __name__ == "__main__":
    main()