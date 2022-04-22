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
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.constants import classproperty
from ovirt_engine_setup.constants import osetupattrs
from ovirt_engine_setup.constants import osetupattrsclass
from ovirt_engine_setup.engine import constants as oenginecons

from . import config


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-setup')

DEK = oengcommcons.DBEnvKeysConst

@util.export
@util.codegen
class Const(object):
    KEYCLOAK_MASTER_REALM = 'master'
    KEYCLOAK_INTERNAL_REALM = 'ovirt-internal'
    OVIRT_ADMIN_USER = 'admin@ovirt'
    OVIRT_ADMIN_USER_EMAIL = 'admin@localhost'
    KEYCLOAK_INTERNAL_CLIENT_NAME = 'ovirt-engine-internal'
    KEYCLOAK_WEB_CONTEXT = 'ovirt-engine-auth'
    KEYCLOAK_DB_MAX_CONNECTIONS = 20
    OVIRT_CLIENT_SCOPES = (
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
    )
    GRAFANA_ADMIN_ROLE = 'grafana-admin'
    GRAFANA_EDITOR_ROLE = 'grafana-editor'
    GRAFANA_VIEWER_ROLE = 'grafana-viewer'
    GRAFANA_USER_ROLES = (
        GRAFANA_ADMIN_ROLE,
        GRAFANA_EDITOR_ROLE,
        GRAFANA_VIEWER_ROLE,
    )
    OVIRT_ADMINISTRATOR_USER_GROUP_NAME = 'ovirt-administrator'
    OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME = 'internalkeycloak'
    OVIRT_ENGINE_KEYCLOAK_SSO_PROFILE = 'internalsso'
    OVIRT_ENGINE_KEYCLOAK_DB_BACKUP_PREFIX = 'keycloak'
    KEYCLOAK_ADD_USER_SCRIPT = 'add-user-keycloak.sh'
    KEYCLOAK_CLI_ADMIN_SCRIPT = 'kcadm.sh'
    OVIRT_ENGINE_KEYCLOAK_PACKAGE_NAME = 'ovirt-engine-keycloak'
    OVIRT_ENGINE_KEYCLOAK_SETUP_PACKAGE_NAME = 'ovirt-engine-keycloak-setup'

    @classproperty
    def KEYCLOAK_DB_ENV_KEYS(self):
        return {
            DEK.HOST: DBEnv.HOST,
            DEK.PORT: DBEnv.PORT,
            DEK.SECURED: DBEnv.SECURED,
            DEK.HOST_VALIDATION: DBEnv.SECURED_HOST_VALIDATION,
            DEK.USER: DBEnv.USER,
            DEK.PASSWORD: DBEnv.PASSWORD,
            DEK.DATABASE: DBEnv.DATABASE,
            DEK.CONNECTION: DBEnv.CONNECTION,
            DEK.PGPASSFILE: DBEnv.PGPASS_FILE,
            DEK.NEW_DATABASE: DBEnv.NEW_DATABASE,
            DEK.NEED_DBMSUPGRADE: DBEnv.NEED_DBMSUPGRADE,
            DEK.DUMPER: DBEnv.DUMPER,
            DEK.FILTER: DBEnv.FILTER,
            DEK.RESTORE_JOBS: DBEnv.RESTORE_JOBS,
        }

    @classproperty
    def DEFAULT_KEYCLOAK_DB_ENV_KEYS(self):
        return {
            DEK.HOST: Defaults.DEFAULT_DB_HOST,
            DEK.PORT: Defaults.DEFAULT_DB_PORT,
            DEK.SECURED: Defaults.DEFAULT_DB_SECURED,
            DEK.HOST_VALIDATION: Defaults.DEFAULT_DB_SECURED_HOST_VALIDATION,
            DEK.USER: Defaults.DEFAULT_DB_USER,
            DEK.PASSWORD: Defaults.DEFAULT_DB_PASSWORD,
            DEK.DATABASE: Defaults.DEFAULT_DB_DATABASE,
            DEK.DUMPER: Defaults.DEFAULT_DB_DUMPER,
            DEK.FILTER: Defaults.DEFAULT_DB_FILTER,
            DEK.RESTORE_JOBS: Defaults.DEFAULT_DB_RESTORE_JOBS,
        }

