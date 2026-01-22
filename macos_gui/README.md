# NetworkTool (macOS SwiftUI)

This folder contains a standalone SwiftUI macOS app that mirrors the behavior of the Python scanner.

## Build

From the repo root:

```bash
./macos_gui/build_icon.sh
./macos_gui/build_app.sh
```

The app bundle will be created at:

```
macos_gui/build/NetworkTool.app
```

## Notes

- Requires Xcode command line tools.
- Targets macOS 12.0+ for `Table` support.
- `build_icon.sh` uses macOS tools (`swift`, `sips`, `iconutil`) to generate a custom app icon.
