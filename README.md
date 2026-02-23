# whisper-cpp-vulkan

Automated builds of [whisper.cpp](https://github.com/ggml-org/whisper.cpp) for Fedora 43, 44, and rawhide, with the Vulkan GPU backend enabled. Tracks upstream releases daily and rebuilds automatically.

## Features

- Vulkan backend enabled (`-DGGML_VULKAN=ON`) — runs on any Vulkan-capable GPU
- Curl support for model downloading
- Tracks upstream `vX.Y.Z` releases daily
- Builds for Fedora 43, 44, and rawhide simultaneously from a single SRPM

## Installation

```bash
sudo dnf copr enable YOUR_USERNAME/whisper-cpp-vulkan
sudo dnf install whisper-cpp
```

For the shared libraries only (e.g. for embedding):

```bash
sudo dnf install whisper-cpp-libs
```

## Usage

Download a model first:

```bash
whisper-cpp-download-model base.en
```

Available models: `tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large-v1`, `large-v2`, `large-v3`, `large-v3-turbo`

Models are saved to `~/.local/share/whisper-cpp/models/` (respects `XDG_DATA_HOME`).

Transcribe an audio or video file:

```bash
whisper-cli -m base.en file.wav
whisper-cli -m large-v3 file.mp4
```

The `-m` flag accepts either a short model name (e.g. `large-v3`) or a full path. Short names resolve to `~/.local/share/whisper-cpp/models/ggml-<name>.bin` automatically. FFmpeg support is built in, so MP4, Opus, AAC, and other formats work directly.

## GitHub Actions Setup

### 1. Create a COPR project

Go to https://copr.fedorainfracloud.org and create a project named `whisper-cpp-vulkan`.

When creating the project, enable these chroots:
- `fedora-43-x86_64`
- `fedora-44-x86_64`
- `fedora-rawhide-x86_64`

**Important:** In the project settings, enable **"Follow Fedora branching"**. This makes COPR automatically add the next Fedora chroot (e.g. `fedora-45-x86_64`) when rawhide branches. You then only need to add the new version to `CHROOTS` in `build.yml` to start explicitly targeting it.

### 2. Get a COPR API token

Go to https://copr.fedorainfracloud.org/api/ and copy your credentials.

### 3. Add GitHub Secrets

Add these to your repository (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `COPR_LOGIN` | Your COPR login token |
| `COPR_USERNAME` | Your COPR/Fedora username |
| `COPR_TOKEN` | Your COPR API token |

### 4. Workflow triggers

- **Daily** at 6 AM UTC — checks for new upstream releases
- **On push** to `whisper-cpp.spec` or workflow files — rebuilds with spec changes
- **Manually** via workflow_dispatch (with optional force build)

## Local Build (Vulkan)

```bash
# Install build dependencies
sudo dnf install rpm-build rpmdevtools wget python3

# Clone this repository
git clone https://github.com/YOUR_USERNAME/fedora-whispercpp.git
cd fedora-whispercpp

# Run the build script
./build.sh

# Upload the resulting SRPM to all chroots
copr-cli build whisper-cpp-vulkan whisper-cpp-*.src.rpm \
  --chroot fedora-43-x86_64 \
  --chroot fedora-44-x86_64 \
  --chroot fedora-rawhide-x86_64 \
  --nowait
```

## Build Dependencies (for local Vulkan builds)

```bash
sudo dnf install cmake gcc-c++ ninja-build vulkan-devel glslang shaderc libcurl-devel
```

## Upstream

- https://github.com/ggml-org/whisper.cpp
