Name     : docker-upstream
Version  : 1.12.0
Release  : 7
URL      : https://github.com/docker/docker/archive/e8439971b42a65dd831f80ec76a38e8c8e938cb6.tar.gz
Source0  : https://github.com/docker/docker/archive/e8439971b42a65dd831f80ec76a38e8c8e938cb6.tar.gz
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

%global commit_id e8439971b42a65dd831f80ec76a38e8c8e938cb6

%description
Docker is an open source project to pack, ship and run any application as a lightweight container.

%prep
%setup -q -n docker-e8439971b42a65dd831f80ec76a38e8c8e938cb6
%patch1 -p1

%build
mkdir -p src/github.com/docker/
ln -s $(pwd) src/github.com/docker/docker
export DOCKER_GITCOMMIT=%commit_id AUTO_GOPATH=1 GOROOT=/usr/lib/golang
./hack/make.sh dynbinary

%install
rm -rf %{buildroot}
# install binary
install -d %{buildroot}/%{_bindir}
install -p -m 755 bundles/latest/dynbinary-client/docker-%{version}-dev %{buildroot}%{_bindir}/docker-upstream
install -p -m 755 bundles/latest/dynbinary-daemon/dockerd-%{version}-dev %{buildroot}%{_bindir}/dockerd-upstream
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
%{_bindir}/dockerd-upstream
%{_bindir}/docker-containerd
%{_bindir}/docker-containerd-shim
%{_bindir}/docker-containerd-ctr
%{_bindir}/docker-runc
%{_prefix}/lib/systemd/system/*.socket
%{_prefix}/lib/systemd/system/*.service
%{_prefix}/lib/systemd/system/*/*.socket
%{_prefix}/lib/systemd/system/*/*.service
