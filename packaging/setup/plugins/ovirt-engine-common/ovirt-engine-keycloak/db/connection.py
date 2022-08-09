#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Keycloak DB Connection plugin."""


import gettext


from otopi import constants as otopicons
from otopi import util
from otopi import plugin


from ovirt_engine import configfile

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.keycloak import constants as okkcons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.engine_common import database


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Keycloak DB Connection plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_BOOT,
    )
    def _boot(self):
        self.environment[
            otopicons.CoreEnv.LOG_FILTER_KEYS
        ].append(
            okkcons.DBEnv.PASSWORD
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            okkcons.DBEnv.HOST,
            None
        )
        self.environment.setdefault(
            okkcons.DBEnv.PORT,
            None
        )
        self.environment.setdefault(
            okkcons.DBEnv.SECURED,
            None
        )
        self.environment.setdefault(
            okkcons.DBEnv.SECURED_HOST_VALIDATION,
            None
        )
        self.environment.setdefault(
            okkcons.DBEnv.USER,
            None
        )
        self.environment.setdefault(
            okkcons.DBEnv.PASSWORD,
            None
        )
        self.environment.setdefault(
            okkcons.DBEnv.DATABASE,
            None
        )
        self.environment.setdefault(
            okkcons.DBEnv.DUMPER,
            okkcons.Defaults.DEFAULT_DB_DUMPER
        )
        self.environment.setdefault(
            okkcons.DBEnv.FILTER,
            okkcons.Defaults.DEFAULT_DB_FILTER
        )
        self.environment.setdefault(
            okkcons.DBEnv.RESTORE_JOBS,
            okkcons.Defaults.DEFAULT_DB_RESTORE_JOBS
        )

        self.environment[okkcons.DBEnv.CONNECTION] = None
        self.environment[okkcons.DBEnv.STATEMENT] = None
        self.environment[okkcons.DBEnv.NEW_DATABASE] = True
        self.environment[okkcons.DBEnv.NEED_DBMSUPGRADE] = False

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _commands(self):
        dbovirtutils = database.OvirtUtils(
            plugin=self,
            dbenvkeys=okkcons.Const.KEYCLOAK_DB_ENV_KEYS,
        )
        dbovirtutils.detectCommands()

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
        name=okkcons.Stages.DB_CONNECTION_SETUP,
        condition=lambda self: (
            self.environment[osetupcons.CoreEnv.ACTION]
            != osetupcons.Const.ACTION_PROVISIONDB
        ),
    )
    def _setup_connection(self):
        config = configfile.ConfigFile([
            okkcons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIG_KEYCLOAK,
        ])
        if config.get('KEYCLOAK_DB_PASSWORD'):
            try:
                dbenv = {}
                for e, k in (
                        (okkcons.DBEnv.HOST, 'KEYCLOAK_DB_HOST'),
                        (okkcons.DBEnv.PORT, 'KEYCLOAK_DB_PORT'),
                        (okkcons.DBEnv.USER, 'KEYCLOAK_DB_USER'),
                        (okkcons.DBEnv.PASSWORD, 'KEYCLOAK_DB_PASSWORD'),
                        (okkcons.DBEnv.DATABASE, 'KEYCLOAK_DB_DATABASE'),
                ):
                    dbenv[e] = (
                        self.environment.get(e)
                        if self.environment.get(e) is not None
                        else config.get(k)
                    )
                for e, k in (
                        (okkcons.DBEnv.SECURED, 'KEYCLOAK_DB_SECURED'),
                        (
                                okkcons.DBEnv.SECURED_HOST_VALIDATION,
                                'KEYCLOAK_DB_SECURED_VALIDATION'
                        )
                ):
                    dbenv[e] = config.getboolean(k)

                dbovirtutils = database.OvirtUtils(
                    plugin=self,
                    dbenvkeys=okkcons.Const.KEYCLOAK_DB_ENV_KEYS,
                )
                dbovirtutils.tryDatabaseConnect(dbenv)
                self.environment.update(dbenv)
                self.environment[
                    okkcons.DBEnv.NEW_DATABASE
                ] = dbovirtutils.isNewDatabase()
                self.environment[
                    okkcons.DBEnv.NEED_DBMSUPGRADE
                ] = dbovirtutils.checkDBMSUpgrade()
            except RuntimeError:
                self.logger.debug(
                    'Existing credential use failed',
                    exc_info=True,
                )
                msg = _(
                    "Cannot connect to Keycloak database '{database}' using existing "
                    "credentials: {user}@{host}:{port}"
                ).format(
                    host=dbenv[okkcons.DBEnv.HOST],
                    port=dbenv[okkcons.DBEnv.PORT],
                    database=dbenv[okkcons.DBEnv.DATABASE],
                    user=dbenv[okkcons.DBEnv.USER],
                )
                if self.environment[
                    osetupcons.CoreEnv.ACTION
                ] == osetupcons.Const.ACTION_REMOVE:
                    self.logger.warning(msg)
                else:
                    raise RuntimeError(msg)


# vim: expandtab tabstop=4 shiftwidth=4
