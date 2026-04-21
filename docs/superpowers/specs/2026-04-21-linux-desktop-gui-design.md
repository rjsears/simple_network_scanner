# Linux Desktop GUI Design

**Date:** 2026-04-21  
**Status:** Approved

## Overview

Build a Linux Ubuntu 25 desktop application for the Simple Network Host Scanner, matching the polish and visual identity of the existing macOS SwiftUI version while adding export and preset features.

## Technology Stack

| Component | Choice |
|-----------|--------|
| Framework | PySide6 (Qt6 for Python) |
| Language | Python 3.10+ |
| Styling | Qt Style Sheets (QSS) |
| Packaging | .deb package + AppImage |

## Visual Design

The Linux version matches the macOS app's visual identity:

- **Color Scheme:** Teal primary (#008c9e), teal accent (#4dc0cc)
- **Layout:** Card-based with rounded corners (16px radius) and subtle shadows
- **Background:** Tech grid overlay on map background image with gradient
- **Typography:** Monospace fonts throughout (system monospace)
- **Components:**
  - Header with title, author, and status indicator capsule
  - Controls card with labeled inputs and action buttons
  - Progress card with animated progress bar
  - Results table with sortable columns
  - Summary pills (clickable to filter)

## Features

### Core Features (matching macOS)

1. **Scan Parameters**
   - Start IP address input
   - Host count input
   - CIDR netmask input
   - Start Scan / Cancel buttons

2. **Progress Display**
   - Real-time progress bar
   - Scanned count / total count display
   - Status text (Idle / Scanning / Complete / Cancelled)

3. **Results Table**
   - IP address column
   - Status column (UP/DOWN/NTWRK/BCAST with colors)
   - Hostname column
   - Sortable by IP

4. **Summary & Filtering**
   - Clickable summary pills showing counts by status
   - Filter dialog to view hosts by status

5. **About Dialog**
   - Version info
   - Author info
   - GitHub link

### New Features (Linux-only)

6. **Export Results**
   - Export to CSV format
   - Export to JSON format
   - File save dialog

7. **Network Presets**
   - Save current scan configuration as named preset
   - Load preset to populate inputs
   - Delete presets
   - Stored in ~/.config/network-scanner/presets.json

## Architecture

### Project Structure

```
linux_gui/
├── src/
│   ├── main.py              # Entry point, app initialization
│   ├── app.py               # MainWindow class
│   ├── scanner.py           # NetworkScanner, threading logic
│   ├── models.py            # Data classes (HostResult, ScanRequest)
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── header.py        # HeaderWidget
│   │   ├── controls.py      # ControlsCard
│   │   ├── progress.py      # ProgressCard
│   │   ├── results.py       # ResultsTable
│   │   ├── summary.py       # SummaryCard with pills
│   │   └── background.py    # TechBackground with grid
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── about.py         # AboutDialog
│   │   ├── filter.py        # FilterDialog
│   │   ├── export.py        # ExportDialog
│   │   └── presets.py       # PresetsDialog
│   ├── presets.py           # Preset save/load logic
│   ├── export.py            # CSV/JSON export logic
│   └── styles.py            # QSS stylesheet constants
├── assets/
│   ├── app_icon.png         # Application icon
│   ├── app_icon.svg         # Vector version
│   └── map_background.png   # Background image
├── packaging/
│   ├── debian/
│   │   ├── control          # Package metadata
│   │   ├── postinst          # Post-install script
│   │   └── network-scanner.desktop
│   └── appimage/
│       ├── AppRun
│       └── network-scanner.desktop
├── requirements.txt
├── build_deb.sh
├── build_appimage.sh
└── README.md
```

### Key Classes

**MainWindow (app.py)**
- Composes all widgets
- Manages scan state
- Coordinates signals between components

**NetworkScanner (scanner.py)**
- Runs in QThread for non-blocking UI
- Emits progress and result signals
- Handles parallel ping using ThreadPoolExecutor
- Performs reverse DNS lookups

**Data Models (models.py)**
- `HostResult`: IP, status, hostname, sort key
- `ScanRequest`: start IP, count, CIDR, generated IP list
- `HostStatus`: Enum (UP, DOWN, NETWORK, BROADCAST)

### Styling Approach

Single QSS stylesheet applied at app level with:
- Custom properties for color palette
- Widget-specific selectors
- Hover/pressed states for buttons
- Table alternating row colors

## Packaging

### .deb Package
- Target: Ubuntu 24.04+ / Debian 12+
- Dependencies: python3, python3-pyside6
- Installs to /opt/network-scanner
- Creates /usr/share/applications desktop entry
- Build via dpkg-deb

### AppImage
- Self-contained with bundled Python + PySide6
- Built using python-appimage or linuxdeploy
- Single executable, no installation required
- Works on any Linux with glibc 2.31+

## Testing

- Manual testing on Ubuntu 25 desktop
- Verify all features work correctly
- Test both packaging formats
- Verify desktop integration (icon, menu entry)

## Success Criteria

1. App launches and displays correctly on Ubuntu 25
2. Visual design matches macOS version's aesthetic
3. All scan functionality works (ping, DNS, progress, results)
4. Export to CSV/JSON works correctly
5. Presets save/load correctly
6. Both .deb and AppImage packages install and run properly
