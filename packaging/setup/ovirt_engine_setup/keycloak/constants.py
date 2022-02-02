#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Constants."""


import gettext
import os

from otopi import util

from ovirt_engine_setup import constants as oesetupcons
from ovirt_engine_setup.engine_common import config as oesetupcommconfig
from ovirt_engine_setup.constants import osetupattrs
from ovirt_engine_setup.constants import osetupattrsclass
from ovirt_engine_setup.engine import constants as oenginecons

from . import config


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-setup')


@util.export
@util.codegen
class Const(object):
    OVIRT_ENGINE_KEYCLOAK_SETUP_PACKAGE_NAME = \
        'ovirt-engine-keycloak'
    KEYCLOAK_MASTER_REALM = 'master'
    KEYCLOAK_INTERNAL_REALM = 'ovirt-internal'
    OVIRT_ADMIN_USER = 'admin@ovirt'
    KEYCLOAK_INTERNAL_CLIENT_NAME = 'ovirt-engine-internal'
    KEYCLOAK_WEB_CONTEXT = 'ovirt-engine-auth'
    OVIRT_CLIENT_SCOPES = [
        'ovirt-app-admin',
        'ovirt-app-api',
        'ovirt-app-portal',
        'ovirt-ext=auth:identity',
        'ovirt-ext=auth:sequence-priority=~',
        'ovirt-ext=token-info:authz-search',
        'ovirt-ext=token-info:public-authz-search',
        'ovirt-ext=token-info:validate',
        'ovirt-ext=token:login-on-behalf',
        'ovirt-ext=token:password-access',
        'ovirt-ext=revoke:revoke-all',
    ]
    OVIRT_ADMINISTRATOR_USER_GROUP_NAME = 'ovirt-administrator'
    OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME = 'internalkeycloak'
    OVIRT_ENGINE_KEYCLOAK_SSO_PROFILE = 'internalsso'


@util.export
@util.codegen
@osetupattrsclass
class ApacheEnv(object):
    HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK = 'OVESETUP_APACHE/configFileOvirtEngineKeycloak'
    HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC = 'OVESETUP_APACHE/configFileInternalSsoOpenIdc'


@util.export
@util.codegen
@osetupattrsclass
class ConfigEnv(object):

    @osetupattrs(
        is_secret=True,
    )
    def KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET(self):
        return 'OVESETUP_KEYCLOAK/ovirtInternalClientSecret'


@util.export
@util.codegen
class FileLocations(oesetupcons.FileLocations):
    PKG_DATA_DIR = config.PKG_DATA_DIR

    DIR_HTTPD = os.path.join(
        oesetupcons.FileLocations.SYSCONFDIR,
        'httpd',
    )

    HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK = os.path.join(
        DIR_HTTPD,
        'conf.d',
        'z-ovirt-engine-keycloak-proxy.conf'
    )

    HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK_TEMPLATE = os.path.join(
        PKG_DATA_DIR,
        'conf',
        'z-ovirt-engine-keycloak-proxy.conf.in',
    )

    HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC = os.path.join(
        DIR_HTTPD,
        'conf.d',
        'internalsso-openidc.conf'
    )

    HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC_TEMPLATE = os.path.join(
        PKG_DATA_DIR,
        'conf',
        'internalsso-openidc.conf.in',
    )

    OVIRT_ENGINE_SERVICE_CONFIG_KEYCLOAK = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIGD,
        '12-setup-keycloak.conf'
    )

    OVIRT_ENGINE_SERVICE_KEYCLOAK_AUTHN = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_EXTENSIONS_DIR,
        '{}-authn.properties'.format(
            Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME
        )
    )

    OVIRT_ENGINE_SERVICE_KEYCLOAK_AUTHZ = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_EXTENSIONS_DIR,
        '{}-authz.properties'.format(
            Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME
        )
    )

    OVIRT_ENGINE_SERVICE_KEYCLOAK_HTTP_MAPPING = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_EXTENSIONS_DIR,
        '{}-http-mapping.properties'.format(
            Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME
        )
    )

    KEYCLOAK_ADD_USER_SCRIPT = os.path.join(
        oesetupcommconfig.JBOSS_HOME,
        "bin",
        "add-user-keycloak.sh",
    )

    KEYCLOAK_CLI_ADMIN_SCRIPT = os.path.join(
        oesetupcommconfig.JBOSS_HOME,
        "bin",
        "kcadm.sh",
    )

    OVIRT_ENGINE_CONFIG_DIR = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_DATADIR,
        "services",
        "ovirt-engine"
    )

    KEYCLOAK_ADD_INITIAL_ADMIN_FILE = os.path.join(
        OVIRT_ENGINE_CONFIG_DIR,
        "keycloak-add-user.json",
    )


@util.export
class Stages(object):
    CLIENT_SECRET_GENERATED = 'osetup.keycloak.core.client_secret'


# vim: expandtab tabstop=4 shiftwidth=4
