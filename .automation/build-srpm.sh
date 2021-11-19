#!/bin/bash -xe

# Directory, where build artifacts will be stored, should be passed as the 1st parameter
ARTIFACTS_DIR=${1:-exported-artifacts}
export ARTIFACTS_DIR

# Prepare source archive
[[ -d rpmbuild/SOURCES ]] || mkdir -p rpmbuild/SOURCES

# Clean leftovers from previous builds
rm -rf rpmbuild/SOURCES/*
make clean

# Get the tarball
make dist


# Build SRPMs
rpmbuild \
    -D "_topdir rpmbuild" \
    -ts ./*.tar.gz
