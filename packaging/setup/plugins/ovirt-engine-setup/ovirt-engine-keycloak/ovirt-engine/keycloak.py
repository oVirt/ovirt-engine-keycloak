#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""keycloak plugin."""


import gettext

from otopi import constants as otopicons
from otopi import filetransaction
from otopi import plugin
from otopi import util


from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-setup')


@util.export
class Plugin(plugin.PluginBase):
    """keycloak plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup(self):
        self.environment[oengcommcons.ConfigEnv.JAVA_NEEDED] = True
        self.environment[oengcommcons.ConfigEnv.JBOSS_NEEDED] = True

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        after=(
                oengcommcons.Stages.DB_CONNECTION_AVAILABLE,
        ),
        condition=lambda self: (
                self.environment[oenginecons.CoreEnv.ENABLE] and
                self.environment[
                    oenginecons.EngineDBEnv.NEW_DATABASE
                ],
        )
    )
    def _misc(self):
        content = [
            'KEYCLOAK_BUNDLED=true',
        ]
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=okkcons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIG_KEYCLOAK,
                content=content,
                modifiedList=self.environment[
                    otopicons.CoreEnv.MODIFIED_FILES
                ],
            )
        )


# vim: expandtab tabstop=4 shiftwidth=4
