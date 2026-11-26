#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APK="$ROOT/app/build/outputs/apk/debug/app-debug.apk"

if ! command -v adb >/dev/null 2>&1; then
    echo "adb not found. Install Android platform-tools first." >&2
    exit 1
fi

if [ ! -f "$APK" ]; then
    if [ -x "$ROOT/gradlew" ]; then
        "$ROOT/gradlew" :app:assembleDebug
    else
        gradle :app:assembleDebug
    fi
fi

adb wait-for-device
adb install -r "$APK"
echo "Installed. Apply the theme: Nova Launcher -> Settings -> Look & feel -> Icon theme -> Systema Theme"
