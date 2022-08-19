%global modn c_icap

Summary:    An implementation of an ICAP server
Name:       c-icap
Version:    0.5.10
Release:    3%{?dist}
License:    LGPLv2+
URL:        http://%{name}.sourceforge.net/

Source0:    http://downloads.sourceforge.net/project/%{name}/%{name}/0.5.x/%{modn}-%{version}.tar.gz
Source1:    %{name}.logrotate
Source2:    %{name}.sysconfig
Source3:    %{name}.tmpfiles.conf
Source4:    %{name}.service
Patch0:     c-icap.conf.in.patch

BuildRequires:  bzip2-devel
BuildRequires:  brotli-devel
BuildRequires:  gcc
BuildRequires:  gdbm-devel
BuildRequires:  libdb-devel
BuildRequires:  make
BuildRequires:  openldap-devel
BuildRequires:  pcre-devel
BuildRequires:  perl-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  zlib-devel

Requires(pre):  shadow-utils

%description
C-icap is an implementation of an ICAP server. It can be used with HTTP proxies
that support the ICAP protocol to implement content adaptation and filtering
services. Most of the commercial HTTP proxies must support the ICAP protocol,
the open source Squid 3.x proxy server supports it too.

%package devel
Summary:     Development tools for %{name}
Requires:    %{name}-libs%{?_isa} = %{version}-%{release}
Requires:    zlib-devel

%description devel
The c-icap-devel package contains the static libraries and header files for
developing software using c-icap.

%package ldap
Summary:    The LDAP module for %{name}
Requires:   %{name} = %{version}-%{release}

%description ldap
The c-icap-ldap package contains the LDAP module for c-icap.

%package libs
Summary:    Libraries used by %{name}

%description libs
The c-icap-libs package contains all runtime libraries used by c-icap and the
utilities.

%package perl
Summary:    The Perl handler for %{name}
Requires:   %{name} = %{version}-%{release}

%description perl
The c-icap-perl package contains the Perl handler for c-icap.

%package bin
Summary:    Related programs for %{name}

%description bin
The c-icap-bin package contains several commandline tools for c-icap.

%prep
%autosetup -p1 -n %{modn}-%{version}

%build
%configure \
  --sysconfdir=%{_sysconfdir}/%{name} \
  --enable-shared \
  --disable-static \
  --enable-ipv6 \
  --enable-large-files \
  --enable-lib-compat \
  --with-bdb \
  --with-brotli \
  --with-ldap \
  --with-openssl \
  --with-perl \
  --with-zlib

%make_build

%install
%make_install

find %{buildroot} -name "*.la" -delete

mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_datadir}/%{modn}/{contrib,templates}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}

mv -f %{buildroot}%{_bindir}/%{name} %{buildroot}%{_sbindir}

install -D -p -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -D -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -D -p -m 0644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -D -p -m 0644 %{SOURCE4} %{buildroot}%{_unitdir}/%{name}.service

# Do not add default configuration files
rm -f %{buildroot}%{_sysconfdir}/%{name}/*.default

# Let rpm pick up the docs in the files section
rm -fr %{buildroot}%{_docdir}/%{name}

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null ||
    useradd -r -g %{name} -d /run/%{name} -s /sbin/nologin \
    -c "C-ICAP Service user" %{name}
exit 0

%if 0%{?rhel} == 7
%ldconfig_scriptlets libs
%endif

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%doc AUTHORS COPYING README TODO
%doc contrib/*.pl
%attr(750,root,%{name}) %dir %{_sysconfdir}/%{name}
%attr(640,root,%{name}) %config(noreplace) %{_sysconfdir}/%{name}/*.conf
%attr(640,root,%{name}) %config(noreplace) %{_sysconfdir}/%{name}/*.magic
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}.service
%dir %{_libdir}/%{modn}
%{_libdir}/%{modn}/bdb_tables.so
%{_libdir}/%{modn}/dnsbl_tables.so
%{_libdir}/%{modn}/shared_cache.so
%{_libdir}/%{modn}/srv_echo.so
%{_libdir}/%{modn}/srv_ex206.so
%{_libdir}/%{modn}/sys_logger.so
%{_sbindir}/%{name}
%{_datadir}/%{modn}
%{_mandir}/man8/%{name}.8*
%attr(750,%{name},%{name}) %dir %{_localstatedir}/log/%{name}

%files devel
%{_bindir}/%{name}-config
%{_bindir}/%{name}-libicapapi-config
%{_includedir}/%{modn}
%{_libdir}/libicapapi.so
%{_mandir}/man8/%{name}-config.8*
%{_mandir}/man8/%{name}-libicapapi-config.8*

%files ldap
%{_libdir}/%{modn}/ldap_module.so

%files libs
%license COPYING
%{_libdir}/libicapapi.so.*

%files perl
%{_libdir}/%{modn}/perl_handler.so

%files bin
%{_bindir}/%{name}-client
%{_bindir}/%{name}-mkbdb
%{_bindir}/%{name}-stretch
%{_mandir}/man8/%{name}-client.8*
%{_mandir}/man8/%{name}-mkbdb.8*
%{_mandir}/man8/%{name}-stretch.8*

%changelog
* Fri Aug 19 2022 Simone Caronni <negativo17@gmail.com> - 0.5.10-3
- Clean up SPEC file, use packaging guidelines where possible and fix rpmlint
  issues.
- Drop hardcoded dependencies and use dynamic ones.
- Trim changelog.
- Do not add default configuration files to configuration directory.
- Add perl examples to documentation.
- Add brotli support.
- Rename sources files to something more readable.

* Sun Jul 10 2022 Frank Crawford <frank@crawford.emu.id.au> - 0.5.10-2
- Update spec file for autoremoval of autotool .la files

* Thu Oct 21 2021 Frank Crawford <frank@crawford.emu.id.au> - 0.5.10-1
- Update to 0.5.10

* Sat Sep 25 2021 Frank Crawford <frank@crawford.emu.id.au> - 0.5.9-1
- Update to 0.5.9

* Sun Mar 14 2021 Frank Crawford <frank@crawford.emu.id.au> - 0.5.8-2
- Cleaned up PID path entry from /var/run to /run for systemd

* Sun Mar 14 2021 Frank Crawford <frank@crawford.emu.id.au> - 0.5.8-1
- Update to 0.5.8
- Update tmpfile.d location and definitions
- Upgraded to latest Berkeley DB version
