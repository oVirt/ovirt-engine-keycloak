
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#

"""Ovirt engine keycloak initial admin user plugin."""

import datetime
import gettext
import os

from otopi import plugin
from otopi import util

from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup import util as osetuputil
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """Ovirt engine keycloak initial admin user plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_SETUP,
    )
    def _setup(self):
        self.environment.setdefault(
            okkcons.ConfigEnv.KEYCLOAK_ADD_USER_SCRIPT,
            os.path.join(
                self.environment[oengcommcons.ConfigEnv.JBOSS_HOME],
                "bin",
                okkcons.Const.KEYCLOAK_ADD_USER_SCRIPT,
            ),
        )
        self.environment.setdefault(
            okkcons.ConfigEnv.KEYCLOAK_WRAPPER_SCRIPT,
            okkcons.FileLocations.KEYCLOAK_WRAPPER_SCRIPT,
        )


    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        after=(
            okkcons.Stages.KEYCLOAK_CREDENTIALS_SETUP,
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
    def _create_admin(self):
        password = self.environment[okkcons.ConfigEnv.ADMIN_PASSWORD]
        if password:
            self.logger.info(_('Creating initial Keycloak admin user'))
            # TODO consider using transaction
            #  ie. be implementing transaction.TransactionElement
            # current implementation is idempotent because in the line below
            # already existing json configuration files are renamed with
            # proper datetime based suffix make place for newly created
            # add user config file
            self._safely_keep_existing_user_json_file()
            # TODO handle upgrade
            self.execute(
                args=(
                    self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_WRAPPER_SCRIPT
                    ],
                    '-r', okkcons.Const.KEYCLOAK_MASTER_REALM,
                    '-u', self.environment[
                        oenginecons.ConfigEnv.ADMIN_USER
                    ].rsplit('@', 1)[0],
                    '--sc', okkcons.FileLocations.OVIRT_ENGINE_CONFIG_DIR,
                ),
                envAppend={
                    'JAVA_OPTS': '-Dcom.redhat.fips=false',
                    'ADMIN_PASSWORD': password,
                    'KK_TOOL': self.environment[
                        okkcons.ConfigEnv.KEYCLOAK_ADD_USER_SCRIPT
                    ]
                },
            )
            os.chown(
                okkcons.FileLocations.KEYCLOAK_ADD_INITIAL_ADMIN_FILE,
                osetuputil.getUid(
                    self.environment[osetupcons.SystemEnv.USER_ENGINE],
                ),
                osetuputil.getGid(
                    self.environment[osetupcons.SystemEnv.GROUP_ENGINE],
                ),
            )
            os.chmod(
                okkcons.FileLocations.KEYCLOAK_ADD_INITIAL_ADMIN_FILE,
                0o600
            )
            self.environment[oengcommcons.ApacheEnv.NEED_RESTART] = True
        else:
            self.logger.info(_('Not creating initial Keycloak admin user '
                               'because admin password is missing'))

    @staticmethod
    def _safely_keep_existing_user_json_file():
        if os.path.exists(
            okkcons.FileLocations.KEYCLOAK_ADD_INITIAL_ADMIN_FILE
        ):
            now = datetime.datetime.now()
            timestamp = str(now.strftime("%Y%m%d_%H-%M-%S"))
            backup_file = ".".join([
                okkcons.FileLocations.KEYCLOAK_ADD_INITIAL_ADMIN_FILE,
                timestamp
            ])
            os.renames(
                okkcons.FileLocations.KEYCLOAK_ADD_INITIAL_ADMIN_FILE,
                backup_file
            )


# vim: expandtab tabstop=4 shiftwidth=4
