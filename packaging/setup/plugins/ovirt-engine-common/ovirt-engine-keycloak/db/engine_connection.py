#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Engine db Connection plugin. Will be used for user migration in future"""


import gettext


from otopi import constants as otopicons
from otopi import plugin
from otopi import transaction
from otopi import util


from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import database
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Engine db Connection plugin. Will be used for user migration in future"""

    class DBTransaction(transaction.TransactionElement):
        """yum transaction element."""

        def __init__(self, parent):
            self._parent = parent

        def __str__(self):
            return _("Keycloak Engine Database Transaction")

        def prepare(self):
            pass

        def abort(self):
            if not self._parent.environment[oenginecons.CoreEnv.ENABLE]:
                engine_conn = self._parent.environment[
                    oenginecons.EngineDBEnv.CONNECTION
                ]
                if engine_conn is not None:
                    engine_conn.rollback()
                    self._parent.environment[
                        oenginecons.EngineDBEnv.CONNECTION
                    ] = None

        def commit(self):
            if not self._parent.environment[oenginecons.CoreEnv.ENABLE]:
                engine_conn = self._parent.environment[
                    oenginecons.EngineDBEnv.CONNECTION
                ]
                if engine_conn is not None:
                    engine_conn.commit()

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_BOOT,
    )
    def _boot(self):
        self.environment[
            otopicons.CoreEnv.LOG_FILTER_KEYS
        ].append(
            oenginecons.EngineDBEnv.PASSWORD
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            oenginecons.EngineDBEnv.HOST,
            None
        )
        self.environment.setdefault(
            oenginecons.EngineDBEnv.PORT,
            None
        )
        self.environment.setdefault(
            oenginecons.EngineDBEnv.SECURED,
            None
        )
        self.environment.setdefault(
            oenginecons.EngineDBEnv.SECURED_HOST_VALIDATION,
            None
        )
        self.environment.setdefault(
            oenginecons.EngineDBEnv.USER,
            None
        )
        self.environment.setdefault(
            oenginecons.EngineDBEnv.PASSWORD,
            None
        )
        self.environment.setdefault(
            oenginecons.EngineDBEnv.DATABASE,
            None
        )

        self.environment[oenginecons.EngineDBEnv.CONNECTION] = None
        self.environment[oenginecons.EngineDBEnv.STATEMENT] = None
        self.environment[oenginecons.EngineDBEnv.NEW_DATABASE] = True
        self.environment[oenginecons.EngineDBEnv.NEED_DBMSUPGRADE] = False

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup_dbtransaction(self):
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            self.DBTransaction(self)
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        name=okkcons.Stages.ENGINE_DB_CONNECTION_AVAILABLE,
        condition=lambda self: (
            # If engine is enabled, STATEMENT and CONNECTION are set there
            not self.environment[oenginecons.CoreEnv.ENABLE] and
            self.environment[oenginecons.EngineDBEnv.PASSWORD] is not None
        ),
        after=(
            oengcommcons.Stages.DB_CONNECTION_AVAILABLE,
        ),
    )
    def _engine_connection(self):
        self.environment[
            oenginecons.EngineDBEnv.STATEMENT
        ] = database.Statement(
            environment=self.environment,
            dbenvkeys=oenginecons.Const.ENGINE_DB_ENV_KEYS,
        )
        # must be here as we do not have database at validation
        self.environment[
            oenginecons.EngineDBEnv.CONNECTION
        ] = self.environment[oenginecons.EngineDBEnv.STATEMENT].connect()


# vim: expandtab tabstop=4 shiftwidth=4
