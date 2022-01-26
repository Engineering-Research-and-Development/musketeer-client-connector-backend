"""
Please note that the following code was developed for the project MUSKETEER in DRL funded by
the European Union under the Horizon 2020 Program.
The project started on 01/12/2018 and will be / was completed on 30/11/2021. Thus, in accordance
with article 30.3 of the Multi-Beneficiary General Model Grant Agreement of the Program, the above
limitations are in force until 30/11/2025.

Author: Engineering - Ingegneria Informatica S.p.A. (musketeer-team@eng.it).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from utils import platform_utils as utils

import logging
import communication_abstract_interface as ffl


LOGGER = logging.getLogger('auth')
LOGGER.setLevel(logging.DEBUG)


def login(credentials, username, password):

    try:
        context = utils.platform(credentials, username, password)
        ffl_user = ffl.Factory.user(context)

        with ffl_user:
            ffl_user.connect()

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err

    return True


def registration(credentials, username, password, org):

    try:
        fflapi = utils.get_comms_module()
        fflapi.create_user(username, password, org, credentials)

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err

    return


def change_password(credentials, username, password, new_password):

    try:

        context = utils.platform(credentials, username, password)
        user = ffl.Factory.user(context)

        with user:
            result = user.change_password(username, new_password)

        LOGGER.debug(result)
        LOGGER.info("Password changed")

        return result

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def deregister(credentials, username, password):

    try:

        context = utils.platform(credentials, username, password)
        user = ffl.Factory.user(context)

        with user:
            result = user.deregister()

        LOGGER.debug(result)
        LOGGER.info("User deregistered")

        return result

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def status(credentials, username, password):

    try:

        context = utils.platform(credentials, username, password)

        user = ffl.Factory.user(context)

        with user:

            LOGGER.info("Green status")

        return True

    except Exception as err:
        LOGGER.error('Red status: %s', err)
        return False
