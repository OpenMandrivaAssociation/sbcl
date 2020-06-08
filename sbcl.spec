%define bootstrap 0
%define threads 1

Name:           sbcl
Version:        2.0.5
Release:        1
Summary:        Steel Bank Common Lisp compiler and runtime system
License:        Public Domain and MIT and BSD with advertising
Group:          Development/Other
URL:            http://sbcl.sourceforge.net/
Source0:        http://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{name}-%{version}-source.tar.bz2
Source10:       customize-target-features.lisp
Patch1:         %{name}-1.0.45-default-%{name}-home.patch
Patch2:         %{name}-1.1.14-personality.patch
Patch3:         %{name}-1.1.14-optflags.patch
Patch4:         %{name}-0.9.17-LIB_DIR.patch
# Allow override of contrib test failure(s)
Patch7:         %{name}-1.1.14-permissive.patch

# doc generation
BuildRequires:  ghostscript
BuildRequires:  gmp-devel
BuildRequires:  texinfo
BuildRequires:  texlive
BuildRequires:  time
%if %{bootstrap}
BuildRequires:  clisp
%else
BuildRequires:  %{name}
%endif

%description
Steel Bank Common Lisp (SBCL) is a Open Source development environment for
Common Lisp. It includes an integrated native compiler, interpreter, and
debugger.


%prep
%setup -q
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0
%patch7 -p0

%if %{threads}
install -m644 -p %{SOURCE10} ./customize-target-features.lisp
%endif

%build
#setup SBCL_HOME, DEFAULT_SBCL_HOME and RPM_OPT_FLAGS
#these variables are available thanks to patching
export SBCL_HOME=%{_libdir}/%{name}
export DEFAULT_SBCL_HOME=%{_libdir}/%{name}
export RPM_OPT_FLAGS=$(echo %{optflags} | sed -e "s/-fomit-frame-pointer//")

%if %{bootstrap}
sh make.sh "clisp"
%else
sh make.sh "%{name}"
%endif

make -C doc/manual

%install
unset SBCL_HOME
export INSTALL_ROOT=%{buildroot}%{_prefix}
export LIB_DIR=%{buildroot}%{_libdir}
sh install.sh

if test %{_docdir} != %{_prefix}/share/doc ;then
   mkdir -p %{buildroot}%{_docdir}
   mv %{buildroot}%{_prefix}/share/doc/%{name} %{buildroot}%{_docdir}/
fi

## Unpackaged files
rm -f  %{buildroot}%{_infodir}/dir
# CVS crud
find %{buildroot} -name CVS -type d | xargs rm -rf
find %{buildroot} -name .cvsignore | xargs rm -f
# 'test-passed' files from %%check
find %{buildroot} -name 'test-passed' | xargs rm -vf

%files
%doc %{_docdir}/%{name}
%{_bindir}/*
%{_libdir}/%{name}/%{name}.core
%define sb_prefix %{_libdir}/%{name}/contrib
%{sb_prefix}/asdf.*
%{sb_prefix}/sb-aclrepl.*
%{sb_prefix}/sb-bsd-sockets.*
%{sb_prefix}/sb-cltl2.*
%{sb_prefix}/sb-concurrency.*
%{sb_prefix}/sb-cover.*
%{sb_prefix}/sb-executable.*
%{sb_prefix}/sb-gmp.*
%{sb_prefix}/sb-grovel.*
%{sb_prefix}/sb-introspect.*
%{sb_prefix}/sb-md5.*
%{sb_prefix}/sb-posix.*
%{sb_prefix}/sb-queue.*
%{sb_prefix}/sb-rotate-byte.*
%{sb_prefix}/sb-rt.*
%{sb_prefix}/sb-simple-streams.*
%{sb_prefix}/sb-sprof.*
%{_infodir}/*
%{_mandir}/man?/*

