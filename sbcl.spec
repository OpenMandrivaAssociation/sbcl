%define sbcl_shell /bin/bash

# threading support
%define threads 1
%{?_without_threads: %{expand: %%global threads 0}}

%define bootstrap 0
%{?_with_bootstrap: %{expand: %%global bootstrap 1}}

Name: 	 sbcl
Version: 1.0.37
Release: %mkrel 1
Summary: Steel Bank Common Lisp compiler and runtime system
License: BSD
Group:   Development/Other
URL:     http://sbcl.sourceforge.net/
Source0: http://prdownloads.sourceforge.net/sbcl/%{name}-%{version}-source.tar.bz2
#%if %{bootstrap}
#Source1: http://prdownloads.sourceforge.net/sbcl/%{name}-%{version}-x86-linux-binary.tar.bz2
#Source2: http://prdownloads.sourceforge.net/sbcl/%{name}-%{version}-x86-64-linux-binary.tar.bz2
#%endif
Source3: customize-target-features.lisp 
Patch1: sbcl-1.0.25-default-sbcl-home.patch
Patch2: sbcl-0.9.5-personality.patch
Patch3: sbcl-1.0.28-optflags.patch
Patch4: sbcl-0.9.17-LIB_DIR.patch
Patch5: sbcl-1.0.16-GNU_SOURCE.patch
# Allow override of contrib test failure(s)
Patch7: sbcl-1.0.2-permissive.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}

Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
# doc generation
BuildRequires: ghostscript
BuildRequires: texinfo
BuildRequires: time
%if ! %{bootstrap}
BuildRequires: sbcl
%endif

%description
Steel Bank Common Lisp (SBCL) is a Open Source development environment
for Common Lisp. It includes an integrated native compiler,
interpreter, and debugger.


%prep
%if %{bootstrap}
%ifarch x86_64
echo x86_64
%define sbcl_arch x86_64
%setup -a 2
%define dirbin %{name}-%{version}
%endif

%ifarch %{ix86}
echo ix86
%define sbcl_arch x86
%setup -a 1
%define dirbin %{name}-%{version}-%{sbcl_arch}-linux
%endif

mkdir sbcl-bootstrap
pushd %{dirbin}
INSTALL_ROOT=`pwd`/../sbcl-bootstrap %{?sbcl_shell} ./install.sh
popd
%else
%setup
%endif

%patch1 -p1 -b .default-sbcl-home
%patch2 -p1 -b .personality
%patch3 -p1 -b .optflags
%patch4 -p1 -b .LIB_DIR
%patch5 -p1 -b .GNU_SOURCE
%patch7 -p1 -b .permissive

%if %{threads}
install -m644 -p %{SOURCE3} ./customize-target-features.lisp
%endif

%build
%if %{bootstrap}
export SBCL_HOME=`pwd`/sbcl-bootstrap/lib/sbcl
export PATH=`pwd`/sbcl-bootstrap/bin:${PATH}
%endif

export DEFAULT_SBCL_HOME=%{_libdir}/sbcl
export RPM_OPT_FLAGS=$(echo %optflags | sed -e "s/-fomit-frame-pointer//")
sh make.sh

make -C doc/manual html info

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}{%{_bindir},%{_libdir},%{_mandir}}

unset SBCL_HOME 
export INSTALL_ROOT=%{buildroot}%{_prefix} 
export LIB_DIR=%{buildroot}%{_libdir} 
sh install.sh 

## Unpackaged files
rm -rf %{buildroot}%{_docdir}/sbcl
rm -f  %{buildroot}%{_infodir}/dir
# CVS crud 
find %{buildroot} -name CVS -type d | xargs rm -rf
find %{buildroot} -name .cvsignore | xargs rm -f
# 'test-passed' files from %%check
find %{buildroot} -name 'test-passed' | xargs rm -vf


%post
/sbin/install-info %{_infodir}/sbcl.info %{_infodir}/dir ||:
/sbin/install-info %{_infodir}/asdf.info %{_infodir}/dir ||:

%postun
/sbin/install-info --delete %{_infodir}/sbcl.info %{_infodir}/dir ||:
/sbin/install-info --delete %{_infodir}/asdf.info %{_infodir}/dir ||:

%pre
# min_bootstrap: We *could* check for only-on-upgrade, but why bother?   (-:
/sbin/install-info --delete %{_infodir}/sbcl.info %{_infodir}/dir >& /dev/null ||:
/sbin/install-info --delete %{_infodir}/asdf.info %{_infodir}/dir >& /dev/null ||:


%files
%defattr(-,root,root)
%doc BUGS COPYING README CREDITS NEWS TLA TODO
%doc STYLE PRINCIPLES
%{_bindir}/*
%{_libdir}/sbcl/
%{_mandir}/man?/*
%doc doc/manual/sbcl
%doc doc/manual/asdf
%{_infodir}/*

%clean
rm -rf %{buildroot}
