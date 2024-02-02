# Use %%bcond_with bootstrap to build sbcl with an existing sbcl package
%bcond_with bootstrap
%bcond_without docs
%bcond_with verbose

# disable docs if bootstrapping
%if %{with bootstrap}
%bcond_with docs
%endif

# default path
%global sb_prefix %{_libdir}/%{name}/contrib

%if %{with bootstrap}
%ifarch x86_64
%define sbcl_arch x86-64
%define sbcl_ver 2.3.6
%endif
%ifarch znver1
%define sbcl_arch x86-64
%define sbcl_ver 2.3.6
%endif
%ifarch aarch64
%define sbcl_arch arm64
%define sbcl_ver 1.4.2
%endif
%endif

Summary:	Steel Bank Common Lisp compiler and runtime system
Name:		sbcl
Version:	2.4.1
Release:	1
License:	Public Domain and MIT and BSD with advertising
Group:		Development/Other
URL:		https://sbcl.sourceforge.net/
Source0:	https://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{name}-%{version}-source.tar.bz2
%if %{with bootstrap}
Source50:	https://downloads.sourceforge.net/sourceforge/sbcl/%{name}-%{sbcl_ver}-%{sbcl_arch}-linux-binary.tar.bz2
%endif
Source10:	customize-target-features.lisp

Patch0:		%{name}-2.3.5-personality.patch
Patch1:		%{name}-2.3.5-optflags.patch
%if %{with verbose}
Patch2:		%{name}-2.3.5-verbose-build.patch
%endif
Patch3:		%{name}-2.3.5-LIB_DIR.patch

%if %{without bootstrap}
BuildRequires:	%{name}
%endif

BuildRequires:	ctags
BuildRequires: emacs-common
%if %{with docs}
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
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/%{name}.core
%{_libdir}/%{name}/%{name}.mk
%{_libdir}/%{name}/contrib/
%{_mandir}/man1/%{name}.1*
%if %{with docs}
%{_infodir}/*
%endif

#---------------------------------------------------------------------------

%prep
%autosetup -p1 %{?with_bootstrap:-b50}

# set version.lisp-expr
%if %{with bootstrap}
sed -i.-e "s|\"%{version}\"|\"%{version}-bootstrap\"|" version.lisp-expr
%else
sed -i.-e "s|\"%{version}\"|\"%{version}-%{vendor}\"|" version.lisp-expr
%endif

#if %{without bootstrap}
#install -m644 -p %{SOURCE10} ./customize-target-features.lisp
#endif

# fix lib path
sed -i 's|/lib/|/%{_lib}/|g' \
	install.sh \
	make-config.sh \
	contrib/sb-gmp/gmp.lisp \
	doc/cmu-user/extensions.tex \
	src/runtime/runtime.c \
	src/code/module.lisp \
	src/code/filesys.lisp \
	tests/install-test.sh \
	tests/install-test.sh \
	tests/pathnames.pure.lisp \
	%{nil}

%build
%set_build_flags
export SBCL_HOME=%{_libdir}/%{name}
export RPM_OPT_FLAGS=$(echo %{optflags} | sed -e "s/-fomit-frame-pointer//")
export CFLAGS="$RPM_OPT_FLAGS -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64"

%{?sbcl_arch:export SBCL_ARCH=%{sbcl_arch}}

#sh make-config.sh
sh make.sh \
	--prefix=%{_prefix} \
	--with-sb-core-compression \
	%{?with_bootstrap:--xc-host="../%{name}-%{sbcl_ver}-%{sbcl_arch}-linux/run-sbcl.sh"}

# docs
%if %{with docs}
%make_build -C doc/manual info
%endif

%install
INSTALL_ROOT=%{buildroot}%{_prefix} \
LIB_DIR=%{buildroot}%{_libdir} \
SBCL_HOME=%{buildroot}%{_libdir}/%{name} \
sh install.sh

if test %{_docdir} != %{_prefix}/share/doc ;then
	mkdir -p %{buildroot}/%{_docdir}
	mv %{buildroot}/%{_prefix}/share/doc/sbcl %{buildroot}/%{_docdir}/
fi

# remove unwanted stuff
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

%check

