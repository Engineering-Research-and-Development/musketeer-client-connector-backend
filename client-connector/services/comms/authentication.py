from utils import platform_utils as utils

import logging
import communication_abstract_interface as ffl


LOGGER = logging.getLogger('auth')
LOGGER.setLevel(logging.DEBUG)


def login(credentials, user, password):

    try:
        context = utils.platform(credentials, user, password)
        ffl_user = ffl.Factory.user(context)

        with ffl_user:
            ffl_user.connect()

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err

    return True


def registration(credentials, user, password, org):

    try:
        context = utils.platform(credentials)
        ffl_user = ffl.Factory.user(context)

        with ffl_user:
            ffl_user.create_user(user, password, org)

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err

    return
