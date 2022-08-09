#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Keycloak connection plugin."""


from otopi import plugin
from otopi import util

from ovirt_engine_setup.keycloak import constants as okkcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.engine_common import database


@util.export
class Plugin(plugin.PluginBase):
    """Keycloak connection plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        name=okkcons.Stages.DB_CONNECTION_CUSTOMIZATION,
        before=(
            oengcommcons.Stages.DB_OWNERS_CONNECTIONS_CUSTOMIZED,
        ),
        after=(
            oengcommcons.Stages.DIALOG_TITLES_S_DATABASE,
        ),
        condition=lambda self: (
            self.environment[oenginecons.CoreEnv.ENABLE] and
            self.environment[oengcommcons.KeycloakEnv.ENABLE]
        )
    )
    def _customization(self):
        database.OvirtUtils(
            plugin=self,
            dbenvkeys=okkcons.Const.KEYCLOAK_DB_ENV_KEYS,
        ).getCredentials(
            name='Keycloak',
            queryprefix='OVESETUP_KEYCLOAK_DB_',
            defaultdbenvkeys=okkcons.Const.DEFAULT_KEYCLOAK_DB_ENV_KEYS,
            show_create_msg=True,
        )


# vim: expandtab tabstop=4 shiftwidth=4
