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
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment[oengcommcons.KeycloakEnv.SUPPORTED] = True

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        name=okkcons.Stages.CORE_ENABLE,
        before=(
            okkcons.Stages.KEYCLOAK_CREDENTIALS_SETUP,
            oenginecons.Stages.OVN_PROVIDER_CREDENTIALS_CUSTOMIZATION,
        ),
        after=(
            oenginecons.Stages.CORE_ENABLE,
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
            oengcommcons.KeycloakEnv.ENABLE
        ] is None

        # Notice: this condition is not ready
        # for --reconfigure-optional-components
        # because of the following scenario
        # There is already existing oVirt environment
        # ( < 4.5.1 ). In this case ENABLE flag is None,
        # CONFIGURED is None and
        # oenginecons.EngineDBEnv.NEW_DATABASE is False
        # We cannot here drop NEW_DATABASE condition becuase
        # the requirement is not to even ask for keycloak
        # in case of upgrading from non-keycloak existing
        # oVirt installation.
        # In order to enforce keycloak activation use:
        #
        # $ engine-setup \
        #    --otopi-environment="OVESETUP_CONFIG/keycloakEnable=bool:True"
        #
        if first_installation:
            self.dialog.note(
                text=_(
                    '\n* Please note * : Keycloak is now deprecating '
                    'AAA/JDBC authentication module. '
                    '\nIt is highly recommended to install '
                    'Keycloak based authentication. '
                )
            )
            self.environment[
                oengcommcons.KeycloakEnv.ENABLE
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

            if not self.environment[oengcommcons.KeycloakEnv.ENABLE]:
                self.dialog.note(
                    text=_(
                        '\nAre you really sure not to install '
                        'internal Keycloak based authentication? '
                        '\nAAA modules are being deprecated '
                    )
                )
                self.environment[
                    oengcommcons.KeycloakEnv.ENABLE
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


# vim: expandtab tabstop=4 shiftwidth=4
