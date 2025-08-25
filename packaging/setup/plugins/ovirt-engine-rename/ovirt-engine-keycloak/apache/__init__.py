#
# ovirt-engine-rename -- ovirt engine rename
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#


from otopi import util


from . import internalsso


@util.export
def createPlugins(context):
    internalsso.Plugin(context=context)


# vim: expandtab tabstop=4 shiftwidth=4
