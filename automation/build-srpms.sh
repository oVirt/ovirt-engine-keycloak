#!/bin/sh -e

# Keycloak version specification
KEYCLOAK_VERSION="15.0.2"

# RPM version specification
RPM_VERSION="${KEYCLOAK_VERSION}"
RPM_RELEASE="1"

export KEYCLOAK_VERSION RPM_VERSION RPM_RELEASE

# Cleanup
rm -rf exported-artifacts
rm -rf output

# Build SRPMs
automation/build-keycloak.sh
