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


from data_connector.data_connector import CsvConnector
from utils.charts_utils import create_chart
from communication import create_aggregator_communication, wait_for_workers_to_join
from services.cc.configuration import get_mmll_class_from_classpath

import argparse
import logging
import time
import json

# Set up logger
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('aggregator')
logger.setLevel(logging.DEBUG)


def create_communication(credentials, user, password, task_name, platform):

    return create_aggregator_communication(credentials, user, password, task_name, platform)


def run_master_node(comms, masternode_class, task_definition, datasets, aggregator, task_name):

    ####################################
    # PARAMETERS FROM TASK DEFINITION #
    algorithm_name = task_definition["algorithm_name"]
    algorithm_type = task_definition["algorithm_type"].lower()

    pom = int(task_definition["POM"])

    data_description = task_definition["data_description"]
    logger.info("Data description: ")
    logger.info(data_description)

    verbose = False
    ####################################

    ####################################
    # Data connector #
    logger.info('Aggregator: loading Validation Data')
    if "validation" in datasets and datasets["validation"] is not None:
        try:
            validation_dataset = CsvConnector(spec_dataset=datasets["validation"], data_description=data_description)
        except Exception as err:
            logger.error('MasterNode error during validation data loading: ' + str(err))
            raise err
        [x_val, y_val] = validation_dataset.get_data()

    logger.info('Aggregator: loading Test Data')
    try:
        test_dataset = CsvConnector(spec_dataset=datasets["test"], data_description=data_description)
    except Exception as err:
        logger.error('MasterNode error during test data loading: ' + str(err))
        raise err
    ####################################

    ####################################
    # Creating Central Node object
    logger.info('Aggregator: creating aggregator object')
    mn = masternode_class(pom, comms, logger, verbose)

    # Set validation and test dataset
    # [x_val, y_val] = validation_dataset.get_data()
    # mn.set_validation_data("validation_dataset", x_val, y_val)
    # logger.info('MasterNode loaded %d patterns for validation' % mn.NPval)
    [x_tst, y_tst] = test_dataset.get_data()
    mn.set_test_data("test_dataset", x_tst, y_tst)
    logger.info('MasterNode loaded %d patterns for test' % mn.NPtst)

    # Creating a ML model
    logger.info('Aggregator: activating task: ' + algorithm_name)

    mn.create_model_Master(algorithm_name, model_parameters=task_definition)

    logger.info('MMLL model %s ready for training' % algorithm_name)

    t_ini = time.time()
    logger.info('Aggregator: training the model')

    if "validation" in datasets and datasets["validation"] is not None:
        mn.fit(Xval=x_val, yval=y_val)
    else:
        mn.fit()

    logger.info('Aggregator: training complete')
    t_end = time.time()
    logger.info('Aggregator: training time = %d seconds' % (t_end - t_ini))

    logger.info('Retrieving the trained model from MasterNode')
    model = mn.get_model()

    logger.info('Aggregator: Terminating all user nodes')
    mn.terminate_Workers()

    # Update server status to "completed"
    logger.info('Dispatch final model to participants')

    # Create chart
    create_chart(master_node=mn, pom=pom, algorithm_name=algorithm_name, type=algorithm_type, task_name=task_name, model=model, x=x_tst, y_tst=y_tst)

    with aggregator:
        aggregator.stop_task(model)
    logger.info('Completed training')
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
    fh = logging.FileHandler('results/logs/' + str(user) + '_aggregator_' + task_name + '.log')
    logger.addHandler(fh)
    logger.info(task_name + " initializing..")

    # Import MMLL classes
    wrapper_comms_class = get_mmll_class_from_classpath("mmll_comms_master_wrapper_classpath")
    masternode_class = get_mmll_class_from_classpath("mmll_masternode_classpath")

    # Instantiate Communication object for the aggregator user
    comms, task_definition = create_communication(credentials, user, password, task_name, platform)
    logger.info("Task definition: %s", task_definition)
    for key, value in task_definition.items():
        if type(value) is dict:
            task_definition[key] = json.dumps(value)  # to manage JSON parameter
    logger.info(task_name + ": object comms instantited")

    # Waiting for workers to join
    wait_for_workers_to_join(comms, task_definition['quorum'])

    # Instantiate wrapper Communication object
    wrapper_comms = wrapper_comms_class(comms)

    # Run 'master' aggregator
    run_master_node(wrapper_comms, masternode_class, task_definition, datasets, comms, task_name)


if __name__ == "__main__":

    try:
        main()
    except Exception as err:
        logger.error("Aggregator failed: " + str(err))
        logger.info("!x")  # To end log stream event
        raise err
