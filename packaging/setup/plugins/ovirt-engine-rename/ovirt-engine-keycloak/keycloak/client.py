#
# ovirt-engine-rename -- ovirt engine rename
#
# Copyright oVirt Authors
# SPDX-License-Identifier: Apache-2.0
#
#

"""keycloak client plugin."""

import gettext

from otopi import plugin
from otopi import util
from ovirt_engine_setup import constants as osetupcons
from ovirt_engine_setup.engine_common import constants as oengcommcons
from ovirt_engine_setup.keycloak import constants as okkcons
from ovirt_engine_setup.engine_common import database


def _(m):
    return gettext.dgettext(message=m, domain='ovirt-engine-rename')


@util.export
class Plugin(plugin.PluginBase):
    """keycloak client plugin."""

    def __init__(self, context):
        super(Plugin, self).__init__(context=context)

    @plugin.event(
        stage=plugin.Stages.STAGE_MISC,
        after=(
                oengcommcons.Stages.DB_CONNECTION_AVAILABLE,
        )
    )
    def _update_client(self):
        """
        Update Root URL, Valid Redirect URIs, Base URL, Admin URL and Web Origins
        for ovirt-engine-internal client
        """
        self.logger.info(
            _(f"Update Keycloak client: {okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME}")
        )

        statement = database.Statement(
            environment=self.environment,
            dbenvkeys=okkcons.Const.KEYCLOAK_DB_ENV_KEYS,
        )

        try:
            # Get Client ID
            client_id = statement.execute(
                statement="""
                    SELECT id FROM public.client
                    WHERE client_id = %(client_name)s;
                """,
                args=dict(
                    client_name=okkcons.Const.KEYCLOAK_INTERNAL_CLIENT_NAME,
                ),
                ownConnection=True,
                transaction=False,
            )

            if not client_id:
                self.logger.warning(
                    _("Keycloak client not found")
                )
                return

            client_id = client_id[0].get('id')
            base_url = f'https://{self.environment[osetupcons.RenameEnv.FQDN]}'

            # Update client table
            statement.execute(
                statement="""
                    UPDATE public.client
                    SET
                        root_url =  %(url)s,
                        base_url =  %(url)s,
                        management_url =  %(url)s
                    WHERE id = %(client_id)s;
                """,
                args=dict(
                    url=base_url,
                    client_id=client_id
                ),
                ownConnection=True,
                transaction=False,
            )

            # Update web_origins table
            statement.execute(
                statement="""
                    UPDATE public.web_origins
                    SET
                        value = %(url)s
                    WHERE client_id = %(client_id)s;
                """,
                args=dict(
                    url=base_url,
                    client_id=client_id
                ),
                ownConnection=True,
                transaction=False,
            )

            # Update redirect_uris table
            statement.execute(
                statement="""
                    DELETE FROM public.redirect_uris
                    WHERE client_id = %(client_id)s;

                    INSERT INTO public.redirect_uris (client_id, value)
                    VALUES (%(client_id)s, %(uri)s);
                """,
                args=dict(
                    uri=f'{base_url}*',
                    client_id=client_id
                ),
                ownConnection=True,
                transaction=False,
            )

            self.logger.info(
                _("Keycloak client updated successfully")
            )

        except Exception as e:
            self.logger.error(
                _(f"Failed to update Keycloak client: {str(e)}")
            )


# vim: expandtab tabstop=4 shiftwidth=4
