#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#

"""keycloak httpd internal sso openidc config plugin."""

import gettext

from otopi import constants as otopicons
from otopi import filetransaction
from otopi import plugin
from otopi import util
from ovirt_engine import util as outil
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """keycloak httpd internal sso openidc config plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            okkcons.ApacheEnv.HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC,
            okkcons.FileLocations.HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC,
        )
        self.environment.setdefault(
            oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_ID,
            okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME,
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
            self.environment[oengcommcons.KeycloakEnv.ENABLE] and
            not self.environment[oengcommcons.KeycloakEnv.CONFIGURED]
        ),
        after=(
            okkcons.Stages.CLIENT_SECRET_GENERATED,
        )
    )
    def _internalsso_openidc(self):
        uninstall_files = []
        self.environment[
            osetupcons.CoreEnv.REGISTER_UNINSTALL_GROUPS
        ].addFiles(
            group='ovirt_keycloak_files',
            fileList=uninstall_files,
        )

        self.environment[oengcommcons.ApacheEnv.NEED_RESTART] = True
        openidc_template = okkcons\
            .FileLocations\
            .HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC_TEMPLATE
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=self.environment[
                    okkcons.ApacheEnv
                        .HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC
                ],
                mode=0o640,
                enforcePermissions=True,
                content=outil.processTemplate(
                    template=(openidc_template),
                    subst={
                        '@CLIENT_SECRET@': self.environment[
                            oengcommcons.KeycloakEnv
                                .KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
                        ],
                        '@CLIENT_ID@':self.environment[
                            oengcommcons.KeycloakEnv
                                .KEYCLOAK_OVIRT_INTERNAL_CLIENT_ID
                        ],
                        '@OVIRT_REALM@':
                            okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                        '@ENGINE_FQDN@': self.environment[
                            oenginecons.ConfigEnv.ENGINE_FQDN
                        ],
                        '@KEYCLOAK_WEB_CONTEXT@':
                            okkcons.Const.KEYCLOAK_WEB_CONTEXT,
                    },
                ),
                modifiedList=uninstall_files,
            )
        )


# vim: expandtab tabstop=4 shiftwidth=4
