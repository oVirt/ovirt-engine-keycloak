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
from ovirt_engine_setup.engine_common import database
from ovirt_engine_setup.grafana_dwh import constants as ogdwhcons
from ovirt_engine_setup.keycloak import constants as okkcons
from ovirt_setup_lib import dialog


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


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
            oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET,
            None
        )
        self.environment.setdefault(
            oengcommcons.KeycloakEnv.ADMIN_PASSWORD,
            None
        )

        self.environment[
            okkcons.ConfigEnv.OVIRT_ADMIN_USER
        ] = okkcons.Const.OVIRT_ADMIN_USER

        keycloak_admin_with_profile = \
            '{user}@{profile}'.format(
                user=okkcons.Const.OVIRT_ADMIN_USER,
                profile=okkcons.Const.OVIRT_ENGINE_KEYCLOAK_SSO_PROFILE,
            )
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_ADMIN_USER_WITH_PROFILE
        ] = keycloak_admin_with_profile

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        name=okkcons.Stages.KEYCLOAK_CREDENTIALS_SETUP,
        before=(
            oenginecons.Stages.OVN_PROVIDER_CREDENTIALS_CUSTOMIZATION,
        ),
        after=(
            oengcommcons.Stages.ADMIN_PASSWORD_SET,
        ),
        condition=lambda self: (
            self.environment[oengcommcons.KeycloakEnv.ENABLE]
            and not self.environment[oengcommcons.KeycloakEnv.CONFIGURED]
            and self.environment[oengcommcons.KeycloakEnv.ADMIN_PASSWORD] is None
        )
    )
    def _setup_keycloak_ovirt_admin_credentials(self):
        password = None
        if self.environment[oenginecons.ConfigEnv.ADMIN_PASSWORD] is not None:
            use_engine_admin_password = dialog.queryBoolean(
                dialog=self.dialog,
                name='KEYCLOAK_USE_ENGINE_ADMIN_PASSWORD',
                note=_(
                    "Use Engine admin password as initial "
                    "keycloak admin password "
                    "(@VALUES@) [@DEFAULT@]: "
                ),
                prompt=True,
                default=True
            )
            if use_engine_admin_password:
                password = self.environment[
                    oenginecons.ConfigEnv.ADMIN_PASSWORD
                ]

        if password is None:
            password = dialog.queryPassword(
                dialog=self.dialog,
                logger=self.logger,
                env=self.environment,
                key=oengcommcons.KeycloakEnv.ADMIN_PASSWORD,
                note=_(
                    'Keycloak [admin] password: '
                ),
            )
        self.environment[oengcommcons.KeycloakEnv.ADMIN_PASSWORD] = password

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
            not self.environment[oengcommcons.KeycloakEnv.ENABLE]
            and self.environment[oenginecons.EngineDBEnv.NEW_DATABASE]
        )
    )
    def _misc_keycloak_disabled(self):
        uninstall_files = []
        self.environment[
            osetupcons.CoreEnv.REGISTER_UNINSTALL_GROUPS
        ].addFiles(
            group='ovirt_keycloak_files',
            fileList=uninstall_files,
        )

        self.environment[otopicons.CoreEnv.MAIN_TRANSACTION].append(
            filetransaction.FileTransaction(
                name=okkcons.FileLocations.OVIRT_ENGINE_SERVICE_CONFIG_KEYCLOAK,
                mode=0o640,
                owner=self.environment[oengcommcons.SystemEnv.USER_ROOT],
                group=self.environment[osetupcons.SystemEnv.GROUP_ENGINE],
                enforcePermissions=True,
                content=(('KEYCLOAK_BUNDLED=false')),
                modifiedList=uninstall_files,
            )
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        name=okkcons.Stages.CLIENT_SECRET_GENERATED,
        condition=lambda self: (
            self.environment[oengcommcons.KeycloakEnv.ENABLE]
            and not self.environment[oengcommcons.KeycloakEnv.CONFIGURED]
            and not self.environment[
                oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
            ]
        )
    )
    def _misc_client_secret(self):
        client_secret = secrets.token_urlsafe(nbytes=16)
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
        ] = client_secret

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        condition=lambda self: (
            self.environment[oengcommcons.KeycloakEnv.ENABLE]
        )
    )
    def _misc_keycloak_admin_url(self):
        keycloak_url = self._build_keycloak_url()
        self.environment[
            okkcons.ConfigEnv.KEYCLOAK_ADMIN_CONSOLE_URL
        ] = f"{keycloak_url}/admin"

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        name=okkcons.Stages.AUTH_ENDPOINTS_RESOLVED,
        after=(
            okkcons.Stages.DB_CREDENTIALS_AVAILABLE,
            okkcons.Stages.CLIENT_SECRET_GENERATED,
        ),
        before=(
            ogdwhcons.Stages.GRAFANA_CONFIG,
        ),
        condition=lambda self: (
            self.environment[oengcommcons.KeycloakEnv.ENABLE]
            and not self.environment[oengcommcons.KeycloakEnv.CONFIGURED]
        )
    )
    def _misc_keycloak_enabled(self):
        uninstall_files = []
        self.environment[
            osetupcons.CoreEnv.REGISTER_UNINSTALL_GROUPS
        ].addFiles(
            group='ovirt_keycloak_files',
            fileList=uninstall_files,
        )

        client_secret = self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
        ]

        keycloak_url = self._build_keycloak_url()
        userinfo_endpoint = self._build_endpoint_url(keycloak_url, "userinfo")
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_USERINFO_URL
        ] = userinfo_endpoint
        token_endpoint = self._build_endpoint_url(keycloak_url, "token")
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_TOKEN_URL
        ] = token_endpoint
        self.environment[
            oengcommcons.KeycloakEnv.KEYCLOAK_AUTH_URL
        ] = self._build_endpoint_url(keycloak_url, "auth")

        logout_endpoint = self._build_endpoint_url(keycloak_url, "logout")

        db_content = database.OvirtUtils(
            plugin=self,
            dbenvkeys=okkcons.Const.KEYCLOAK_DB_ENV_KEYS
        ).getDBConfig(
            prefix="KEYCLOAK"
        )

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
                    'KEYCLOAK_DB_MAX_CONNECTIONS={keycloak_db_max_connections}\n'
                    '{db_content}\n'
                ).format(
                    client_id=self.environment[
                        oengcommcons.KeycloakEnv.KEYCLOAK_OVIRT_INTERNAL_CLIENT_ID
                    ],
                    client_secret=client_secret,
                    userinfo_endpoint=userinfo_endpoint,
                    token_endpoint=token_endpoint,
                    logout_endpoint=logout_endpoint,
                    pki_trust_pass=oenginecons.Const.PKI_PASSWORD,
                    trust_store=oenginecons.FileLocations.OVIRT_ENGINE_PKI_ENGINE_TRUST_STORE,
                    keycloak_db_max_connections=okkcons.Const.KEYCLOAK_DB_MAX_CONNECTIONS,
                    db_content=db_content,
                ),
                modifiedList=uninstall_files,
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
                modifiedList=uninstall_files,
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
                modifiedList=uninstall_files,
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
                modifiedList=uninstall_files,
            )
        )

    def _build_keycloak_url(self):
        fqdn = self.environment[
            oenginecons.ConfigEnv.ENGINE_FQDN
        ]
        keycloak_web_context = okkcons.Const.KEYCLOAK_WEB_CONTEXT
        keycloak_url = f'https://{fqdn}/{keycloak_web_context}'
        return keycloak_url

    def _build_endpoint_url(self, keycloak_url, endpoint):
        return f"{keycloak_url}" \
               f"/realms/{okkcons.Const.KEYCLOAK_INTERNAL_REALM}" \
               f"/protocol/openid-connect/{endpoint}"


# vim: expandtab tabstop=4 shiftwidth=4