@util.export
@util.codegen
class Defaults(object):
    DEFAULT_DB_HOST = 'localhost'
    DEFAULT_DB_PORT = 5432
    DEFAULT_DB_DATABASE = 'ovirt_engine_keycloak'
    DEFAULT_DB_USER = 'ovirt_engine_keycloak'
    DEFAULT_DB_PASSWORD = ''
    DEFAULT_DB_SECURED = False
    DEFAULT_DB_SECURED_HOST_VALIDATION = False
    DEFAULT_DB_DUMPER = 'pg_custom'
    DEFAULT_DB_RESTORE_JOBS = 2
    DEFAULT_DB_FILTER = None

@util.export
@util.codegen
@osetupattrsclass
class ApacheEnv(object):
    HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK = \
        'OVESETUP_APACHE/configFileOvirtEngineKeycloak'
    HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC = \
        'OVESETUP_APACHE/configFileInternalSsoOpenIdc'

@util.export
@util.codegen
@osetupattrsclass
class ConfigEnv(object):

    @osetupattrs(
        is_secret=True,
        answerfile=True,
        postinstallfile=True,
    )
    def KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET(self):
        return 'OVESETUP_KEYCLOAK/ovirtInternalClientSecret'

    @osetupattrs(
        answerfile=True,
    )
    def OVIRT_ENGINE_KEYCLOAK_DB_BACKUP_DIR(self):
        return 'OVESETUP_KEYCLOAK_CONFIG/keycloakDbBackupDir'

    @osetupattrs(
        answerfile=True,
        postinstallfile=True,
        is_secret=True,
    )
    def ADMIN_PASSWORD(self):
        return 'OVESETUP_KEYCLOAK_CONFIG/adminPassword'

    KEYCLOAK_ADD_USER_SCRIPT = 'OVESETUP_KEYCLOAK_CONFIG/addUserKeycloakScript'
    KEYCLOAK_CLI_ADMIN_SCRIPT = 'OVESETUP_KEYCLOAK_CONFIG/kcadmScript'
    KEYCLOAK_WRAPPER_SCRIPT = 'OVESETUP_KEYCLOAK_CONFIG/kkWrapperScript'
    KEYCLOAK_AUTH_URL = 'OVESETUP_KEYCLOAK_CONFIG/authUrl'
    KEYCLOAK_TOKEN_URL = 'OVESETUP_KEYCLOAK_CONFIG/tokenUrl'
    KEYCLOAK_USERINFO_URL = 'OVESETUP_KEYCLOAK_CONFIG/userinfoUrl'

@util.export
@util.codegen
@osetupattrsclass
class CoreEnv(object):

    @osetupattrs(
        answerfile=True,
        postinstallfile=True,
        summary=True,
        reconfigurable=False,
        description=_('Keycloak installation'),
    )
    def ENABLE(self):
        return 'OVESETUP_KEYCLOAK_CORE/enable'

@util.export
@util.codegen
@osetupattrsclass
class DBEnv(object):

    @osetupattrs(
        answerfile=True,
        answerfile_condition=lambda env: not env.get(
            ProvisioningEnv.POSTGRES_PROVISIONING_ENABLED
        ),
        is_secret=True,
    )
    def PASSWORD(self):
        return 'OVESETUP_KEYCLOAK_DB/password'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Keycloak database host'),
    )
    def HOST(self):
        return 'OVESETUP_KEYCLOAK_DB/host'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Keycloak database port'),
    )
    def PORT(self):
        return 'OVESETUP_KEYCLOAK_DB/port'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Keycloak database secured connection'),
    )
    def SECURED(self):
        return 'OVESETUP_KEYCLOAK_DB/secured'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Keycloak database host name validation'),
    )
    def SECURED_HOST_VALIDATION(self):
        return 'OVESETUP_KEYCLOAK_DB/securedHostValidation'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Keycloak database name'),
    )
    def DATABASE(self):
        return 'OVESETUP_KEYCLOAK_DB/database'

    @osetupattrs(
        answerfile=True,
        summary=True,
        description=_('Keycloak database user name'),
    )
    def USER(self):
        return 'OVESETUP_KEYCLOAK_DB/user'

    @osetupattrs(
        answerfile=True,
        answerfile_condition=lambda env: not env.get(
            ProvisioningEnv.POSTGRES_PROVISIONING_ENABLED
        ),
    )
    def PASSWORD(self):
        return 'OVESETUP_KEYCLOAK_DB/password'

    @osetupattrs(
        answerfile=True,
    )
    def DUMPER(self):
        return 'OVESETUP_KEYCLOAK_DB/dumper'

    @osetupattrs(
        answerfile=True,
    )
    def FILTER(self):
        return 'OVESETUP_KEYCLOAK_DB/filter'

    @osetupattrs(
        answerfile=True,
    )
    def RESTORE_JOBS(self):
        return 'OVESETUP_KEYCLOAK_DB/restoreJobs'

    CONNECTION = 'OVESETUP_KEYCLOAK_DB/connection'
    STATEMENT = 'OVESETUP_KEYCLOAK_DB/statement'
    PGPASS_FILE = 'OVESETUP_KEYCLOAK_DB/pgPassFile'
    NEW_DATABASE = 'OVESETUP_KEYCLOAK_DB/newDatabase'
    NEED_DBMSUPGRADE = 'OVESETUP_KEYCLOAK_DB/needDBMSUpgrade'

