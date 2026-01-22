#!/usr/bin/env bash
set -euo pipefail

APP_NAME="NetworkTool"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$ROOT_DIR/build"
APP_DIR="$BUILD_DIR/$APP_NAME.app"
ICON_PATH="$ROOT_DIR/assets/AppIcon.icns"
BACKGROUND_PATH="$ROOT_DIR/assets/map_background.png"

mkdir -p "$BUILD_DIR"

SDK_PATH="$(xcrun --sdk macosx --show-sdk-path)"
ARM_TARGET="arm64-apple-macos12"
X86_TARGET="x86_64-apple-macos12"

swiftc \
  -O \
  -sdk "$SDK_PATH" \
  -target "$ARM_TARGET" \
  -framework SwiftUI \
  -framework AppKit \
  "$ROOT_DIR/Sources/NetworkToolApp.swift" \
  "$ROOT_DIR/Sources/NetworkScanner.swift" \
  -o "$BUILD_DIR/${APP_NAME}_arm64"

swiftc \
  -O \
  -sdk "$SDK_PATH" \
  -target "$X86_TARGET" \
  -framework SwiftUI \
  -framework AppKit \
  "$ROOT_DIR/Sources/NetworkToolApp.swift" \
  "$ROOT_DIR/Sources/NetworkScanner.swift" \
  -o "$BUILD_DIR/${APP_NAME}_x86_64"

lipo -create \
  "$BUILD_DIR/${APP_NAME}_arm64" \
  "$BUILD_DIR/${APP_NAME}_x86_64" \
  -output "$BUILD_DIR/$APP_NAME"

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

cp "$BUILD_DIR/$APP_NAME" "$APP_DIR/Contents/MacOS/"
cp "$ROOT_DIR/Info.plist" "$APP_DIR/Contents/"
if [[ -f "$ICON_PATH" ]]; then
  cp "$ICON_PATH" "$APP_DIR/Contents/Resources/AppIcon.icns"
fi
if [[ -f "$BACKGROUND_PATH" ]]; then
  cp "$BACKGROUND_PATH" "$APP_DIR/Contents/Resources/map_background.png"
fi

echo "Built $APP_DIR"
