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
import json

# Set up logger
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger('communication')
LOGGER.setLevel(logging.DEBUG)


def create_participant_communication(credentials, user, password, task_name, platform='cloud'):

    context = utils.platform(credentials, user, password, platform)
    user = ffl.Factory.user(context)

    with user:
        task_definition = json.loads(user.task_info(task_name)['definition'])

    return ffl.Factory.participant(context, task_name=task_name), task_definition


def create_aggregator_communication(credentials, user, password, task_name, platform='cloud'):

    context = utils.platform(credentials, user, password, platform)
    user = ffl.Factory.user(context)

    with user:
        task_definition = json.loads(user.task_info(task_name)['definition'])

    return ffl.Factory.aggregator(context, task_name=task_name), task_definition


def wait_for_workers_to_join(aggregator, quorum):
    """
    Wait for workers to join until quorum is met.
    """
    with aggregator:
        workers = aggregator.get_participants()

    if workers:
        if len(workers) == quorum:
            LOGGER.info('Participants have already joined')
            return workers

    LOGGER.info('Waiting for workers to join (%d of %d present)' % (len(workers), quorum))

    ready = False
    while not ready:
        try:
            with aggregator:
                resp = aggregator.receive(300)
                participant = resp.notification['participant']
            LOGGER.info('Participant %s joined' % participant)
        except Exception as err:
            raise err

        if len(workers) == quorum:
            ready = True

    return workers