@util.export
@util.codegen
@osetupattrsclass
class ProvisioningEnv(object):

    @osetupattrs(
        answerfile=True,
        summary=True,
        is_secret=True,
        description=_('Configure local Keycloak database'),
    )
    def POSTGRES_PROVISIONING_ENABLED(self):
        return 'OVESETUP_KEYCLOAK_PROVISIONING/postgresProvisioningEnabled'

@util.export
@util.codegen
@osetupattrsclass
class RemoveEnv(object):
    @osetupattrs(
        answerfile=True,
    )
    def REMOVE_DATABASE(self):
        return 'OVESETUP_KEYCLOAK_REMOVE/database'

@util.export
@util.codegen
@osetupattrsclass
class RPMDistroEnv(object):
    PACKAGES = 'OVESETUP_KEYCLOAK_RPMDISRO_PACKAGES'
    PACKAGES_SETUP = 'OVESETUP_KEYCLOAK_RPMDISRO_PACKAGES_SETUP'

@util.export
@util.codegen
class FileLocations(oesetupcons.FileLocations):
    PKG_DATA_DIR = config.PKG_DATA_DIR
    PKG_STATE_DIR = config.PKG_STATE_DIR

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

    KEYCLOAK_WRAPPER_SCRIPT = os.path.join(
        PKG_DATA_DIR,
        'bin',
        'kk_cli.sh'
    )

    OVIRT_ENGINE_SERVICE_CONFIG_KEYCLOAK = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIGD,
        '12-setup-keycloak.conf'
    )

    OVIRT_ENGINE_SERVICE_KEYCLOAK_AUTHN = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_EXTENSIONS_DIR,
        f'{Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME}-authn.properties'
    )

    OVIRT_ENGINE_SERVICE_KEYCLOAK_AUTHZ = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_EXTENSIONS_DIR,
        f'{Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME}-authz.properties'
    )

    OVIRT_ENGINE_SERVICE_KEYCLOAK_HTTP_MAPPING = os.path.join(
        oenginecons.FileLocations.OVIRT_ENGINE_EXTENSIONS_DIR,
        f'{Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME}'
        '-http-mapping.properties'
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

    OVIRT_ENGINE_DEFAULT_KEYCLOAK_DB_BACKUP_DIR = os.path.join(
        PKG_STATE_DIR,
        'backups',
    )

@util.export
class Stages(object):
    CLIENT_SECRET_GENERATED = 'osetup.keycloak.core.client_secret'
    AUTH_ENDPOINTS_RESOLVED = 'osetup.keycloak.core.auth.endpoints_resolved'
    CORE_ENABLE = 'osetup.keycloak.core.enable'
    KEYCLOAK_CREDENTIALS_SETUP = 'osetup.keycloak.config.credentials'
    DB_CREDENTIALS_AVAILABLE = 'osetup.keycloak.db.connection.credentials'
    DB_CONNECTION_SETUP = 'osetup.keycloak.db.connection.setup'
    ENGINE_DB_CONNECTION_AVAILABLE = \
        'osetup.keycloak.engine.db.connection.available'
    DB_PROVISIONING_CUSTOMIZATION = 'osetup.keycloak.db.provisioning.customization'
    DB_PROVISIONING_PROVISION = 'osetup.keycloak.db.provisioning.provision'


# vim: expandtab tabstop=4 shiftwidth=4
