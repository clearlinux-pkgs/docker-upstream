Name     : docker-upstream
Version  : 1.11.1
Release  : 1
URL      : https://github.com/docker/docker/archive/v1.11.1.tar.gz
Source0  : https://github.com/docker/docker/archive/v1.11.1.tar.gz
Summary  : the open-source application container engine
Group    : Development/Tools
License  : Apache-2.0
BuildRequires : go
BuildRequires : glibc-staticdev
BuildRequires : pkgconfig(sqlite3)
BuildRequires : pkgconfig(devmapper)
BuildRequires : btrfs-progs-devel
BuildRequires : gzip
Requires : gzip
Requires : containerd
Requires : runc
Conflicts : docker
Patch1    : 0001-add-suffix-to-socket-and-service-files.patch

# don't strip, these are not ordinary object files
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

%global gopath /usr/lib/golang
%global library_path github.com/docker/

%global commit_id 5604cbed50d51c4039b1abcb1cf87c4e01bce924

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n docker-%{version}
%patch1 -p1
#%patch1 -p1
#%if "%{_vendor}" != "clr"
#%patch2 -p1
#%endif
# %patch401 -p1
# %patch402 -p1
# %patch403 -p1
# %patch5 -p1
# %patch6 -p1

%build
mkdir -p src/github.com/docker/
ln -s $(pwd) src/github.com/docker/docker
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 GOROOT=/usr/lib/golang
./hack/make.sh dynbinary

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/%{_bindir}
install -p -m 755 bundles/latest/dynbinary/docker-%{version} %{buildroot}%{_bindir}/docker-upstream
# install containerd
ln -s /usr/bin/containerd %{buildroot}/%{_bindir}/docker-containerd
ln -s /usr/bin/containerd-shim %{buildroot}/%{_bindir}/docker-containerd-shim
ln -s /usr/bin/containerd-ctr %{buildroot}/%{_bindir}/docker-containerd-ctr

# install runc
ln -s /usr/bin/runc %{buildroot}/%{_bindir}/docker-runc

# install systemd unit files
install -m 0644 -D ./contrib/init/systemd/docker-upstream.service %{buildroot}%{_prefix}/lib/systemd/system/docker-upstream.service
install -m 0644 -D ./contrib/init/systemd/docker-upstream.socket %{buildroot}%{_prefix}/lib/systemd/system/docker-upstream.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/sockets.target.wants
ln -s ../docker-upstream.socket %{buildroot}/usr/lib/systemd/system/sockets.target.wants/docker-upstream.socket
mkdir -p %{buildroot}/usr/lib/systemd/system/multi-user.target.wants
ln -s ../docker-upstream.service %{buildroot}/usr/lib/systemd/system/multi-user.target.wants/docker-upstream.service

# add init scripts
install -d %{buildroot}/etc/sysconfig
install -d %{buildroot}/%{_initddir}

%files
%defattr(-,root,root,-)
%{_bindir}/docker-upstream
%{_bindir}/docker-containerd
%{_bindir}/docker-containerd-shim
%{_bindir}/docker-containerd-ctr
%{_bindir}/docker-runc
%{_prefix}/lib/systemd/system/*.socket
%{_prefix}/lib/systemd/system/*.service
%{_prefix}/lib/systemd/system/*/*.socket
%{_prefix}/lib/systemd/system/*/*.service
