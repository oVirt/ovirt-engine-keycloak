#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


import gettext

from otopi import constants as otopicons
from otopi import util
from otopi import plugin

from ovirt_engine import configfile
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)


    @plugin.event(
        stage=plugin.Stages.STAGE_BOOT,
        before=(
            osetupcons.Stages.SECRETS_FILTERED_FROM_SETUP_ATTRS_MODULES,
        ),
    )
    def _boot(self):
        self.environment[
            osetupcons.CoreEnv.SETUP_ATTRS_MODULES
        ].append(
            okkcons,
        )
        self.environment[
            otopicons.CoreEnv.LOG_FILTER_KEYS
        ].append(
            "QUESTION/1/OVESETUP_CONFIG_ADMIN_SETUP"
        )
        self.environment[
            otopicons.CoreEnv.LOG_FILTER_KEYS
        ].append(
            "QUESTION/2/OVESETUP_CONFIG_ADMIN_SETUP"
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup(self):
        self.environment[
            osetupcons.CoreEnv.REGISTER_UNINSTALL_GROUPS
        ].createGroup(
            group='ovirt_keycloak_files',
            description='Keycloak files',
            optional=True,
        )


    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        config = configfile.ConfigFile([
            okkcons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIG_KEYCLOAK,
        ])

        if config.get('KEYCLOAK_BUNDLED') is not None:
            self.environment.setdefault(okkcons.CoreEnv.ENABLE,
                                        config.getboolean('KEYCLOAK_BUNDLED'))
        else:
            self.environment.setdefault(okkcons.CoreEnv.ENABLE, None)


# vim: expandtab tabstop=4 shiftwidth=4
