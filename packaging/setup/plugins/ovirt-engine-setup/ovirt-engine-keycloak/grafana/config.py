#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Grafana SSO configuration plugin."""

import gettext

from otopi import plugin
from otopi import util

from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.grafana_dwh import constants as ogdwhcons
from ovirt_engine_setup.keycloak import constants as okkcons

def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Grafana SSO configuration plugin"""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        before=(
            ogdwhcons.Stages.GRAFANA_CONFIG,
        ),
        condition=lambda self: (
            self.environment[oengcommcons.KeycloakEnv.ENABLE]
        )
    )
    def _init(self):
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_GRAFANA_ADMIN_ROLE
        ] = okkcons.Const.GRAFANA_ADMIN_ROLE
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_GRAFANA_EDITOR_ROLE
        ] = okkcons.Const.GRAFANA_EDITOR_ROLE
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_GRAFANA_VIEWER_ROLE
        ] = okkcons.Const.GRAFANA_VIEWER_ROLE


# vim: expandtab tabstop=4 shiftwidth=4
