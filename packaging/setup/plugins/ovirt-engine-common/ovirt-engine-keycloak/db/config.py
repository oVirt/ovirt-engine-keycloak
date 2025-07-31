#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Config plugin."""


import os
import gettext


from otopi import util
from otopi import plugin

from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Config plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            okkcons.ConfigEnv.OVIRT_ENGINE_KEYCLOAK_DB_BACKUP_DIR,
            okkcons.FileLocations.OVIRT_ENGINE_DEFAULT_KEYCLOAK_DB_BACKUP_DIR
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_VALIDATION,
        condition=lambda self: (
            self.environment[oengcommcons.KeycloakEnv.ENABLE]
        )
    )
    def _validation(self):
        path = self.environment[
            okkcons.ConfigEnv.OVIRT_ENGINE_KEYCLOAK_DB_BACKUP_DIR
        ]
        if not os.path.exists(path):
            raise RuntimeError(
                _(
                    'Backup path {path} not found'
                ).format(
                    path=path,
                )
            )


# vim: expandtab tabstop=4 shiftwidth=4
