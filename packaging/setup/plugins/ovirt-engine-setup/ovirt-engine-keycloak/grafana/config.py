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
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        after=(
            okkcons.Stages.CORE_ENABLE,
        ),
        condition=lambda self: (
            self.environment[okkcons.CoreEnv.ENABLE]
        )
    )
    def _customize(self):
        self.environment[ogdwhcons.KeycloakEnv.KEYCLOAK_ENABLED] = \
            self.environment[okkcons.CoreEnv.ENABLE]

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        after=(
            okkcons.Stages.CLIENT_SECRET_GENERATED,
            okkcons.Stages.AUTH_ENDPOINTS_RESOLVED,
        ),
        before=(
            ogdwhcons.Stages.GRAFANA_CONFIG,
        ),
        condition=lambda self: (
            self.environment[okkcons.CoreEnv.ENABLE]
        )
    )
    def _misc(self):
        self.environment[
            ogdwhcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
        ] = self.environment[
            okkcons.ConfigEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
        ]

        self.environment[
            ogdwhcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_ID
        ] = okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME

        self.environment[ogdwhcons.KeycloakEnv.KEYCLOAK_AUTH_URL] = \
            self.environment[okkcons.ConfigEnv.KEYCLOAK_AUTH_URL]

        self.environment[ogdwhcons.KeycloakEnv.KEYCLOAK_TOKEN_URL] = \
            self.environment[okkcons.ConfigEnv.KEYCLOAK_TOKEN_URL]

        self.environment[ogdwhcons.KeycloakEnv.KEYCLOAK_USERINFO_URL] = \
            self.environment[okkcons.ConfigEnv.KEYCLOAK_USERINFO_URL]

        self.environment[
            ogdwhcons.KeycloakEnv.KEYCLOAK_GRAFANA_ADMIN_ROLE
        ] = okkcons.Const.GRAFANA_ADMIN_ROLE
        self.environment[
            ogdwhcons.KeycloakEnv.KEYCLOAK_GRAFANA_EDITOR_ROLE
        ] = okkcons.Const.GRAFANA_EDITOR_ROLE
        self.environment[
            ogdwhcons.KeycloakEnv.KEYCLOAK_GRAFANA_VIEWER_ROLE
        ] = okkcons.Const.GRAFANA_VIEWER_ROLE


# vim: expandtab tabstop=4 shiftwidth=4
