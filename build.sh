#!/bin/bash
# Local build script for whisper-cpp SRPM with Vulkan support
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"

echo "==> Fetching latest whisper.cpp release tag..."
TAG=$(curl -sf \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/ggml-org/whisper.cpp/releases/latest \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'])")

if [ -z "${TAG}" ]; then
  echo "Error: Could not determine latest release tag"
  exit 1
fi

echo "==> Latest release: ${TAG}"

mkdir -p "${BUILD_DIR}"
rpmdev-setuptree

echo "==> Downloading source tarball..."
wget "https://github.com/ggml-org/whisper.cpp/archive/refs/tags/${TAG}.tar.gz" \
  -O ~/rpmbuild/SOURCES/${TAG}.tar.gz

echo "==> Copying and versioning spec file..."
cp "${SCRIPT_DIR}/whisper-cpp.spec" ~/rpmbuild/SPECS/
sed -i "s/^Version:.*/Version:        ${TAG}/" ~/rpmbuild/SPECS/whisper-cpp.spec

echo "==> Building SRPM..."
rpmbuild -bs ~/rpmbuild/SPECS/whisper-cpp.spec

SRPM=$(ls -1t ~/rpmbuild/SRPMS/whisper-cpp-*.src.rpm | head -1)
echo "==> Created: ${SRPM}"
cp "${SRPM}" "${SCRIPT_DIR}/"

echo "==> Done! SRPM ready for COPR upload: ${SCRIPT_DIR}/$(basename ${SRPM})"
echo ""
echo "To upload manually:"
echo "  copr-cli build whisper-cpp-vulkan $(basename ${SRPM}) --chroot fedora-43-x86_64 --nowait"
