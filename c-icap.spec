%define modn c_icap
%define name c-icap
%define ver  0.5.10

Summary         : An implementation of an ICAP server
Name            : %{name}
Version         : %{ver}
Release         : 2%{?dist}%{?pext}
License         : LGPLv2+
Group           : System Environment/Daemons
URL             : http://%{name}.sourceforge.net/
Source0         : http://downloads.sourceforge.net/project/%{name}/%{name}/0.5.x/%{modn}-%{ver}.tar.gz
Source1         : etc---logrotate.d---c-icap
Source2         : etc---sysconfig---c-icap.sysconfig
Source3         : usr---lib---tmpfiles.d---c-icap.conf
Source4         : usr---lib---systemd---system---c-icap.service
Patch0		: c-icap.conf.in.patch
Buildroot       : %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires        : %{name}-libs = %{version}-%{release}
Requires        : libdb zlib bzip2-libs pcre
Requires(pre)   : /usr/sbin/groupadd /usr/sbin/useradd
Requires(post)  : /bin/systemctl
Requires(preun) : /bin/systemctl
Requires(postun): /bin/systemctl
BuildRequires   : gdbm-devel openldap-devel perl-devel tar zlib-devel bzip2-devel pcre-devel
BuildRequires	: libdb-devel
BuildRequires	: gcc make
Vendor          : Tsantilas Christos <chtsanti@users.sourceforge.net>

%description
C-icap is an implementation of an ICAP server. It can be used with HTTP proxies
that support the ICAP protocol to implement content adaptation and filtering
services. Most of the commercial HTTP proxies must support the ICAP protocol,
the open source Squid 3.x proxy server supports it too.

%package devel
Summary         : Development tools for %{name}
Group           : Development/Libraries
Requires        : %{name}-libs = %{version}-%{release}
Requires        : zlib-devel

%description devel
The c-icap-devel package contains the static libraries and header files for
developing software using c-icap.

%package ldap
Summary         : The LDAP module for %{name}
Group           : System Environment/Libraries
Requires        : %{name} = %{version}-%{release}
Requires        : openldap

%description ldap
The c-icap-ldap package contains the LDAP module for c-icap.

%package libs
Summary         : Libraries used by %{name}
Group           : System Environment/Libraries

%description libs
The c-icap-libs package contains all runtime libraries used by c-icap and the
utilities.

%package perl
Summary         : The Perl handler for %{name}
Group           : System Environment/Libraries
Requires        : %{name} = %{version}-%{release}
Requires        : perl-libs

%description perl
The c-icap-perl package contains the Perl handler for c-icap.

%package bin
Summary         : Related programs for %{name}
Group           : Applications/Internet
Requires        : %{name}-libs = %{version}-%{release}

%description bin
The c-icap-bin package contains several commandline tools for c-icap.

%prep
%setup -q -n %{modn}-%{ver}
%patch0 -p 1

%build
LIBS="-lpthread"; export LIBS
%configure \
  LDFLAGS="" \
  CFLAGS="${RPM_OPT_FLAGS} -fno-strict-aliasing -I/usr/include/libdb" \
  --sysconfdir=%{_sysconfdir}/%{name}            \
  --enable-shared                                \
  --enable-static                                \
  --enable-large-files                           \
  --enable-lib-compat                            \
  --with-perl                                    \
  --with-zlib                                    \
  --with-bdb                                     \
  --with-ldap
  #--enable-ipv6 # net.ipv6.bindv6only not supported

%{__make} %{?_smp_mflags}

%install
[ -n "${RPM_BUILD_ROOT}" -a "${RPM_BUILD_ROOT}" != "/" ] && %{__rm} -rf ${RPM_BUILD_ROOT}
%{__mkdir_p} ${RPM_BUILD_ROOT}%{_sbindir}
%{__mkdir_p} ${RPM_BUILD_ROOT}%{_datadir}/%{modn}/{contrib,templates}
%{__mkdir_p} ${RPM_BUILD_ROOT}%{_localstatedir}/log/%{name}

%{__make} \
  DESTDIR=${RPM_BUILD_ROOT} \
  install

%{__mv}      -f      ${RPM_BUILD_ROOT}%{_bindir}/%{name} ${RPM_BUILD_ROOT}%{_sbindir}

%{__mkdir_p}                      ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
%{__install} -m 0644 %{SOURCE1}   ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/%{name}
%{__mkdir_p}                      ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
%{__install} -m 0644 %{SOURCE2}   ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/%{name}
%{__mkdir_p}                      ${RPM_BUILD_ROOT}%{_tmpfilesdir}
%{__install} -m 0644 %{SOURCE3}   ${RPM_BUILD_ROOT}%{_tmpfilesdir}/%{name}.conf
%{__mkdir_p}                      ${RPM_BUILD_ROOT}%{_unitdir}
%{__install} -m 0644 %{SOURCE4}   ${RPM_BUILD_ROOT}%{_unitdir}/%{name}.service

