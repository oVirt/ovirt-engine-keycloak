#
# ovirt-engine-rename -- ovirt engine rename
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
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons
import re


PATTERNS = [
    r'(^\s+OIDCProviderMetadataURL https://).+(\/ovirt-engine.*)',
    r'(^\s+OIDCRedirectURI https:\/\/).+(\/ovirt-engine.*)',
    r'(^\s+OIDCDefaultURL https:\/\/).+(\/ovirt-engine.*)',
    r'(^\s+OIDCOAuthIntrospectionEndpoint https:\/\/).+(\/ovirt-engine.*)'
]

def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-rename')


@util.export
class Plugin(plugin.PluginBase):
    """keycloak httpd internal sso openidc config plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup(self):
        self.environment[
            osetupcons.RenameEnv.FILES_TO_BE_MODIFIED
        ].append(okkcons.FileLocations.HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC)

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
                self.environment[oengcommcons.KeycloakEnv.ENABLE]
        )
    )
    def _internalsso_reconfigure(self):
        """
        Configuring parameters (see PATTERNS) in internalsso-openidc.conf with new FQDN
        """
        config_path = okkcons.FileLocations.HTTPD_CONF_OVIRT_ENGINE_INTERNAL_SSO_OPENIDC

        REPLACEMENT = r'\g<1>{host}\g<2>'.format(
            host=self.environment[osetupcons.RenameEnv.FQDN]
        )

        try:
            with open(config_path, 'r') as file:
                content = file.read()

            for pattern in PATTERNS:
                content = re.sub(
                    pattern=pattern,
                    repl=REPLACEMENT,
                    string=content,
                    flags=re.MULTILINE
                )

            self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
                filetransaction.FileTransaction(
                    name=config_path,
                    content=content,
                    modifiedList=self.environment[
                        otopicons.CoreEnv.MODIFIED_FILES
                    ],
                )
            )

        except Exception as e:
            raise RuntimeError(
                _(f"Failed to update configuration file '{config_path}': {str(e)}")
            )


# vim: expandtab tabstop=4 shiftwidth=4
