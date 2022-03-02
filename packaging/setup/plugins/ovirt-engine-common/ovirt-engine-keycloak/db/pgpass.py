#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Keycloak DB pgpass plugin."""


import gettext


from otopi import util
from otopi import plugin


from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import database
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Keycloak DB pgpass plugin."""
    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment[okkcons.DBEnv.PGPASS_FILE] = None

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        name=okkcons.Stages.DB_CREDENTIALS_AVAILABLE,
        condition=lambda self: (
                self.environment[oenginecons.CoreEnv.ENABLE] and
                self.environment[okkcons.DBEnv.PASSWORD] is not None
        ),
    )
    def _misc(self):
        database.OvirtUtils(
            plugin=self,
            dbenvkeys=okkcons.Const.KEYCLOAK_DB_ENV_KEYS,
        ).createPgPass()


# vim: expandtab tabstop=4 shiftwidth=4
