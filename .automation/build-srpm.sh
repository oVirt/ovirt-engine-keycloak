#!/bin/bash -xe

# Directory, where build artifacts will be stored, should be passed as the 1st parameter
ARTIFACTS_DIR=${1:-exported-artifacts}
export ARTIFACTS_DIR

# Prepare source archive
[[ -d rpmbuild/SOURCES ]] || mkdir -p rpmbuild/SOURCES


# Keycloak version specification
KEYCLOAK_VERSION="15.0.2"

# RPM version specification
RPM_VERSION="${KEYCLOAK_VERSION}"
RPM_RELEASE="1"

export KEYCLOAK_VERSION RPM_VERSION RPM_RELEASE

# Cleanup
#rm -rf $ARTIFACTS_DIR

# The name and source of the package
name="ovirt-engine-keycloak"
src="keycloak-overlay-$KEYCLOAK_VERSION.zip"
url="https://github.com/keycloak/keycloak/releases/download/${KEYCLOAK_VERSION}/keycloak-overlay-${KEYCLOAK_VERSION}.zip"

# Download the source:
if [ ! -f "${src}" ]
then
    curl -L -o "rpmbuild/SOURCES/${src}" "${url}"
fi

# Generate the spec from the template:
sed \
    -e "s/@VERSION@/${RPM_VERSION}/g" \
    -e "s/@RELEASE@/${RPM_RELEASE}/g" \
    -e "s/@SRC@/${src}/g" \
    < "${name}.spec.in" \
    > "${name}.spec"

cp "${name}.spec.in" rpmbuild/SOURCES
cp "${name}.spec" rpmbuild/SOURCES
cp "README.md" rpmbuild/SOURCES

# Build SRPMs
rpmbuild \
    -D "_topdir rpmbuild" \
    -bs "${name}.spec"






