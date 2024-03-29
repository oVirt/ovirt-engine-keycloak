#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


"""Keycloak database plugins."""


from otopi import util

from . import connection


@util.export
def createPlugins(context):
    connection.Plugin(context=context)


# vim: expandtab tabstop=4 shiftwidth=4
