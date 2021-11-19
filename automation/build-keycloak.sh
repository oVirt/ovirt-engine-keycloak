#!/bin/sh -e


# Keycloak version specification
KEYCLOAK_VERSION="15.0.2"

# RPM version specification
RPM_VERSION="${KEYCLOAK_VERSION}"
RPM_RELEASE="1"


# Cleanup
rm -rf exported-artifacts
rm -rf output
make clean


# The name and source of the package
name="ovirt-engine-keycloak"
src="keycloak-overlay-$KEYCLOAK_VERSION.zip"
url="https://github.com/keycloak/keycloak/releases/download/${KEYCLOAK_VERSION}/keycloak-overlay-${KEYCLOAK_VERSION}.zip"

[[ -d ${PWD}/rpmbuild/SOURCES ]] || mkdir -p ${PWD}/rpmbuild/SOURCES

# Get the tarball
make dist

# Build the source and binary packages:
rpmbuild \
	-ts \
	--define="_topdir ${PWD}/rpmbuild" \
	--define="_srcrpmdir ${PWD}/output" \
	"${name}-${RPM_VERSION}.tar.gz"
