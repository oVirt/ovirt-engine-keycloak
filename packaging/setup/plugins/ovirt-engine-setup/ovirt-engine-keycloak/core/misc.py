#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


import gettext


from otopi import util
from otopi import plugin

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons
from ovirt_setup_lib import dialog


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        name=okkcons.Stages.CORE_ENABLE,
        before=(
            okkcons.Stages.KEYCLOAK_CREDENTIALS_SETUP,
            oenginecons.Stages.OVN_PROVIDER_CREDENTIALS_CUSTOMIZATION,
        ),
        after=(
            osetupcons.Stages.DIALOG_TITLES_S_PRODUCT_OPTIONS,
        ),
        condition=lambda self: (
            self.environment[oenginecons.CoreEnv.ENABLE] and
            not self.environment[osetupcons.CoreEnv.DEVELOPER_MODE]
        ),
    )
    def _customization(self):
        first_installation = self.environment[
            oenginecons.EngineDBEnv.NEW_DATABASE
        ] and self.environment[
            okkcons.CoreEnv.ENABLE
        ] is None

        reconfiguration = not self.environment[
            oenginecons.EngineDBEnv.NEW_DATABASE
        ] and self.environment[
            okkcons.CoreEnv.ENABLE
        ] is not None

        if first_installation or reconfiguration:
            self.dialog.note(
                text=_(
                    '\n* Please note * : Keycloak is now deprecating '
                    'AAA/JDBC authentication module. '
                    '\nIt is highly recommended to install '
                    'Keycloak based authentication. '
                )
            )
            self.environment[
                okkcons.CoreEnv.ENABLE
            ] = dialog.queryBoolean(
                dialog=self.dialog,
                name='OVESETUP_KEYCLOAK_ENABLE',
                note=_(
                    'Configure Keycloak on this host '
                    '(@VALUES@) [@DEFAULT@]: '
                ),
                prompt=True,
                default=True,

            )

            if not self.environment[okkcons.CoreEnv.ENABLE]:
                self.dialog.note(
                    text=_(
                        '\nAre you really sure not to install '
                        'internal Keycloak based authentication? ' 
                        '\nAAA modules are being deprecated '
                    )
                )
                self.environment[
                    okkcons.CoreEnv.ENABLE
                ] = dialog.queryBoolean(
                    dialog=self.dialog,
                    name='OVESETUP_KEYCLOAK_ENABLE',
                    note=_(
                        'Configure Keycloak on this host '
                        '(@VALUES@) [@DEFAULT@]: '
                    ),
                    prompt=True,
                    default=True,
                )

            self.environment[oengcommcons.KeycloakEnv.KEYCLOAK_ENABLED] = \
                self.environment[okkcons.CoreEnv.ENABLE]


# vim: expandtab tabstop=4 shiftwidth=4
