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

%build
%cmake \
    -DGGML_NATIVE=OFF \
    -DGGML_VULKAN=ON \
    -DWHISPER_CURL=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_RPATH=%{_privlibdir} \
    -G Ninja
%cmake_build

%install
%cmake_install

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
