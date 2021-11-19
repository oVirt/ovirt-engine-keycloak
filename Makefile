# ====================================================================
#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ====================================================================
#
# This software consists of voluntary contributions made by many
# individuals on behalf of the Apache Software Foundation.  For more
# information on the Apache Software Foundation, please see
# <http://www.apache.org/>.

#
# CUSTOMIZATION-BEGIN
#
# Keycloak version specification
KEYCLOAK_VERSION="15.0.2"

# RPM version specification
RPM_VERSION="${KEYCLOAK_VERSION}"
RPM_RELEASE="1"

EXTRA_BUILD_FLAGS=
BUILD_VALIDATION=1

PACKAGE_NAME=ovirt-engine-keycloak

PYTHON=$(shell which python3 2> /dev/null)
PREFIX=/usr/local
LOCALSTATE_DIR=$(PREFIX)/var
BIN_DIR=$(PREFIX)/bin
SYSCONF_DIR=$(PREFIX)/etc
DATAROOT_DIR=$(PREFIX)/share
DOC_DIR=$(DATAROOT_DIR)/doc
PKG_DATA_DIR=$(DATAROOT_DIR)/ovirt-engine-keycloak
PKG_SYSCONF_DIR=$(SYSCONF_DIR)/ovirt-engine-keycloak
WILDFLY_DATA_DIR=$(DATAROOT_DIR)/ovirt-engine-wildfly
HTTPD_SYSCONF_DIR=$(SYSCONF_DIR)/httpd
PYTHON_DIR=$(PYTHON_SYS_DIR)
DEV_PYTHON_DIR=
PKG_USER=ovirt
PKG_GROUP=ovirt
KEYCLOAK_OVERLAY_ZIP="keycloak-overlay-$(KEYCLOAK_VERSION).zip"
KEYCLOAK_OVERLAY_URL="https://github.com/keycloak/keycloak/releases/download/${KEYCLOAK_VERSION}/${KEYCLOAK_OVERLAY_ZIP}"
#
# CUSTOMIZATION-END
#


BUILD_FLAGS:=$(BUILD_FLAGS) $(EXTRA_BUILD_FLAGS)

PYTHON_SYS_DIR:=$(shell $(PYTHON) -c "from distutils.sysconfig import get_python_lib as f;print(f())")

TARBALL=$(PACKAGE_NAME)-$(RPM_VERSION).tar.gz
BUILD_FILE=tmp.built


.SUFFIXES:
.SUFFIXES: .in

.in:
	sed \
	-e "s|@KEYCLOAK_VERSION@|$(KEYCLOAK_VERSION)|g" \
	-e "s|@KEYCLOAK_OVERLAY_ZIP@|$(KEYCLOAK_OVERLAY_ZIP)|g" \
	-e "s|@PKG_USER@|$(PKG_USER)|g" \
	-e "s|@PKG_GROUP@|$(PKG_GROUP)|g" \
	-e "s|@DATAROOT_DIR@|$(DATAROOT_DIR)|g" \
	-e "s|@PKG_SYSCONF_DIR@|$(PKG_SYSCONF_DIR)|g" \
	-e "s|@PKG_DATA_DIR@|$(PKG_DATA_DIR)|g" \
	-e "s|@PKG_STATE_DIR@|$(PKG_STATE_DIR)|g" \
	-e "s|@DEV_PYTHON_DIR@|$(DEV_PYTHON_DIR)|g" \
	-e "s|@RPM_VERSION@|$(RPM_VERSION)|g" \
	-e "s|@RPM_RELEASE@|$(RPM_RELEASE)|g" \
	-e "s|@PACKAGE_NAME@|$(PACKAGE_NAME)|g" \
	-e "s|@KEYCLOAK_VERSION@|$(KEYCLOAK_VERSION)|g" \
	-e "s|@KEYCLOAK_OVERLAY_PKG@|$(KEYCLOAK_OVERLAY_PKG)|g" \
	-e "s|@PY_VERSION@|$(PY_VERSION)|g" \
	-e "s|@HTTPD_SYSCONF_DIR@|$(HTTPD_SYSCONF_DIR)|g" \
	-e "s|@WILDFLY_DATA_DIR@|$(WILDFLY_DATA_DIR)|g" \
	$< > $@


GENERATED = \
	build/python-check.sh \
	ovirt-engine-keycloak.spec \
	packaging/setup/ovirt_engine_setup/keycloak/config.py \
	$(NULL)


all:	\
	generated-files \
	validations \
	$(BUILD_FILE) \
	$(NULL)

generated-files:	$(GENERATED)
	chmod a+x build/python-check.sh

$(BUILD_FILE):
	touch $(BUILD_FILE)

clean:
	rm -rf $(BUILD_FILE)
	rm -rf tmp.dev.flist
	rm -rf $(GENERATED)

install: \
	all \
	install-packaging-files \
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
	@echo For distro specific packaging refer to http://www.ovirt.org/Build_Binary_Package
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
		build/shell-check.sh && \
		build/python-check.sh; \
	fi

install-packaging-files: \
		$(GENERATED) \
		$(NULL)
	$(MAKE) copy-recursive SOURCEDIR=packaging/sys-etc TARGETDIR="$(DESTDIR)$(SYSCONF_DIR)" EXCLUDE_GEN="$(GENERATED)"
	$(MAKE) copy-recursive SOURCEDIR=packaging/setup TARGETDIR="$(DESTDIR)$(PKG_DATA_DIR)/../ovirt-engine/setup" EXCLUDE_GEN="$(GENERATED)"
	$(MAKE) copy-recursive SOURCEDIR=packaging/conf TARGETDIR="$(DESTDIR)$(PKG_DATA_DIR)/conf" EXCLUDE_GEN="$(GENERATED)"

