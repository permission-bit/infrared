#!/bin/bash

set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo
echo "========================================"
echo "          TestPyPI Release"
echo "========================================"
echo

command -v python >/dev/null 2>&1 || {
    echo "ERROR: python not found."
    exit 1
}

python -m build --version >/dev/null 2>&1 || {
    echo "ERROR: build is not installed."
    echo "Run: python -m pip install build"
    exit 1
}

python -m twine --version >/dev/null 2>&1 || {
    echo "ERROR: twine is not installed."
    echo "Run: python -m pip install twine"
    exit 1
}

# --------------------------------------------------
# Read package information
# --------------------------------------------------

PACKAGE_INFO=$(python - <<'PY'
import tomllib

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

print(data["project"]["name"])
print(data["project"]["version"])
PY
)

PACKAGE_NAME=$(echo "$PACKAGE_INFO" | sed -n '1p')
VERSION=$(echo "$PACKAGE_INFO" | sed -n '2p')

echo "Package : $PACKAGE_NAME"
echo "Version : $VERSION"

# --------------------------------------------------
# Check if version already exists on TestPyPI
# --------------------------------------------------

echo
echo "Checking TestPyPI..."

VERSION_EXISTS=$(python - "$PACKAGE_NAME" "$VERSION" <<'PY'
import json
import sys
import urllib.request

package = sys.argv[1]
version = sys.argv[2]

url = f"https://test.pypi.org/pypi/{package}/json"

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.load(response)

    print("yes" if version in data.get("releases", {}) else "no")

except Exception:
    print("unknown")
PY
)

if [[ "$VERSION_EXISTS" == "yes" ]]; then
    echo
    echo "Version $VERSION already exists on TestPyPI."
    echo "Nothing to upload."
    echo
    echo "Use this same version for the real PyPI release."
    exit 0
fi

if [[ "$VERSION_EXISTS" == "unknown" ]]; then
    echo "WARNING: Could not check TestPyPI."
fi

# --------------------------------------------------
# Clean
# --------------------------------------------------

echo
echo "Cleaning old builds..."

rm -rf build dist
find src -type d -name "*.egg-info" -prune -exec rm -rf {} +

# --------------------------------------------------
# Build
# --------------------------------------------------

echo
echo "Building $PACKAGE_NAME $VERSION..."

python -m build

# --------------------------------------------------
# Check
# --------------------------------------------------

echo
echo "Checking package..."

python -m twine check dist/*

# --------------------------------------------------
# Show files
# --------------------------------------------------

echo
echo "Files:"
ls -lh dist/

# --------------------------------------------------
# Confirmation
# --------------------------------------------------

echo
echo "========================================"
echo "Package : $PACKAGE_NAME"
echo "Version : $VERSION"
echo "Target  : TestPyPI"
echo "========================================"
echo

read -r -p "Upload $VERSION to TestPyPI? [y/N] " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

# --------------------------------------------------
# Upload
# --------------------------------------------------

echo
echo "Uploading $PACKAGE_NAME $VERSION to TestPyPI..."

python -m twine upload --repository testpypi dist/*

echo
echo "========================================"
echo "TestPyPI Release Successful!"
echo "========================================"
echo "Package : $PACKAGE_NAME"
echo "Version : $VERSION"
echo
echo "You can now test:"
echo
echo "pip install --index-url https://test.pypi.org/simple/ $PACKAGE_NAME"
echo