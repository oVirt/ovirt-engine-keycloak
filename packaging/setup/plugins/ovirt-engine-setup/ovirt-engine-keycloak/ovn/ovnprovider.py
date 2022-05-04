#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Ovirt OVN provider SSO configuration plugin."""

import gettext

from otopi import plugin
from otopi import util

from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons

def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Ovirt OVN provider SSO configuration plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)


    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        before=(
            oenginecons.Stages.OVN_PROVIDER_CREDENTIALS_CUSTOMIZATION,
        ),
        after=(
            okkcons.Stages.KEYCLOAK_CREDENTIALS_SETUP,
        ),
        condition=lambda self: (
            self.environment[okkcons.CoreEnv.ENABLE] and
            self.environment[okkcons.ConfigEnv.ADMIN_PASSWORD] is not None
        )
    )
    def _setup_keycloak_ovirt_ovn_credentials(self):
        self.logger.debug(_('Setting Keycloak credentials '
                           'for ovn provider installation.'))
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_ADMIN_USER
        ] = self.environment[
            okkcons.ConfigEnv.OVIRT_ADMIN_USER_WITH_PROFILE
        ]
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_ADMIN_PASSWD
        ] = self.environment[
            okkcons.ConfigEnv.ADMIN_PASSWORD
        ]


# vim: expandtab tabstop=4 shiftwidth=4
