
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#

"""Ovirt engine keycloak internal sso realm configuration plugin."""

import gettext
import json
import os
import time

from otopi import plugin
from otopi import util

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Ovirt engine keycloak internal sso realm configuration plugin."""

    KCADM_ENV = {
        'KC_OPTS':'-Dcom.redhat.fips=false'
    }

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup(self):
        self.environment.setdefault(
            okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT,
            os.path.join(
                self.environment[oengcommcons.ConfigEnv.JBOSS_HOME],
                "bin",
                okkcons.Const.KEYCLOAK_CLI_ADMIN_SCRIPT,
            ),
        )
        self.environment.setdefault(
            okkcons.ConfigEnv.KEYCLOAK_WRAPPER_SCRIPT,
            okkcons.FileLocations.KEYCLOAK_WRAPPER_SCRIPT,
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        after=(
            oengcommcons.Stages.CORE_ENGINE_START,
        ),
        condition=lambda self: (
            self.environment[okkcons.CoreEnv.ENABLE] and
            self.environment[okkcons.DBEnv.NEW_DATABASE] and
            self.environment[
                oenginecons.EngineDBEnv.JUST_RESTORED
            ] is not True and
            not self.environment[
                osetupcons.CoreEnv.ACTION
            ] == osetupcons.Const.ACTION_PROVISIONDB
        ),
    )
    def _setup_ovirt(self):
        password = self.environment.get(okkcons.ConfigEnv.ADMIN_PASSWORD)
        if password:
            self.logger.info('Start with setting up Keycloak for Ovirt Engine')

            # TODO sometimes keycloak app is not ready soon enough  resulting
            # in 503 error on attempt to use kcadm.sh / api
            # This sleep is only a workaround until better way is found
            time.sleep(30)

            self._setup_keystore()

            self.logger.debug(_('Logging in with Keycloak CLI admin'))
            self._login(
                passwd=password
            )

            self.logger.debug('Creating realm with Keycloak CLI admin')
            self._setup_realm()

            # please note that client_id is an id (hash) and
            # is not the human readable
            # 'client id' defined as
            # okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME
            self.logger.debug(
                'Creating internal client in with Keycloak CLI admin'
            )
            client_id = self._setup_client()

            for scope in okkcons.Const.OVIRT_CLIENT_SCOPES:
                self._setup_client_scope(
                    scope_name=scope,
                    client_id=client_id,
                )

            self._setup_protocol_mapper_username(
                client_id=client_id
            )
            self._setup_protocol_mapper_groups(
                client_id=client_id
            )
            self._setup_protocol_mapper_user_realm_role(
                client_id=client_id
            )

            administrator_group_id = self._setup_ovirt_administrator_group()
            self._setup_internal_admin_user(
                administrator_group_id=administrator_group_id,
                password=password,
            )

            for role in okkcons.Const.GRAFANA_USER_ROLES:
                # all required roles created up front
                # initially only 'admin' in use
                self._add_role(
                    name=role,
                    description=f"Grafana '{role}' role"
                )
            self._assign_role_to_user(
                username=okkcons.Const.OVIRT_ADMIN_USER,
                role_name=okkcons.Const.GRAFANA_ADMIN_ROLE
            )
            self.logger.info('Done with setting up Keycloak for Ovirt Engine')

    def _setup_keystore(self):
        self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'config',
                'truststore',
                '--trustpass', oenginecons.Const.PKI_PASSWORD,
                oenginecons.FileLocations.OVIRT_ENGINE_PKI_ENGINE_TRUST_STORE
            ),
            envAppend=self.KCADM_ENV,
        )

    def _login(self, passwd):
        engine_host = self.environment[
            oenginecons.ConfigEnv.ENGINE_FQDN
        ]

        keycloak_server_url = os.path.join(
            engine_host,
            okkcons.Const.KEYCLOAK_WEB_CONTEXT,
        )

        envs = self.KCADM_ENV.copy()
        envs['ADMIN_PASSWORD'] = passwd
        envs['KK_TOOL'] = self.environment[
            okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
        ]
        self.execute(
            args=(
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_WRAPPER_SCRIPT
                ],
                'config',
                'credentials',
                '--server', 'https://{}'.format(keycloak_server_url),
                '--realm', okkcons.Const.KEYCLOAK_MASTER_REALM,
                '--user', self.environment[
                    oenginecons.ConfigEnv.ADMIN_USER
                ].rsplit('@', 1)[0],
            ),
            envAppend=envs
        )

    def _setup_realm(self):
        realm_id = self._get_realm_id(
            realm_name=okkcons.Const.KEYCLOAK_INTERNAL_REALM
        )

        if realm_id is None:
            rc, stdout, stderr = self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    'realms',
                    '-s', 'realm=%s' % okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'enabled=true',
                    '-i'
                ),
                envAppend=self.KCADM_ENV,
            )
            realm_id = self._results(rc, stdout)
        else:
            self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'update',
                    'realms/%s' % okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'enabled=true',
                ),
                envAppend=self.KCADM_ENV,
            )
        return realm_id

    def _setup_client(self):
        cid = self._get_client_id(
            client_id_name=okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME
        )
        envs = self.KCADM_ENV.copy()
        envs['CLIENT_SECRET'] = self.environment[
            okkcons.ConfigEnv
                .KEYCLOAK_OVIRT_INTERNAL_CLIENT_SECRET
        ]
        envs['KK_TOOL']=self.environment[
            okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
        ]
        if cid is None:
            rc, stdout, stderr = self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_WRAPPER_SCRIPT
                    ],
                    'create',
                    'clients',
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'enabled=true',
                    '-s', 'clientId={}'.format(
                        okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME
                    ),
                    '-s', 'clientAuthenticatorType=client-secret',
                    '-i',
                ),
                envAppend=envs,
            )
            cid = self._results(rc, stdout)

        # Once basic client id exists
        # then let's update it with desired configuration
        engine_host = self.environment[
            oenginecons.ConfigEnv.ENGINE_FQDN
        ]
        self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'update',
                'clients/{}'.format(cid),
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '-s', 'directAccessGrantsEnabled=true',
                '-s', 'rootUrl=https://{}'.format(engine_host),
                '-s', 'adminUrl=https://{}'.format(engine_host),
                '-s', 'baseUrl=https://{}'.format(engine_host),
                '-s', 'redirectUris=["https://{}*"]'.format(engine_host),
                '-s', 'webOrigins=["https://{}"]'.format(engine_host),
                '-s', 'attributes."access.token.lifespan"=17280',
            ),
            envAppend=self.KCADM_ENV,
        )
        return cid

    def _setup_client_scope(self, scope_name, client_id):
        client_scope_id = self._get_client_scope_id(
            scope_name=scope_name
        )

        if client_scope_id is None:
            rc, stdout, stderr = self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    'client-scopes',
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'name={}'.format(scope_name),
                    '-s', 'protocol=openid-connect',
                    '-i',
                ),
                envAppend=self.KCADM_ENV,
            )
            client_scope_id = self._results(rc, stdout)

        self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'update',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                "clients/{client_id}/optional-client-scopes/{client_scope_id}"
                .format(
                    client_id=client_id,
                    client_scope_id=client_scope_id
                ),
            ),
            envAppend=self.KCADM_ENV,
        )
        return client_scope_id

    def _setup_protocol_mapper_username(self, client_id):
        if self._get_protocol_mapper_id(
            protocol_mapper_name='username',
            client_id=client_id,
        ) is None:
            self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    'clients/{}/protocol-mappers/models'.format(client_id),
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'name=username',
                    '-s', 'protocol=openid-connect',
                    '-s', 'protocolMapper=oidc-usermodel-property-mapper',
                    '-s', 'config."id.token.claim"="true"',
                    '-s', 'config."access.token.claim"="true"',
                    '-s', 'config."userinfo.token.claim"="true"',
                    '-s', 'config."claim.name"="preferred_username"',
                    '-s', 'config."user.attribute"="username"',
                    '-s', 'config."jsonType.label"="String"',
                    '-i',
                ),
                envAppend=self.KCADM_ENV,
            )

    def _setup_protocol_mapper_groups(self, client_id):
        if self._get_protocol_mapper_id(
            protocol_mapper_name='groups',
            client_id=client_id,
        ) is None:
            self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    'clients/{}/protocol-mappers/models'.format(client_id),
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'name=groups',
                    '-s', 'protocol=openid-connect',
                    '-s', 'protocolMapper=oidc-group-membership-mapper',
                    '-s', 'config."id.token.claim"="true"',
                    '-s', 'config."access.token.claim"="true"',
                    '-s', 'config."userinfo.token.claim"="true"',
                    '-s', 'config."claim.name"="groups"',
                    '-s', 'config."full.path"="true"',
                    '-i',
                ),
                envAppend=self.KCADM_ENV,
            )

    def _setup_protocol_mapper_user_realm_role(self, client_id):
        if self._get_protocol_mapper_id(
                protocol_mapper_name='realm role',
                client_id=client_id,
        ) is None:
            self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    f'clients/{client_id}/protocol-mappers/models',
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'name=realm role',
                    '-s', 'protocol=openid-connect',
                    '-s', 'protocolMapper=oidc-usermodel-realm-role-mapper',
                    '-s', 'config."id.token.claim"="true"',
                    '-s', 'config."access.token.claim"="true"',
                    '-s', 'config."userinfo.token.claim"="true"',
                    '-s', 'config."claim.name"="realm_access.roles"',
                    '-s', 'config."jsonType.label"="String"',
                    '-s', 'config."multivalued"="true"',
                    '-i',
                ),
                envAppend=self.KCADM_ENV,
            )

    def _setup_ovirt_administrator_group(self):
        group_id = self._get_group_id(
            okkcons.Const.OVIRT_ADMINISTRATOR_USER_GROUP_NAME
        )
        if group_id is None:
            rc, stdout, stderr = self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    'groups',
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', 'name={}'.format(
                        okkcons.Const.OVIRT_ADMINISTRATOR_USER_GROUP_NAME
                    ),
                    '-i',
                ),
                envAppend=self.KCADM_ENV,
            )
            group_id = self._results(rc, stdout)
        return group_id

    def _setup_internal_admin_user(self, password, administrator_group_id):
        admin_user_id = self._get_user_id(okkcons.Const.OVIRT_ADMIN_USER)
        if admin_user_id is None:
            rc, stdout, stderr = self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    'users',
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', f'username={okkcons.Const.OVIRT_ADMIN_USER}',
                    '-s', f'email={okkcons.Const.OVIRT_ADMIN_USER_EMAIL}',
                    '-s', 'enabled=true',
                    '-i',
                ),
                envAppend=self.KCADM_ENV,
            )
            admin_user_id = self._results(rc, stdout)

        # set admin password
        envs = self.KCADM_ENV.copy()
        envs['USER_NEW_PASSWORD'] = password
        envs['KK_TOOL']=self.environment[
            okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
        ]
        self.execute(
            args=(
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_WRAPPER_SCRIPT
                ],
                'set-password',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--username', okkcons.Const.OVIRT_ADMIN_USER,
            ),
            envAppend=envs,
        )

        # assign admin to ovirt-administrator group
        self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'update',
                'users/{user_id}/groups/{group_id}'.format(
                    user_id=admin_user_id,
                    group_id=administrator_group_id,
                ),
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '-s', 'realm={}'.format(okkcons.Const.KEYCLOAK_INTERNAL_REALM),
                '-s', 'userId={}'.format(admin_user_id),
                '-s', 'groupId={}'.format(administrator_group_id),
                '-n',
            ),
            envAppend=self.KCADM_ENV,
        )

    def _add_role(self, name, description):
        role_id = self._get_role_id(role_name=name)
        if role_id is None:
            rc, stdout, stderr = self.execute(
                (
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                    ],
                    'create',
                    'roles',
                    '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                    '-s', f"name={name}",
                    '-s', f"description={description}",
                    '-i',
                ),
                envAppend=self.KCADM_ENV,
            )
            role_id = self._results(rc, stdout)
        return role_id

    def _assign_role_to_user(self, username, role_name):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get-roles',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--uusername', username,
                '--rolename', role_name
            ),
            envAppend=self.KCADM_ENV,
        )

    def _get_role_id(self, role_name):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get-roles',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--fields', 'id,name',
            ),
            envAppend=self.KCADM_ENV,
        )
        return self._get_id_from_response(
            self._results(rc, stdout),
            'name', role_name
        )

    def _get_user_id(self, username):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get',
                'users',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--fields', 'id,username',
            ),
            envAppend=self.KCADM_ENV,
        )
        return self._get_id_from_response(
            self._results(rc, stdout),
            'username', username
        )

    def _get_client_id(self, client_id_name):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get',
                'clients',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--fields', 'id,clientId',
            ),
            envAppend=self.KCADM_ENV,
        )
        return self._get_id_from_response(
            self._results(rc, stdout),
            'clientId',
            client_id_name
        )

    def _get_realm_id(self, realm_name):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get',
                'realms',
                '--fields', 'id,realm',
            ),
            envAppend=self.KCADM_ENV,
        )
        return self._get_id_from_response(
            self._results(rc, stdout),
            'realm',
            realm_name
        )

    def _get_client_scope_id(self, scope_name):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get',
                'client-scopes',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--fields', 'id,name',
            ),
            envAppend=self.KCADM_ENV,
        )
        return self._get_id_from_response(
            self._results(rc, stdout),
            'name',
            scope_name
        )

    def _get_protocol_mapper_id(self, protocol_mapper_name, client_id):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get',
                'clients/{}/protocol-mappers/models'.format(client_id),
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--fields', 'id,name',
            ),
            envAppend=self.KCADM_ENV,
        )
        return self._get_id_from_response(
            self._results(rc, stdout),
            'name',
            protocol_mapper_name
        )

    def _get_group_id(self, group_name):
        rc, stdout, stderr = self.execute(
            (
                self.environment[
                    okkcons.ConfigEnv.KEYCLOAK_CLI_ADMIN_SCRIPT
                ],
                'get',
                'groups',
                '-r', okkcons.Const.KEYCLOAK_INTERNAL_REALM,
                '--fields', 'id,name',
            ),
            envAppend=self.KCADM_ENV,
        )
        return self._get_id_from_response(
            self._results(rc, stdout),
            'name',
            group_name
        )

    @staticmethod
    def _get_id_from_response(response, query_field, query_value):
        items = json.loads(response.replace('\'', '\"'))
        for item in items:
            if item[query_field] == query_value:
                return item['id']
        return None

    @staticmethod
    def _results(rc, out):
        if rc == 1:
            raise RuntimeError("Error configuring internal Keycloak instance."
                               " Check setup log for details")
        return ''.join(out)

    @plugin.event(
        stage=plugin.Stages.STAGE_CLOSEUP,
        before=(
            osetupcons.Stages.DIALOG_TITLES_E_SUMMARY,
        ),
        after=(
            osetupcons.Stages.DIALOG_TITLES_S_SUMMARY,
        ),
        condition=lambda self: (
            self.environment[okkcons.CoreEnv.ENABLE] and
            self.environment[okkcons.DBEnv.NEW_DATABASE]
        )
    )
    def _closeup(self):
        self.dialog.note(
            text=_(
                "Please use the user '{keycloakadmin}' and password specified in "
                "order to login to Keycloak admin console\n"
                "Please use the user '{user}' and password specified in "
                "order to login using Keycloak SSO"
            ).format(
                user=okkcons.Const.OVIRT_ADMIN_USER,
                keycloakadmin=self.environment[
                    oenginecons.ConfigEnv.ADMIN_USER
                ].rsplit('@', 1)[0],
            ),
        )


# vim: expandtab tabstop=4 shiftwidth=4
