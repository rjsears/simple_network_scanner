#!/bin/bash
set -e

VERSION="1.0.0"
BUILD_DIR="build/appimage"
PYTHON_VERSION="3.11"

echo "Building self-contained AppImage..."

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Download python-appimage
if [ ! -f "python${PYTHON_VERSION}-appimage" ]; then
    echo "Downloading Python ${PYTHON_VERSION} AppImage base..."
    curl -Lo "python${PYTHON_VERSION}-appimage" \
        "https://github.com/niess/python-appimage/releases/download/python3.11/python${PYTHON_VERSION}.11-cp311-cp311-manylinux_2_28_x86_64.AppImage"
    chmod +x "python${PYTHON_VERSION}-appimage"
fi

# Extract the Python AppImage
echo "Extracting Python AppImage..."
./python${PYTHON_VERSION}-appimage --appimage-extract
mv squashfs-root NetworkScanner.AppDir

# Install PySide6 into the AppImage
echo "Installing PySide6..."
./NetworkScanner.AppDir/AppRun -m pip install --no-cache-dir PySide6

# Copy application files
echo "Copying application files..."
mkdir -p NetworkScanner.AppDir/opt/network-scanner
cp -r ../../src NetworkScanner.AppDir/opt/network-scanner/
cp -r ../../assets NetworkScanner.AppDir/opt/network-scanner/

# Create the launcher script
cat > NetworkScanner.AppDir/usr/bin/network-scanner << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")"
export PATH="${APPDIR}/usr/bin:${PATH}"
export PYTHONPATH="${APPDIR}/opt/network-scanner:${PYTHONPATH}"
cd "${APPDIR}/opt/network-scanner"
exec "${APPDIR}/AppRun" -m src.main "$@"
EOF
chmod +x NetworkScanner.AppDir/usr/bin/network-scanner

# Update AppRun to launch our app
cat > NetworkScanner.AppDir/AppRun << 'EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
export PATH="${APPDIR}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PYTHONHOME="${APPDIR}/usr"
export PYTHONPATH="${APPDIR}/opt/network-scanner:${PYTHONPATH}"
cd "${APPDIR}/opt/network-scanner"
exec "${APPDIR}/usr/bin/python${PYTHON_VERSION}" -m src.main "$@"
EOF
chmod +x NetworkScanner.AppDir/AppRun

# Update desktop file
cat > NetworkScanner.AppDir/network-scanner.desktop << EOF
[Desktop Entry]
Name=Network Scanner
Comment=Simple Network Host Scanner
Exec=network-scanner
Icon=network-scanner
Terminal=false
Type=Application
Categories=Network;Utility;
EOF
cp NetworkScanner.AppDir/network-scanner.desktop NetworkScanner.AppDir/usr/share/applications/

# Copy icon
cp ../../assets/app_icon.png NetworkScanner.AppDir/network-scanner.png
mkdir -p NetworkScanner.AppDir/usr/share/icons/hicolor/256x256/apps/
cp ../../assets/app_icon.png NetworkScanner.AppDir/usr/share/icons/hicolor/256x256/apps/network-scanner.png

# Download appimagetool
if [ ! -f "appimagetool" ]; then
    echo "Downloading appimagetool..."
    curl -Lo appimagetool \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool
fi

# Build the final AppImage
echo "Building final AppImage..."
ARCH=x86_64 ./appimagetool NetworkScanner.AppDir "../NetworkScanner-${VERSION}-x86_64.AppImage"

cd ..
echo ""
echo "AppImage built: build/NetworkScanner-${VERSION}-x86_64.AppImage"
