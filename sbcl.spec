%define _disable_lto 1

# Use %%bcond_with bootstrap to build sbcl with an existing sbcl package
%bcond_without bootstrap
%bcond_with docs

# disable docs if bootstrapping
%if %{with bootstrap}
%bcond_with docs
%endif

# default path
%global sb_prefix %{_libdir}/%{name}/contrib

%if %{with bootstrap}
%ifarch x86_64
%define sbcl_arch x86-64
%define sbcl_ver 1.4.7
%endif
%ifarch znver1
%define sbcl_arch x86-64
%define sbcl_ver 1.4.7
%endif
%ifarch aarch64
%define sbcl_arch arm64
%define sbcl_ver 1.4.2
%endif
%endif

Summary:	Steel Bank Common Lisp compiler and runtime system
Name:		sbcl
Version:	2.3.6
Release:	1
License:	Public Domain and MIT and BSD with advertising
Group:		Development/Other
URL:		https://sbcl.sourceforge.net/
Source0:	https://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{name}-%{version}-source.tar.bz2
%if %{with bootstrap}
Source50:	https://downloads.sourceforge.net/sourceforge/sbcl/%{name}-%{sbcl_ver}-%{sbcl_arch}-linux-binary.tar.bz2
%endif
Source10:	customize-target-features.lisp

#Patch1:	%{name}-2.3.5-default-%{name}-home.patch
Patch2:		%{name}-2.3.5-personality.patch
Patch3:		%{name}-2.3.5-optflags.patch
#Patch4		%{name}-2.3.5-verbose-build.patch
Patch5:		%{name}-2.3.5-LIB_DIR.patch

%if %{without bootstrap}
BuildRequires:	%{name}
#else
#BuildRequires:	clisp
%endif

BuildRequires:	ctags
%if %{without docs}
BuildRequires:	ghostscript
BuildRequires:	texinfo
BuildRequires:	texlive
BuildRequires:	texlive-collection-fontsrecommended
BuildRequires:	texlive-collection-langgerman
BuildRequires:	texlive-texinfo
%endif
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	time

%description
Steel Bank Common Lisp (SBCL) is a Open Source development environment for
Common Lisp. It includes an integrated native compiler, interpreter, and
debugger.

%files
%doc %{_docdir}/%{name}
%{_bindir}/*
%{_libdir}/%{name}/%{name}.core
%{_libdir}/%{name}/sbcl.mk
%dir %{sb_prefix}
#{sb_prefix}/sbcl.core
#{sb_prefix}/sbcl.mk
#{sb_prefix}/contrib/
%{sb_prefix}/asdf.*
%{sb_prefix}/sb-aclrepl.*
%{sb_prefix}/sb-bsd-sockets.*
%{sb_prefix}/sb-capstone.*
%{sb_prefix}/sb-cltl2.*
%{sb_prefix}/sb-concurrency.*
%{sb_prefix}/sb-cover.*
%{sb_prefix}/sb-executable.*
%{sb_prefix}/sb-gmp.*
%{sb_prefix}/sb-grovel.*
%{sb_prefix}/sb-introspect.*
%{sb_prefix}/sb-md5.*
%{sb_prefix}/sb-mpfr.*
%{sb_prefix}/sb-posix.*
%{sb_prefix}/sb-queue.*
%{sb_prefix}/sb-rotate-byte.*
%{sb_prefix}/sb-rt.*
%{sb_prefix}/sb-simd.*
%{sb_prefix}/sb-simple-streams.*
%{sb_prefix}/sb-sprof.*
%{sb_prefix}/uiop.*
%{_mandir}/man1/%{name}.1*
%{_infodir}/*

#---------------------------------------------------------------------------

%prep
%autosetup -p1 %{?with_bootstrap:-b50}

# set version.lisp-expr
%if %{with bootstrap}
sed -i.-e "s|\"%{version}\"|\"%{version}-%{vendor}\"|" version.lisp-expr
%else
sed -i.-e "s|\"%{version}\"|\"%{version}-bootstrap\"|" version.lisp-expr
%endif

# fix lib path
sed -i 's|../lib/sbcl|../%{_lib}/sbcl|' src/runtime/runtime.c

%if %{without bootstrap}
install -m644 -p %{SOURCE10} ./customize-target-features.lisp
%endif

%build
#setup SBCL_HOME, DEFAULT_SBCL_HOME and CFLAGS
#these variables are available thanks to patching
export SBCL_HOME=%{_libdir}/%{name}
#export DEFAULT_SBCL_HOME=%{_libdir}/%{name}}
export RPM_OPT_FLAGS=$(echo %{optflags} | sed -e "s/-fomit-frame-pointer//")
export CFLAGS="$RPM_OPT_FLAGS -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64"
%{?sbcl_arch:export SBCL_ARCH=%{sbcl_arch}}

sh make.sh \
	--prefix=%{_prefix} \
%if %{with bootstrap}
	--xc-host="../%{name}-%{sbcl_ver}-%{sbcl_arch}-linux/run-sbcl.sh"
%else
	--xc-host="sbcl --disable-debugger --no-sysinit --no-userinit"
%endif

# docs
%if %{with docs}
%make_build -C doc/manual info
%endif

%install
unset SBCL_HOME
export INSTALL_ROOT=%{buildroot}%{_prefix}
export LIB_DIR=%{buildroot}%{_libdir}
sh install.sh

#if test %{_docdir} != %{_prefix}/share/doc ;then
#	mkdir -p %{buildroot}/%{_docdir}
#	mv %{buildroot}/%{_prefix}/share/doc/sbcl %{buildroot}/%{_docdir}/
#fi

## Unpackaged files
rm -f %{buildroot}%{_infodir}/dir
# CVS crud
find %{buildroot} -name CVS -type d | xargs rm -rf
find %{buildroot} -name .cvsignore | xargs rm -f
find %{buildroot} -name .gitignore | xargs rm -f
# remove the a.out files
find %{buildroot} -name a\.out | xargs rm -f
# 'test-passed' files from %%check
find %{buildroot} -name 'test-passed' | xargs rm -vf
find %{buildroot} -name 'test-output' -type d | xargs rm -rf

# remove dangling texinfo files
find %{buildroot} -name *\.texinfo | xargs rm -f
# remove Makefiles
find %{buildroot} -name Makefile | xargs rm -f

