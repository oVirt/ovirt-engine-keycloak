#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#

"""keycloak httpd internal sso openidc config plugin."""

import gettext
import secrets

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

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
            self.environment[oenginecons.CoreEnv.ENABLE] and
            self.environment[oenginecons.EngineDBEnv.NEW_DATABASE] and
            not self.environment[osetupcons.CoreEnv.DEVELOPER_MODE]
        ),
        after=(
            okkcons.Stages.CLIENT_SECRET_GENERATED,
        )
    )
    def _internalsso_openidc(self):
        self.environment[oengcommcons.ApacheEnv.NEED_RESTART] = True
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=self.environment[
                    okkcons.ApacheEnv.HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC
                ],
                content=outil.processTemplate(
                    template=(
                        okkcons.FileLocations.HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC_TEMPLATE
                    ),
                    subst={
                        '@CLIENT_SECRET@': self.environment[
                            okkcons.ConfigEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
                        ],
                        '@CLIENT_ID@':
                            okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME,
                        '@OVIRT_REALM@':
                            okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                        '@ENGINE_FQDN@': self.environment[
                            oenginecons.ConfigEnv.ENGINE_FQDN
                        ],
                        '@KEYCLOAK_WEB_CONTEXT@':
                            okkcons.Const.KEYCLOAK_WEB_CONTEXT,
                        '@RANDOM_CRYPTO_PASSPHRASE@':
                            secrets.token_urlsafe(nbytes=16),
                    },
                ),
                modifiedList=self.environment[
                    otopicons.CoreEnv.MODIFIED_FILES
                ],
            )
        )


# vim: expandtab tabstop=4 shiftwidth=4
