%define underscore() %(echo %1 | sed 's/-/_/g')

Summary:       ARGO probe that checks validity of OAI-PMH XML response.
Name:          argo-probe-oai-pmh
Version:       0.2.0
Release:       1%{?dist}
Source0:       %{name}-%{version}.tar.gz
License:       ASL 2.0
Group:         Development/System
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Prefix:        %{_prefix}
BuildArch:     noarch

BuildRequires: python3-devel
Requires: python36-requests
Requires: python36-lxml


%description
ARGO probe that checks validity of OAI-PMH XML response.

%prep
%setup -q


%build
%{py3_build}


%install
%{py3_install "--record=INSTALLED_FILES" }


%clean
rm -rf $RPM_BUILD_ROOT


%files -f INSTALLED_FILES
%defattr(-,root,root)
%dir %{python3_sitelib}/%{underscore %{name}}/
%{python3_sitelib}/%{underscore %{name}}/*.py


%changelog
* Thu Mar 7 2024 Katarina Zailac <kzailac@srce.hr> - 0.2.0-1
- ARGO-4471 Add performance data to argo-probe-oai-pmh
* Thu Dec 7 2023 Katarina Zailac <kzailac@srce.hr> - 0.1.1-1
- ARGO-4441 Probe check_oai_pmh not exiting with proper system exit
* Thu Jul 28 2022 Katarina Zailac <katarina.zailac@gmail.com> - 0.1.0-1
- ARGO-3940 Create probe for OAI-PMH
