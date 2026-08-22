#!/bin/bash

set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo
echo "========================================"
echo "              PyPI Release"
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
# Check PyPI
# --------------------------------------------------

echo
echo "Checking PyPI..."

VERSION_EXISTS=$(python - "$PACKAGE_NAME" "$VERSION" <<'PY'
import json
import sys
import urllib.request

package = sys.argv[1]
version = sys.argv[2]

url = f"https://pypi.org/pypi/{package}/json"

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
    echo "ERROR:"
    echo "$PACKAGE_NAME $VERSION already exists on PyPI."
    echo
    echo "No version was changed."
    echo "Increase the version manually before releasing."
    exit 1
fi

if [[ "$VERSION_EXISTS" == "unknown" ]]; then
    echo
    echo "WARNING: Could not check PyPI."
    echo "Twine will perform the final validation."
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

echo
echo "Files:"
ls -lh dist/

# --------------------------------------------------
# VERY IMPORTANT confirmation
# --------------------------------------------------

echo
echo "========================================"
echo "             !!! REAL PYPI !!!"
echo "========================================"
echo
echo "Package : $PACKAGE_NAME"
echo "Version : $VERSION"
echo
echo "This will publish the package publicly."
echo

read -r -p "Type '$VERSION' to continue: " CONFIRM

if [[ "$CONFIRM" != "$VERSION" ]]; then
    echo
    echo "Cancelled."
    exit 0
fi

# --------------------------------------------------
# Upload
# --------------------------------------------------

echo
echo "Uploading $PACKAGE_NAME $VERSION to PyPI..."

if python -m twine upload dist/*; then

    echo
    echo "PyPI upload successful."

    # --------------------------------------------------
    # Calculate next development version
    # --------------------------------------------------

    NEXT_VERSION=$(python - "$VERSION" <<'PY'
import sys

parts = sys.argv[1].split(".")

if len(parts) != 3:
    raise SystemExit("Version must be MAJOR.MINOR.PATCH")

major, minor, patch = map(int, parts)

print(f"{major}.{minor}.{patch + 1}")
PY
)

    # --------------------------------------------------
    # Update pyproject.toml
    # --------------------------------------------------

    python - "$NEXT_VERSION" <<'PY'
from pathlib import Path
import re
import sys

path = Path("pyproject.toml")
text = path.read_text()

new_version = sys.argv[1]

new_text, count = re.subn(
    r'(?m)^version\s*=\s*"[^"]+"',
    f'version = "{new_version}"',
    text,
    count=1,
)

if count != 1:
    raise SystemExit(
        "Could not update version in pyproject.toml"
    )

path.write_text(new_text)
PY

    echo
    echo "========================================"
    echo "       PyPI Release Successful!"
    echo "========================================"
    echo
    echo "Published : $VERSION"
    echo "Next      : $NEXT_VERSION"
    echo
    echo "pyproject.toml is now:"
    echo "version = \"$NEXT_VERSION\""
    echo

else

    echo
    echo "========================================"
    echo "          PyPI Upload FAILED"
    echo "========================================"
    echo
    echo "Version remains:"
    echo "$VERSION"
    echo
    echo "pyproject.toml was NOT changed."
    exit 1
fi