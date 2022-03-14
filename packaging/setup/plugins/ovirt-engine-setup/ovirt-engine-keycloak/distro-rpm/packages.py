#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""
Package upgrade plugin.
"""

import gettext


from otopi import util
from otopi import plugin


from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine import constants as oenginecons
from ovirt_engine_setup.keycloak import constants as okkcons


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-keycloak')


@util.export
class Plugin(plugin.PluginBase):
    """
    Package upgrade plugin.
    """

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_INIT,
    )
    def _init(self):
        self.environment.setdefault(
            okkcons.RPMDistroEnv.PACKAGES,
            okkcons.Const.OVIRT_ENGINE_KEYCLOAK_PACKAGE_NAME
        )
        self.environment.setdefault(
            okkcons.RPMDistroEnv.PACKAGES_SETUP,
            okkcons.Const.OVIRT_ENGINE_KEYCLOAK_SETUP_PACKAGE_NAME
        )

    @plugin.event(
        stage=plugin.Stages.STAGE_CUSTOMIZATION,
        after=(
            okkcons.Stages.CORE_ENABLE,
        ),
        before=(
            osetupcons.Stages.DISTRO_RPM_PACKAGE_UPDATE_CHECK,
        ),
        condition=lambda self: (
            self.environment[oenginecons.CoreEnv.ENABLE] and
            self.environment[oenginecons.EngineDBEnv.NEW_DATABASE] and
            not self.environment[osetupcons.CoreEnv.DEVELOPER_MODE]
        )
    )
    def _customization(self):
        def tolist(s):
            return [e.strip() for e in s.split(',')]

        self.environment[
            osetupcons.RPMDistroEnv.PACKAGES_SETUP
        ].extend(
            tolist(self.environment[okkcons.RPMDistroEnv.PACKAGES_SETUP])
        )

        if self.environment[oenginecons.CoreEnv.ENABLE]:
            packages = tolist(
                self.environment[
                    okkcons.RPMDistroEnv.PACKAGES
                ]
            )
            self.environment[
                osetupcons.RPMDistroEnv.PACKAGES_UPGRADE_LIST
            ].append(
                {
                    'packages': packages,
                },
            )
            self.environment[
                osetupcons.RPMDistroEnv.VERSION_LOCK_APPLY
            ].extend(packages)

            self.environment[
                osetupcons.RPMDistroEnv.VERSION_LOCK_FILTER
            ].extend(
                tolist(
                    self.environment[okkcons.RPMDistroEnv.PACKAGES]
                )
            )
            self.environment[
                osetupcons.RPMDistroEnv.VERSION_LOCK_FILTER
            ].extend(
                tolist(
                    self.environment[okkcons.RPMDistroEnv.PACKAGES_SETUP]
                )
            )


# vim: expandtab tabstop=4 shiftwidth=4
