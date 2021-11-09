# outdir: passed by copr telling where to save the src.rpm
# spec: passed by copr telling which spec file should be used;
#       using for selecting the right src.rpm to be copied.

installdeps:
	dnf -y install coreutils curl dnf-utils findutils git rpmdevtools sed

srpm: installdeps
	automation/build-keycloak.sh
	cp output/$(shell sh -c "basename '$(spec)'|cut -f1 -d.")*.src.rpm $(outdir)
