#!/bin/bash -xe

# Finding git hash of the current commit depends if executed from github or not
if [ "${GITHUB_SHA}" == "" ]; then
  GIT_HASH=$(git rev-list HEAD | wc -l)
else
  GIT_HASH=$(git rev-parse --short $GITHUB_SHA)
fi
export GIT_HASH

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
