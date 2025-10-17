# ====================================================================
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
# ====================================================================

#
# CUSTOMIZATION-BEGIN
#
# Keycloak version specification
KEYCLOAK_VERSION="15.0.2"

# RPM version specification
RPM_VERSION="${KEYCLOAK_VERSION}"

RPM_RELEASE_MAIN="7"

# For stable releases it should be empty
RPM_RELEASE_SUFFIX=""
# For nightly release it should contain githash and current date
#RPM_RELEASE_SUFFIX=".0.master.$(shell date -u +%Y%m%d%H%M%S).git$(GIT_HASH)"


RPM_RELEASE="$(RPM_RELEASE_MAIN)$(RPM_RELEASE_SUFFIX)"

EXTRA_BUILD_FLAGS=
BUILD_VALIDATION=1

PACKAGE_NAME=ovirt-engine-keycloak

PYTHON=$(shell which python3 2> /dev/null)
PREFIX=/usr/local
LOCALSTATE_DIR=$(PREFIX)/var
DATAROOT_DIR=$(PREFIX)/share
PKG_DATA_DIR=$(DATAROOT_DIR)/ovirt-engine-keycloak
PKG_STATE_DIR=$(LOCALSTATE_DIR)/lib/ovirt-engine-keycloak
KEYCLOAK_OVERLAY_ZIP="keycloak-overlay-$(KEYCLOAK_VERSION).zip"
KEYCLOAK_OVERLAY_URL="https://github.com/keycloak/keycloak/releases/download/${KEYCLOAK_VERSION}/${KEYCLOAK_OVERLAY_ZIP}"
#
# CUSTOMIZATION-END
#
BUILD_FLAGS:=$(BUILD_FLAGS) $(EXTRA_BUILD_FLAGS)

TARBALL=$(PACKAGE_NAME)-$(RPM_VERSION).tar.gz
BUILD_FILE=tmp.built


.SUFFIXES:
.SUFFIXES: .in

.in:
	sed \
	-e "s|@KEYCLOAK_VERSION@|$(KEYCLOAK_VERSION)|g" \
	-e "s|@KEYCLOAK_OVERLAY_ZIP@|$(KEYCLOAK_OVERLAY_ZIP)|g" \
	-e "s|@DATAROOT_DIR@|$(DATAROOT_DIR)|g" \
	-e "s|@PKG_DATA_DIR@|$(PKG_DATA_DIR)|g" \
	-e "s|@PKG_STATE_DIR@|$(PKG_STATE_DIR)|g" \
	-e "s|@RPM_VERSION@|$(RPM_VERSION)|g" \
	-e "s|@RPM_RELEASE@|$(RPM_RELEASE)|g" \
	-e "s|@PACKAGE_NAME@|$(PACKAGE_NAME)|g" \
	$< > $@


GENERATED = \
	ovirt-engine-keycloak.spec \
	packaging/setup/ovirt_engine_setup/keycloak/config.py \
	$(NULL)


all:	\
	generated-files \
	validations \
	$(BUILD_FILE) \
	$(NULL)

generated-files:	$(GENERATED)

$(BUILD_FILE):
	touch $(BUILD_FILE)

clean:
	rm -rf $(BUILD_FILE)
	rm -rf tmp.dev.flist
	rm -rf $(GENERATED)
	rm -f "$(PACKAGE_NAME)-*.tar.gz"

install: \
	all \
	install-packaging-files \
	install-layout \
	$(NULL)

.PHONY: ovirt-engine-keycloak.spec.in

dist:	ovirt-engine-keycloak.spec \
	download-keycloak \
	$(NULL)

	git ls-files | tar --files-from /proc/self/fd/0 -czf \
		"$(TARBALL)" \
		ovirt-engine-keycloak.spec \
		$(KEYCLOAK_OVERLAY_ZIP)
	@echo
	@echo For distro specific packaging refer to https://www.ovirt.org/develop/dev-process/build-binary-package.html
	@echo

download-keycloak:
	if [ ! -f "$(KEYCLOAK_OVERLAY_ZIP)" ]; then \
		curl -L -o "$(KEYCLOAK_OVERLAY_ZIP)" "$(KEYCLOAK_OVERLAY_URL)"; \
	fi

# copy SOURCEDIR to TARGETDIR
# exclude EXCLUDEGEN a list of files to exclude with .in
# exclude EXCLUDE a list of files.
copy-recursive:
	( cd "$(SOURCEDIR)" && find . -type d -printf '%P\n' ) | while read d; do \
		install -d -m 755 "$(TARGETDIR)/$${d}"; \
	done
	( \
		cd "$(SOURCEDIR)" && find . -type f -printf '%P\n' | \
		while read f; do \
			exclude=false; \
			for x in $(EXCLUDE_GEN); do \
				if [ "$(SOURCEDIR)/$${f}" = "$${x}.in" ]; then \
					exclude=true; \
					break; \
				fi; \
			done; \
			for x in $(EXCLUDE); do \
				if [ "$(SOURCEDIR)/$${f}" = "$${x}" ]; then \
					exclude=true; \
					break; \
				fi; \
			done; \
			$${exclude} || echo "$${f}"; \
		done \
	) | while read f; do \
		src="$(SOURCEDIR)/$${f}"; \
		dst="$(TARGETDIR)/$${f}"; \
		[ -x "$${src}" ] && MASK=0755 || MASK=0644; \
		[ -n "$(DEV_FLIST)" ] && echo "$${dst}" | sed 's#^$(PREFIX)/##' >> "$(DEV_FLIST)"; \
		install -T -m "$${MASK}" "$${src}" "$${dst}"; \
	done


validations:	generated-files
	if [ "$(BUILD_VALIDATION)" != 0 ]; then \
		build/python-check.sh; \
	fi

install-packaging-files: \
		$(GENERATED) \
		$(NULL)
	$(MAKE) copy-recursive SOURCEDIR=packaging/setup TARGETDIR="$(DESTDIR)$(PKG_DATA_DIR)/../ovirt-engine/setup" EXCLUDE_GEN="$(GENERATED)"
	$(MAKE) copy-recursive SOURCEDIR=packaging/conf TARGETDIR="$(DESTDIR)$(PKG_DATA_DIR)/conf" EXCLUDE_GEN="$(GENERATED)"
	$(MAKE) copy-recursive SOURCEDIR=packaging/bin TARGETDIR="$(DESTDIR)$(PKG_DATA_DIR)/bin" EXCLUDE_GEN="$(GENERATED)"

install-layout:
	install -dm 755 "$(DESTDIR)$(PKG_STATE_DIR)/backups" \
