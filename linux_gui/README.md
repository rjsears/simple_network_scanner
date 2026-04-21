# Simple Network Scanner - Linux Desktop

A PySide6 desktop application for Ubuntu 25 (and other Linux distributions).

## Requirements

- Python 3.10+
- PySide6

## Installation

### From Source

```bash
cd linux_gui
pip install -r requirements.txt
python -m src.main
```

### From .deb Package (Ubuntu/Debian)

```bash
sudo dpkg -i network-scanner_1.0.0_all.deb
```

### From AppImage

```bash
chmod +x NetworkScanner-1.0.0-x86_64.AppImage
./NetworkScanner-1.0.0-x86_64.AppImage
```

## Building Packages

### Build .deb Package

```bash
./build_deb.sh
# Output: build/network-scanner_1.0.0_all.deb
```

### Build AppImage

```bash
./build_appimage.sh
# Output: build/NetworkScanner-1.0.0-x86_64.AppImage
```

## Features

- Network host scanning with parallel ping
- Reverse DNS hostname lookup
- Real-time progress display
- Results filtering by status
- Export to CSV/JSON
- Save/load scan presets

## License

MIT License - see LICENSE file in repository root.
