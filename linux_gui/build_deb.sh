#!/bin/bash
set -e

VERSION="1.0.0"
PKG_NAME="network-scanner"
BUILD_DIR="build/deb"
INSTALL_DIR="$BUILD_DIR/$PKG_NAME/opt/network-scanner"

echo "Building .deb package..."

# Clean and create build directory
rm -rf "$BUILD_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$BUILD_DIR/$PKG_NAME/DEBIAN"
mkdir -p "$BUILD_DIR/$PKG_NAME/usr/share/applications"

# Copy application files
cp -r src "$INSTALL_DIR/"
cp -r assets "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp run.sh "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/run.sh"

# Copy desktop entry
cp packaging/debian/network-scanner.desktop "$BUILD_DIR/$PKG_NAME/usr/share/applications/"

# Create control file
cat > "$BUILD_DIR/$PKG_NAME/DEBIAN/control" << EOF
Package: network-scanner
Version: $VERSION
Section: net
Priority: optional
Architecture: all
Depends: python3 (>= 3.10), python3-pyside6
Maintainer: Richard J. Sears <richardjsears@protonmail.com>
Description: Simple Network Host Scanner
 A desktop application for scanning network hosts,
 identifying live systems, and performing reverse DNS lookups.
EOF

# Create postinst script
cat > "$BUILD_DIR/$PKG_NAME/DEBIAN/postinst" << 'EOF'
#!/bin/bash
chmod +x /opt/network-scanner/run.sh
EOF
chmod 755 "$BUILD_DIR/$PKG_NAME/DEBIAN/postinst"

# Build package
dpkg-deb --build "$BUILD_DIR/$PKG_NAME"
mv "$BUILD_DIR/$PKG_NAME.deb" "build/network-scanner_${VERSION}_all.deb"

echo "Package built: build/network-scanner_${VERSION}_all.deb"
