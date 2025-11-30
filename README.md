<h2 align="center">
  <a name="simple_network_scanner_logo" href="https://github.com/rjsears/simple_network_scanner"><img src="https://github.com/rjsears/simple_network_scanner/blob/main/images/netscan_logo.png?raw=true" alt="Simple Network Scanner" height="200" width="200"></a>
  <br>
  Simple Network Scanner (scan_network.py)
  </h2>
  <p align="center">
  A Python-based network scanning utility with a beautiful terminal interface
  </p>

<h4 align="center">Be sure to :star: my repo so you can keep up to date on any updates and progress!</h4>
<br>
<div align="center">
    <a href="https://github.com/rjsears/simple_network_scanner/commits/main"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/rjsears/simple_network_scanner?style=plastic"></a>
    <a href="https://github.com/rjsears/simple_network_scanner/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/rjsears/simple_network_scanner?style=plastic"></a>
    <a href="https://github.com/rjsears/simple_network_scanner/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-green?style=plastic"></a>
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/rjsears/simple_network_scanner?style=plastic">
    <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/rjsears/simple_network_scanner?style=plastic">
</div>
<br>
<p align="left"><font size="3">
Simple Network Scanner is a Python-based network scanning utility with a beautiful terminal interface. Scan IP ranges across any subnet size (/8 to /32), identify active hosts, and view results in a clean, color-coded table. The scanner is fully subnet-aware and correctly handles network and broadcast addresses across any CIDR netmask.
<br><br>
This project was born out of a need for a quick, visual network scanner that understood proper IP subnetting. Whether you're scanning a small /28 subnet or a large /16 network, Simple Network Scanner handles it correctly.
</p>
<br>

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Understanding Subnets](#understanding-subnets)
- [Output Reference](#output-reference)
- [Troubleshooting](#troubleshooting)
- [Acknowledgments](#acknowledgments)
- [License](#license)

<hr>

## Features

<ul>
<li><b>Subnet-Aware Scanning</b> - Supports any CIDR netmask from /8 to /32</li>
<li><b>Intelligent IP Handling</b> - Automatically identifies and skips network and broadcast addresses</li>
<li><b>Parallel Scanning</b> - Uses multithreading for fast scans (20 concurrent threads)</li>
<li><b>Reverse DNS Lookup</b> - Resolves hostnames for all scanned IPs (prioritizes /etc/hosts, falls back to DNS)</li>
<li><b>Beautiful Terminal UI</b> - Color-coded results with progress bar using the Rich library</li>
<li><b>Input Validation</b> - Validates IP addresses and netmask entries with helpful error messages</li>
<li><b>Network/Broadcast Identification</b> - Clearly marks NTWRK and BCAST addresses in results</li>
</ul>
<hr>

## Screenshots

<img src="https://github.com/rjsears/simple_network_scanner/blob/main/images/screenshot1.png" alt="Network Scanner Screenshot">

<hr>

## Requirements

- Python 3.6+
- macOS or Linux (uses native `ping` command)
- [Rich](https://github.com/Textualize/rich) library for terminal formatting

<hr>

## Installation

Clone the repository:
```bash
git clone https://github.com/rjsears/simple_network_scanner.git
cd simple_network_scanner
```

Install the required library:
```bash
pip install rich
```

Make it executable (optional):
```bash
chmod +x scan_network.py
```

<hr>

## Usage

Run the scanner:
```bash
python3 scan_network.py
```

You will be prompted for:
1. **Starting IP address** - The first IP to scan (e.g., `10.200.40.1`)
2. **Number of hosts** - How many valid host addresses to scan
3. **CIDR netmask** - The subnet mask (e.g., `24` for /24, `26` for /26)

### Example Session
```
Enter the starting IP address (e.g., 10.200.40.1):
➤ 10.200.40.1

Enter the number of hosts to scan:
➤ 50

Enter the CIDR netmask (e.g., 8, 16, 22, 23, 24, 25, 26, 27, 28):
➤ /24
```

<hr>

## Understanding Subnets

The scanner respects subnet boundaries based on the CIDR netmask you provide. This is **critical** for accurate scanning - without knowing the netmask, the scanner cannot determine which addresses are valid hosts versus network/broadcast addresses.

### Subnet Reference Table

| CIDR | Addresses per Subnet | Usable Hosts | Network/Broadcast Boundaries |
|------|---------------------|--------------|------------------------------|
| /8   | 16,777,216          | 16,777,214   | x.0.0.0 / x.255.255.255      |
| /16  | 65,536              | 65,534       | x.x.0.0 / x.x.255.255        |
| /22  | 1,024               | 1,022        | Every 4 in 3rd octet         |
| /23  | 512                 | 510          | Every 2 in 3rd octet         |
| /24  | 256                 | 254          | .0 / .255                    |
| /25  | 128                 | 126          | .0,.128 / .127,.255          |
| /26  | 64                  | 62           | Every 64 addresses           |
| /27  | 32                  | 30           | Every 32 addresses           |
| /28  | 16                  | 14           | Every 16 addresses           |
| /29  | 8                   | 6            | Every 8 addresses            |
| /30  | 4                   | 2            | Every 4 addresses            |
| /31  | 2                   | 2            | Point-to-point (both valid)  |
| /32  | 1                   | 1            | Single host                  |

### Example: Scanning with /26

If you start at `10.200.40.50` with 50 hosts and a /26 netmask:

- First /26 block: `10.200.40.0` (network), `.1-.62` (hosts), `.63` (broadcast)
- Your scan starts at `.50`, so it scans `.50-.62` (13 hosts)
- Then marks `.63` (broadcast) and `.64` (network)
- Continues with `.65-.126` (62 hosts) in the next /26 block
- And so on until 50 hosts are scanned

<hr>

## Output Reference

### Status Indicators

| Status | Color | Description |
|--------|-------|-------------|
| ● UP | Green | Host responded to ping |
| ● DOWN | Red (Yellow IP) | Host did not respond |
| ◆ NTWRK | Cyan | Network address (not pinged) |
| ◆ BCAST | Magenta | Broadcast address (not pinged) |

### IP Address Colors

| Color | Meaning |
|-------|---------|
| White | IP address that is UP |
| Yellow | IP address that is DOWN |
| Cyan | Network address |
| Magenta | Broadcast address |

### Summary Panel

The summary panel shows:
- **Hosts UP** - Number of hosts that responded
- **Hosts DOWN** - Number of hosts that did not respond
- **Network** - Number of network addresses encountered
- **Broadcast** - Number of broadcast addresses encountered
- **Total** - Total addresses in the scan

<hr>

## Troubleshooting

### "Permission denied" errors
Some systems require elevated privileges for ICMP ping. Try:
```bash
sudo python3 scan_network.py
```

### Slow scans
The scanner uses 20 parallel threads by default. If scanning across a slow network or VPN, results may take longer.

### No hostnames showing
Hostname resolution first checks `/etc/hosts` for a matching IP, then falls back to reverse DNS lookups. If neither has an entry for the IP, `-` is displayed. Make sure your `/etc/hosts` file has entries or your DNS server has PTR records configured.

### Rich library not found
Make sure you have installed the Rich library:
```bash
pip install rich
```

<hr>

## Acknowledgments

* **My Amazing and loving family!** My family puts up with all my coding and automation projects and encourages me in everything. Without them, my projects would not be possible.
* **My brother James**, who is a continual source of inspiration to me and others. Everyone should have a brother as awesome as mine!
* **[Rich](https://github.com/Textualize/rich)** - The fantastic Python library that makes beautiful terminal output possible.

<hr>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Richard J. Sears

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```