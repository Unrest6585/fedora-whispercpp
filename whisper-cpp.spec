# Version is set to the upstream release tag (e.g. v1.8.3) by the build workflow.
# For local builds, run build.sh which patches this line automatically.
%define version_no_v %(echo %{version} | sed 's/^v//')
%define _privlibdir %{_libdir}/%{name}

Name:           whisper-cpp
Version:        v0
Release:        1%{?dist}
Summary:        Speech-to-text inference engine in C/C++ with Vulkan GPU acceleration
License:        MIT
URL:            https://github.com/ggml-org/whisper.cpp
Source0:        https://github.com/ggml-org/whisper.cpp/archive/refs/tags/%{version}.tar.gz

BuildRequires:  cmake >= 3.14
BuildRequires:  gcc-c++
BuildRequires:  ninja-build
BuildRequires:  vulkan-devel
BuildRequires:  glslc
BuildRequires:  libcurl-devel
BuildRequires:  libavcodec-free-devel
BuildRequires:  libavformat-free-devel
BuildRequires:  libavutil-free-devel
BuildRequires:  libswresample-free-devel

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       vulkan-loader

%description
whisper.cpp is a high-performance inference implementation of OpenAI's Whisper
automatic speech recognition model, written in C/C++. This build enables the
Vulkan backend for GPU-accelerated inference on any Vulkan-capable GPU
(AMD, Intel, NVIDIA).

%package libs
Summary:        Shared libraries for %{name}
Requires:       vulkan-loader

%description libs
Shared libraries for whisper.cpp, including the Vulkan compute backend.
Installed to a private directory to avoid conflicts with other ggml consumers.

%prep
%autosetup -n whisper.cpp-%{version_no_v}

# Patch default model path: look in XDG_DATA_HOME first, then ~/.local/share
# Uses a C++ lambda so it works in any translation unit without extra headers
sed -i 's|"models/ggml-base.en.bin"|[]() -> std::string { auto x = getenv("XDG_DATA_HOME"); if (x \&\& x[0]) return std::string(x) + "/whisper-cpp/models/ggml-base.en.bin"; auto h = getenv("HOME"); if (h \&\& h[0]) return std::string(h) + "/.local/share/whisper-cpp/models/ggml-base.en.bin"; return "models/ggml-base.en.bin"; }().c_str()|g' \
  examples/cli/cli.cpp \
  examples/server/server.cpp \
  examples/bench/bench.cpp \
  examples/quantize/quantize.cpp \
  examples/vad-speech-segments/speech.cpp

# Patch upstream download script to default to XDG model directory
sed -i 's|*/bin) default_download_path="$PWD"|*/bin) default_download_path="${XDG_DATA_HOME:-$HOME/.local/share}/whisper-cpp/models"|' \
  models/download-ggml-model.sh
# Ensure model directory is created before cd
sed -i '/^cd "$models_path"/i mkdir -p "$models_path"' \
  models/download-ggml-model.sh

%build
%cmake \
    -DGGML_NATIVE=OFF \
    -DGGML_VULKAN=ON \
    -DWHISPER_CURL=ON \
    -DWHISPER_FFMPEG=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_RPATH=%{_privlibdir} \
    -G Ninja
%cmake_build

%install
%cmake_install

# Install upstream model download script
install -Dpm 0755 models/download-ggml-model.sh \
  %{buildroot}%{_bindir}/whisper-cpp-download-model

# Move all shared libraries to private directory to avoid conflicts with
# other ggml consumers (e.g. llama-cpp-libs) that ship the same libggml*.so
mkdir -p %{buildroot}%{_privlibdir}
mv %{buildroot}%{_libdir}/lib*.so.* %{buildroot}%{_privlibdir}/

# ld.so.conf drop-in so the dynamic linker finds our private libs
mkdir -p %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo %{_privlibdir} > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf

# Remove devel files (headers, cmake configs, unversioned .so symlinks, pkgconfig)
rm -rf %{buildroot}%{_includedir}
rm -rf %{buildroot}%{_libdir}/cmake
rm -rf %{buildroot}%{_libdir}/pkgconfig
rm -rf %{buildroot}/usr/lib/pkgconfig
find %{buildroot}%{_libdir} -name '*.so' -delete

# Remove test binaries not needed at runtime
rm -f %{buildroot}%{_bindir}/test-*

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%license LICENSE
%doc README.md
%{_bindir}/whisper-*

%files libs
%license LICENSE
%dir %{_privlibdir}
%{_privlibdir}/lib*.so.*
%{_sysconfdir}/ld.so.conf.d/%{name}.conf
