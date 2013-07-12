%define bootstrap 1
%define threads 1
# disabled until updated to work with newer texinfo
%bcond_with	docs

Name:           sbcl
Version:        1.1.3
Release:        1
Summary:        Steel Bank Common Lisp compiler and runtime system
License:        Public Domain and MIT and BSD with advertising
Group:          Development/Other
URL:            http://sbcl.sourceforge.net/
Source0:        http://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{name}-%{version}-source.tar.bz2
Source10:       customize-target-features.lisp 
Patch1:         %{name}-1.0.45-default-%{name}-home.patch
Patch2:         %{name}-0.9.5-personality.patch
Patch3:         %{name}-1.0.28-optflags.patch
Patch4:         %{name}-0.9.17-LIB_DIR.patch
Patch5:         %{name}-1.0.16-GNU_SOURCE.patch
Patch6:		%{name}-1.1.3-glibc-2.17.patch
# Allow override of contrib test failure(s)
Patch7:         %{name}-1.0.2-permissive.patch

#Requires(post): /sbin/install-info
#Requires(preun):/sbin/install-info
BuildRequires:  time
%if %{bootstrap}
BuildRequires:  clisp
%else
BuildRequires:  %{name}
%endif
%if %{with docs}
BuildRequires:  ghostscript
BuildRequires:  texinfo
BuildRequires:  texlive
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
%patch5 -p0
%patch6 -p1 -b .glibc217~
%patch7 -p0

%if %{threads}
install -m644 -p %{SOURCE10} ./customize-target-features.lisp
%endif

%build
#setup SBCL_HOME, DEFAULT_SBCL_HOME and RPM_OPT_FLAGS
#these variables are available thanks to patching
export SBCL_HOME=%{_libdir}/%{name}
export DEFAULT_SBCL_HOME=%{_libdir}/%{name}
export RPM_OPT_FLAGS=$(echo %optflags | sed -e "s/-fomit-frame-pointer//")

%if %{bootstrap}
sh make.sh "clisp"
%else
sh make.sh "%{name}"
%endif

%if %{with docs}
make -C doc/manual
%endif

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
%{_libdir}/%{name}/asdf-install/*
%{_libdir}/%{name}/asdf/*
%{_libdir}/%{name}/sb-aclrepl/*
%{_libdir}/%{name}/sb-bsd-sockets/*
%{_libdir}/%{name}/sb-cltl2/*
%{_libdir}/%{name}/sb-concurrency/*.fasl
%{_libdir}/%{name}/sb-concurrency/*.lisp
%{_libdir}/%{name}/sb-concurrency/*.texinfo
%{_libdir}/%{name}/sb-concurrency/*.asd
%{_libdir}/%{name}/sb-concurrency/tests/*
%{_libdir}/%{name}/sb-concurrency/Makefile
%{_libdir}/%{name}/sb-cover/*
%{_libdir}/%{name}/sb-executable/*
%{_libdir}/%{name}/sb-grovel/*
%{_libdir}/%{name}/sb-introspect/*
%{_libdir}/%{name}/sb-md5/*
%{_libdir}/%{name}/sb-posix/*
%{_libdir}/%{name}/sb-queue/*
%{_libdir}/%{name}/sb-rotate-byte/*
%{_libdir}/%{name}/sb-rt/*
%{_libdir}/%{name}/sb-simple-streams/*
%{_libdir}/%{name}/sb-sprof/*
%{_libdir}/%{name}/%{name}.*
%if %{with docs}
%{_infodir}/*
%endif
%{_mandir}/man?/*
