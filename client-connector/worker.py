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


from data_connector.data_connector import CsvConnector, PklConnector
from communication import create_participant_communication
from services.cc.configuration import get_mmll_class_from_classpath

import argparse
import logging
import json

# Set up logger
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('participant')
logger.setLevel(logging.DEBUG)


def create_communication(credentials, user, password, task_name, platform):
    return create_participant_communication(credentials, user, password, task_name, platform)


def run_worker_node(comms, workernode_class, task_definition, datasets):

    ####################################
    # PARAMETERS FROM TASK DEFINITION #
    algorithm_name = task_definition["algorithm_name"]

    pom = int(task_definition["POM"])

    data_description = task_definition["data_description"]
    logger.info("Data description: ")
    logger.info(data_description)

    verbose = False
    ####################################

    ####################################
    # Creating Central Node object
    logger.info('Aggregator: creating worker node object')
    wn = workernode_class(pom, comms, logger, verbose)
    ####################################

    ####################################

    # Data connector #
    # Set training, validation and test dataset
    logger.info('Participant: loading Training Data')
    try:
        if datasets["training"]["format"] == "csv":
            training_dataset = CsvConnector(spec_dataset=datasets["training"], data_description=data_description)
        elif datasets["training"]["format"] == "pkl":
            training_dataset = PklConnector(spec_dataset=datasets["training"])
    except Exception as err:
        logger.error('WorkerNode error during training data loading: ' + str(err))
        raise err
    [x_tr, y_tr] = training_dataset.get_data()

    try:
        logger.debug(x_tr[0:2])
        logger.debug(y_tr[0:2])
    except:
        pass

    if y_tr is None:
        logger.info("No 'labels' provided")
        wn.set_training_data("training_dataset", x_tr)
    else:
        wn.set_training_data("training_dataset", x_tr, y_tr)
        logger.info('WorkerNode loaded %d patterns for training' % wn.NPtr)

    logger.info('Participant: loading Validation Data')
    if "validation" in datasets and datasets["validation"] is not None:
        try:
            if datasets["validation"]["format"] == "csv":
                validation_dataset = CsvConnector(spec_dataset=datasets["validation"], data_description=data_description)
            elif datasets["validation"]["format"] == "pkl":
                validation_dataset = PklConnector(spec_dataset=datasets["validation"])
        except Exception as err:
            logger.error('WorkerNode error during validation data loading: ' + str(err))
            raise err
        [x_val, y_val] = validation_dataset.get_data()
        wn.set_validation_data("validation_dataset", x_val, y_val)
        logger.info('WorkerNode loaded %d patterns for validation' % wn.NPval)
        if y_val is None:
            logger.info("No 'labels' provided")

    logger.info('Participant: loading Test Data')
    if "test" in datasets and datasets["test"] is not None:
        try:
            if datasets["test"]["format"] == "csv":
                test_dataset = CsvConnector(spec_dataset=datasets["test"], data_description=data_description)
            elif datasets["test"]["format"] == "pkl":
                test_dataset = PklConnector(spec_dataset=datasets["test"])
        except Exception as err:
            logger.error('WorkerNode error during test data loading: ' + str(err))
            raise err
        [x_tst, y_tst] = test_dataset.get_data()
        wn.set_test_data("test_dataset", x_tst, y_tst)
        logger.info('WorkerNode loaded %d patterns for test' % wn.NPtst)
        if y_tst is None:
            logger.info("No 'labels' provided")
    ####################################

    wn.create_model_worker(algorithm_name.strip())
    logger.info('MMLL model %s ready for training' % algorithm_name)

    wn.run()
    logger.info('Worker_' + algorithm_name + ' %s: EXIT' % comms)

    logger.info('Retrieving the trained model from WorkerNode')
    # model = wn.get_model()

    logger.info('Participant: completed')
    logger.info('!x')  # To end log stream event


def main():

    # Arguments parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--credentials', type=str, default=None, help='Credentials for Muskeeter Server')
    parser.add_argument('--user', type=str, default=None, help='User')
    parser.add_argument('--password', type=str, default=None, help='Password')
    parser.add_argument('--task_name', type=str, default=None, help='Name of the task')
    parser.add_argument('--datasets', type=str, default=None, help='Datasets objects to read')
    parser.add_argument('--platform', type=str, default=None, help='Platform used: local or cloud')

    params, unparsed = parser.parse_known_args()
    credentials = params.credentials
    user = params.user
    password = params.password
    task_name = params.task_name
    datasets = json.loads(params.datasets)
    platform = params.platform

    # Logging / Setting FH
    fh = logging.FileHandler('results/logs/' + str(user) + '_participant_' + task_name + '.log')
    logger.addHandler(fh)
    logger.info(task_name + " initializing..")

    # Import MMLL classes
    wrapper_comms_class = get_mmll_class_from_classpath("mmll_comms_worker_wrapper_classpath")
    workernode_class = get_mmll_class_from_classpath("mmll_workernode_classpath")

    # Instantiate Communication object for the participant user
    comms, task_definition = create_communication(credentials, user, password, task_name, platform)
    for key, value in task_definition.items():
        if type(value) is dict:
            task_definition[key] = json.dumps(value)  # to manage JSON parameter
    logging.info(task_name + ": object comms instantited")

    # Instantiate wrapper Communication object
    wrapper_comms = wrapper_comms_class(comms)

    # Run 'worker' participant
    run_worker_node(wrapper_comms, workernode_class, task_definition, datasets)


if __name__ == "__main__":

    try:
        main()
    except Exception as err:
        logger.error("Participant failed: " + str(err))
        logger.info("!x")  # To end log stream event
        raise err
