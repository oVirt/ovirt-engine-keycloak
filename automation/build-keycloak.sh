#!/bin/sh -e


# Keycloak version specification
KEYCLOAK_VERSION="15.0.2"

# RPM version specification
RPM_VERSION="${KEYCLOAK_VERSION}"
RPM_RELEASE="1"

# export KEYCLOAK_VERSION RPM_VERSION RPM_RELEASE

# Cleanup
rm -rf exported-artifacts
rm -rf output


# The name and source of the package
name="ovirt-engine-keycloak"
src="keycloak-overlay-$KEYCLOAK_VERSION.zip"
url="https://github.com/keycloak/keycloak/releases/download/${KEYCLOAK_VERSION}/keycloak-overlay-${KEYCLOAK_VERSION}.zip"

# Download the source:
if [ ! -f "${src}" ]
then
    curl -L -o "${src}" "${url}"
fi

# Generate the spec from the template:
sed \
    -e "s/@VERSION@/${RPM_VERSION}/g" \
    -e "s/@RELEASE@/${RPM_RELEASE}/g" \
    -e "s/@SRC@/${src}/g" \
    < "${name}.spec.in" \
    > "${name}.spec"

# Build the source and binary packages:
rpmbuild \
    -bs \
    --define="_sourcedir ${PWD}" \
    --define="_srcrpmdir ${PWD}/output" \
    --define="_rpmdir ${PWD}" \
    "${name}.spec"

