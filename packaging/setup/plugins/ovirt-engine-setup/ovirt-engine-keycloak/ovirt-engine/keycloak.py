#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""keycloak plugin."""


import gettext
import secrets

from otopi import constants as otopicons
from otopi import filetransaction
from otopi import plugin
from otopi import util

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-setup')


@util.export
class Plugin(plugin.PluginBase):
    """keycloak plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            okkcons.ConfigEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET,
            None
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup(self):
        self.environment[oengcommcons.ConfigEnv.JAVA_NEEDED] = True
        self.environment[oengcommcons.ConfigEnv.JBOSS_NEEDED] = True

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        name=okkcons.Stages.CLIENT_SECRET_GENERATED,
        condition=lambda self: (
            self.environment[oenginecons.CoreEnv.ENABLE] and
            self.environment[oenginecons.EngineDBEnv.NEW_DATABASE] and
            not self.environment[osetupcons.CoreEnv.DEVELOPER_MODE]
        )
    )
    def _misc(self):
        client_secret = secrets.token_urlsafe(nbytes=16)
        self.environment[okkcons.ConfigEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET] = client_secret

        userinfo_endpoint = self._build_endpoint_url("userinfo")
        token_endpoint = self._build_endpoint_url("token")
        logout_endpoint = self._build_endpoint_url("logout")
        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=okkcons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIG_KEYCLOAK,
                mode=0o640,
                owner=self.environment[oengcommcons.SystemEnv.USER_ROOT],
                group=self.environment[osetupcons.SystemEnv.GROUP_ENGINE],
                enforcePermissions=True,
                content=(
                    'KEYCLOAK_BUNDLED=true\n'
                    'ENGINE_SSO_ENABLE_EXTERNAL_SSO=true\n'
                    'ENGINE_SSO_EXTERNAL_SSO_LOGOUT_URI="${{ENGINE_URI}}/callback"\n'
                    'EXTERNAL_OIDC_CLIENT_ID={client_id}\n'
                    'EXTERNAL_OIDC_CLIENT_SECRET="{client_secret}"\n'
                    'EXTERNAL_OIDC_USER_INFO_END_POINT={userinfo_endpoint}\n'
                    'EXTERNAL_OIDC_TOKEN_END_POINT={token_endpoint}\n'
                    'EXTERNAL_OIDC_LOGOUT_END_POINT={logout_endpoint}\n'
                    'EXTERNAL_OIDC_HTTPS_PKI_TRUST_STORE="{trust_store}"\n'
                    'EXTERNAL_OIDC_HTTPS_PKI_TRUST_STORE_PASSWORD="{pki_trust_pass}"\n'
                    'EXTERNAL_OIDC_SSL_VERIFY_CHAIN=true\n'
                    'EXTERNAL_OIDC_SSL_VERIFY_HOST=false\n'
                ).format(
                    client_id=okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME,
                    client_secret=client_secret,
                    userinfo_endpoint=userinfo_endpoint,
                    token_endpoint=token_endpoint,
                    logout_endpoint=logout_endpoint,
                    pki_trust_pass=oenginecons.Const.PKI_PASSWORD,
                    trust_store=oenginecons.FileLocations.OVIRT_ENGINE_PKI_ENGINE_TRUST_STORE,
                ),
                modifiedList=self.environment[
                    otopicons.CoreEnv.MODIFIED_FILES
                ],
            )
        )

        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=okkcons.FileLocations.OVIRT_ENGINE_SERVICE_KEYCLOAK_AUTHN,
                mode=0o640,
                owner=self.environment[oengcommcons.SystemEnv.USER_ROOT],
                group=self.environment[osetupcons.SystemEnv.GROUP_ENGINE],
                enforcePermissions=True,
                content=(
                    'ovirt.engine.extension.name = {extension_name}-authn\n'
                    'ovirt.engine.extension.bindings.method = jbossmodule\n'
                    'ovirt.engine.extension.binding.jbossmodule.module = org.ovirt.engine.extension.aaa.misc\n'
                    'ovirt.engine.extension.binding.jbossmodule.class = '
                    'org.ovirt.engine.extension.aaa.misc.http.AuthnExtension\n'
                    'ovirt.engine.extension.provides = org.ovirt.engine.api.extensions.aaa.Authn\n'
                    'ovirt.engine.aaa.authn.profile.name = {profile}\n'
                    'ovirt.engine.aaa.authn.authz.plugin = {extension_name}-authz\n'
                    'ovirt.engine.aaa.authn.mapping.plugin = {extension_name}-http-mapping\n'
                    'config.artifact.name = HEADER\n'
                    'config.artifact.arg = OIDC_CLAIM_preferred_username\n'
                ).format(
                    extension_name=okkcons.Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME,
                    profile=okkcons.Const.OVIRT_ENGINE_KEYCLOAK_SSO_PROFILE,
                ),
                modifiedList=self.environment[
                    otopicons.CoreEnv.MODIFIED_FILES
                ],
            )
        )

        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=okkcons.FileLocations.OVIRT_ENGINE_SERVICE_KEYCLOAK_AUTHZ,
                mode=0o640,
                owner=self.environment[oengcommcons.SystemEnv.USER_ROOT],
                group=self.environment[osetupcons.SystemEnv.GROUP_ENGINE],
                enforcePermissions=True,
                content=(
                    'ovirt.engine.extension.name = {extension_name}-authz\n'
                    'ovirt.engine.extension.bindings.method = jbossmodule\n'
                    'ovirt.engine.extension.binding.jbossmodule.module = org.ovirt.engine.extension.aaa.misc\n'
                    'ovirt.engine.extension.binding.jbossmodule.class = '
                    'org.ovirt.engine.extension.aaa.misc.http.AuthzExtension\n'
                    'ovirt.engine.extension.provides = org.ovirt.engine.api.extensions.aaa.Authz\n'
                    'config.artifact.name.arg = OIDC_CLAIM_preferred_username\n'
                    'config.artifact.groups.arg = OIDC_CLAIM_groups\n'
                ).format(
                    extension_name=okkcons.Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME,
                ),
                modifiedList=self.environment[
                    otopicons.CoreEnv.MODIFIED_FILES
                ],
            )
        )

        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=okkcons.FileLocations.OVIRT_ENGINE_SERVICE_KEYCLOAK_HTTP_MAPPING,
                mode=0o640,
                owner=self.environment[oengcommcons.SystemEnv.USER_ROOT],
                group=self.environment[osetupcons.SystemEnv.GROUP_ENGINE],
                enforcePermissions=True,
                content=(
                    'ovirt.engine.extension.name = {extension_name}-http-mapping\n'
                    'ovirt.engine.extension.bindings.method = jbossmodule\n'
                    'ovirt.engine.extension.binding.jbossmodule.module = org.ovirt.engine.extension.aaa.misc\n'
                    'ovirt.engine.extension.binding.jbossmodule.class = '
                    'org.ovirt.engine.extension.aaa.misc.mapping.MappingExtension\n'
                    'ovirt.engine.extension.provides = org.ovirt.engine.api.extensions.aaa.Mapping\n'
                    'config.mapAuthRecord.type = regex\n'
                    'config.mapAuthRecord.regex.mustMatch = false\n'
                    'config.mapAuthRecord.regex.pattern = '
                    '^(?<user>.*?)((\\\\\\\\(?<at>@)(?<suffix>.*?)@.*)|(?<realm>@.*))$\n'
                    'config.mapAuthRecord.regex.replacement = ${{user}}${{at}}${{suffix}}\n'
                ).format(
                    extension_name=okkcons.Const.OVIRT_ENGINE_KEYCLOAK_SSO_EXTENSION_NAME,
                ),
                modifiedList=self.environment[
                    otopicons.CoreEnv.MODIFIED_FILES
                ],
            )
        )

    def _build_endpoint_url(self, endpoint):
        endpoint_url = 'https://{fqdn}/{keycloak_web_context}/realms/{realm}/protocol/openid-connect/{endpoint}'\
            .format(
                fqdn=self.environment[
                    oenginecons.ConfigEnv.ENGINE_FQDN
                ],
                keycloak_web_context=okkcons.Const.KEYCLOAK_WEB_CONTEXT,
                realm=okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                endpoint=endpoint
            )
        return endpoint_url


# vim: expandtab tabstop=4 shiftwidth=4
