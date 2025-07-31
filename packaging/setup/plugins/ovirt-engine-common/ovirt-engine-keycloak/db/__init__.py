#
# ovirt-engine-setup -- ovirt engine setup
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


from otopi import util


from . import config
from . import connection
from . import pgpass


@util.export
def createPlugins(context):
    config.Plugin(context=context)
    connection.Plugin(context=context)
    # TODO engine_connection plugin will used for user migration
    # engine_connection.Plugin(context=context)
    pgpass.Plugin(context=context)

# vim: expandtab tabstop=4 shiftwidth=4
