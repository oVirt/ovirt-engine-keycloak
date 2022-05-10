# outdir: passed by copr telling where to save the src.rpm
# spec: passed by copr telling which spec file should be used;
#       using for selecting the right src.rpm to be copied.

installdeps:
	dnf -y install coreutils curl dnf-utils findutils git rpmdevtools sed

# explicity mark the copr generated git repo directory (which is done prior to the mock
# call to the make_srpm and will be the current pwd) as safe for git commands
git-safe:
	git config --global --add safe.directory "$(shell pwd)"

srpm: installdeps git-safe
	.automation/build-srpm.sh
	cp rpmbuild/SRPMS/$(shell sh -c "basename '$(spec)'|cut -f1 -d.")*.src.rpm $(outdir)