%{__install} -m 0755 contrib/*.pl ${RPM_BUILD_ROOT}%{_datadir}/%{modn}/contrib

%{__rm}      -f                   ${RPM_BUILD_ROOT}%{_libdir}/lib*.so.{?,??}

%pre
if ! getent group  %{name} >/dev/null 2>&1; then
  /usr/sbin/groupadd -r %{name}
fi
if ! getent passwd %{name} >/dev/null 2>&1; then
  /usr/sbin/useradd  -r -g %{name}   \
    -d /run/%{name} \
    -c "C-ICAP Service user" -M      \
    -s /sbin/nologin %{name}
fi
exit 0 # Always pass

%post
if [ $1 -eq 1 ] ; then # Initial installation
  /bin/systemctl daemon-reload >/dev/null 2>&1 || :
  /bin/systemctl enable c-icap.service >/dev/null 2>&1 || :
fi

%post libs -p /sbin/ldconfig

%preun
if [ $1 -eq 0 ]; then # Remove
  /bin/systemctl --no-reload disable c-icap.service >/dev/null 2>&1 || :
  /bin/systemctl stop c-icap.service >/dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then # Upgrade
  /bin/systemctl try-restart c-icap.service >/dev/null 2>&1 || :
fi

%postun libs
/sbin/ldconfig

%clean
[ -n "${RPM_BUILD_ROOT}" -a "${RPM_BUILD_ROOT}" != "/" ] && %{__rm} -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING INSTALL README TODO
%attr(750,root,%{name}) %dir %{_sysconfdir}/%{name}
%attr(640,root,%{name}) %config(noreplace) %{_sysconfdir}/%{name}/*.conf
%attr(640,root,%{name}) %config(noreplace) %{_sysconfdir}/%{name}/*.magic
%attr(640,root,%{name}) %{_sysconfdir}/%{name}/*.default
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
%defattr(-,root,root)
%{_bindir}/%{name}-*config
%{_includedir}/%{modn}
# Auto clean up of .la files in f36 and onwards
%if 0%{?fedora} < 36
%{_libdir}/libicapapi.*a
%endif
%{_libdir}/libicapapi.so
%{_libdir}/%{modn}/bdb_tables.*a
%{_libdir}/%{modn}/dnsbl_tables.*a
%{_libdir}/%{modn}/ldap_module.*a
%{_libdir}/%{modn}/perl_handler.*a
%{_libdir}/%{modn}/shared_cache.*a
%{_libdir}/%{modn}/srv_echo.*a
%{_libdir}/%{modn}/srv_ex206.*a
%{_libdir}/%{modn}/sys_logger.*a
%{_mandir}/man8/%{name}-*config.8*

%files ldap
%defattr(-,root,root)
%{_libdir}/%{modn}/ldap_module.so

%files libs
%defattr(-,root,root)
%doc COPYING
%{_libdir}/libicapapi.so.*

%files perl
%defattr(-,root,root)
%{_libdir}/%{modn}/perl_handler.so

%files bin
%defattr(-,root,root)
%{_bindir}/%{name}-client
%{_bindir}/%{name}-mkbdb
%{_bindir}/%{name}-stretch
%{_mandir}/man8/%{name}-client.8*
%{_mandir}/man8/%{name}-mkbdb.8*
%{_mandir}/man8/%{name}-stretch.8*

%changelog
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

* Mon Jan 28 2019 Frank Crawford <frank@crawford.emu.id.au> - 0.5.5-2
- Patch c-icap.conf to match correct logfile details

* Mon Jan 07 2019 Frank Crawford <frank@crawford.emu.id.au> - 0.5.5-1
- Update to 0.5.5

* Thu Mar 16 2017 Marcin Skarbek <rpm@skarbek.name> - 0.4.4-1
- Update to 0.4.4

* Mon Jan 07 2013 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.5-1
- Update to 0.2.5

* Mon Dec 31 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.4-1
- Update to 0.2.4

* Fri Nov 16 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.3-1
- Update to 0.2.3

* Tue Sep 25 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.2-1
- Update to 0.2.2

* Wed Jul 04 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.2.1-1
- Update to 0.2.1

* Mon Jun 04 2012 Oliver Seeburger <oliver.seeburger@sundermeier-werkzeugbau.de> - 0.1.7-2
- Initial build for Fedora 17
