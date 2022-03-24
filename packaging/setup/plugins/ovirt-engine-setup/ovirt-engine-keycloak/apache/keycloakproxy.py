#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#

"""keycloak httpd proxy plugin."""

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
    """keycloak httpd proxy plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            okkcons.ApacheEnv.HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK,
            okkcons.FileLocations.HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
            self.environment[okkcons.CoreEnv.ENABLE] and
            self.environment[okkcons.DBEnv.NEW_DATABASE]
        )
    )
    def _httpd_keycloak_misc(self):
        uninstall_files = []
        self.environment[
            osetupcons.CoreEnv.REGISTER_UNINSTALL_GROUPS
        ].addFiles(
            group='ovirt_keycloak_files',
            fileList=uninstall_files,
        )

        self.environment[oengcommcons.ApacheEnv.NEED_RESTART] = True
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=self.environment[
                    okkcons.ApacheEnv.HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK
                ],
                content=outil.processTemplate(
                    template=(
                        okkcons.FileLocations.HTTPD_CONF_OVIRT_ENGINE_KEYCLOAK_TEMPLATE
                    ),
                    subst={
                        '@JBOSS_AJP_PORT@': self.environment[
                            oengcommcons.ConfigEnv.JBOSS_AJP_PORT
                        ],
                    },
                ),
                modifiedList=uninstall_files,
            )
        )

# vim: expandtab tabstop=4 shiftwidth=4
