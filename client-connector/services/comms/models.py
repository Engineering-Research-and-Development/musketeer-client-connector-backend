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
import os
import json
# import tensorflow as tf
# import pickle


LOGGER = logging.getLogger('comms.models')
LOGGER.setLevel(logging.DEBUG)

# global graph
# graph = tf.compat.v1.get_default_graph()


def get_models(credentials, user, password):

    try:

        context = utils.platform(credentials, user, password)
        user = ffl.Factory.user(context)

        with user:
            models = user.get_models()

        LOGGER.debug('Got models: ' + str(models))

        return models

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def get_model(credentials, user, password, task_name):

    context = utils.platform(credentials, user, password)
    user = ffl.Factory.user(context)

    # with graph.as_default():
    with user:
        model = user.get_model(task_name)
        # model = pickle.dumps(user.get_model(task_name))

    LOGGER.debug(model)
    LOGGER.info('Retrieved model from ' + task_name)
    LOGGER.debug(type(model))

    return model


def save_model(model, task_name, extension):

    output_path = "/results/models/" + task_name + "_model." + extension

    try:
        model.save(output_path)
        if os.path.exists(output_path):
            return json.dumps({'success': True, "message": "The model resulting from " + task_name + " is saved in your local file system."}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({'success': False, "message": "The model resulting from " + task_name + " doesn't support the ." + extension + " extension. Please, try another extension."}), 500, {'ContentType': 'application/json'}

    except Exception as err:
        return json.dumps({'success': False, "message": str(err)}), 500, {'ContentType': 'application/json'}


def delete_model(credentials, user, password, task_name):

    try:

        context = utils.platform(credentials, user, password)
        user = ffl.Factory.user(context)

        with user:
            result = user.delete_model(task_name)

        LOGGER.debug(result)
        LOGGER.info("Model from " + task_name + " has been deleted")

        return result

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def model_lineage(credentials, user, password, task_name):

    try:

        context = utils.platform(credentials, user, password)
        user = ffl.Factory.user(context)

        with user:
            result = user.model_lineage(task_name)

        LOGGER.debug(result)
        LOGGER.info("Model lineage from " + task_name + " has been retrieved")

        return result

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err
