#!/bin/bash
set -e

VERSION="1.0.0"
BUILD_DIR="build/appimage"
APP_DIR="$BUILD_DIR/NetworkScanner.AppDir"

echo "Building AppImage..."

# Clean and create build directory
rm -rf "$BUILD_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy application files
cp -r src "$APP_DIR/usr/bin/"
cp -r assets "$APP_DIR/usr/bin/"
cp requirements.txt "$APP_DIR/usr/bin/"

# Copy desktop entry and icon
cp packaging/appimage/network-scanner.desktop "$APP_DIR/"
cp packaging/appimage/network-scanner.desktop "$APP_DIR/usr/share/applications/"
cp assets/app_icon.png "$APP_DIR/network-scanner.png"
cp assets/app_icon.png "$APP_DIR/usr/share/icons/hicolor/256x256/apps/network-scanner.png"

# Create AppRun
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:$PATH"
cd "${HERE}/usr/bin"
exec python3 -m src.main "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# Download appimagetool if needed
if [ ! -f "build/appimagetool" ]; then
    echo "Downloading appimagetool..."
    curl -Lo build/appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x build/appimagetool
fi

# Build AppImage
ARCH=x86_64 ./build/appimagetool "$APP_DIR" "build/NetworkScanner-${VERSION}-x86_64.AppImage"

echo "AppImage built: build/NetworkScanner-${VERSION}-x86_64.AppImage"
