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
from utils.compressor import compress_data_descriptions, decompress_data_descriptions

import logging
import communication_abstract_interface as ffl
import json
import os.path


# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger('tasks')
LOGGER.setLevel(logging.DEBUG)


class Tasks:

    def __init__(self, credentials, user, password):

        self.credentials = credentials
        self.user = user
        self.password = password

    def get_tasks(self):

        """
        Get a list of all the tasks.
        :param credentials: json file containing credentials.
        :type credentials: `str`
        :return: list of all the tasks, each of which is a dictionary.
        :rtype: `list`
        """

        try:
            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                tasks = user.get_tasks()

            filtered_tasks = []
            for task in tasks:
                if "owner" in task["definition"]:
                    filtered_tasks.append(task)

            return filtered_tasks

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

    def get_task_info(self, task_name):

        try:
            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                task = user.task_info(task_name)

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

        task["definition"] = json.loads(task["definition"])
        task["definition"] = decompress_data_descriptions(task["definition"])
        result_path = "results/" + task_name + '_' + self.user.lower() + ".png"
        old_result_path = "results/" + task_name + ".png"

        # Calculate and set the "actions"
        # It's the task "creator"
        status = task["status"]
        if "task_name" in task:

            participate_flag = -1
            delete_flag = 1

            if status == "COMPLETE":

                if os.path.exists(result_path) \
                        or os.path.exists(old_result_path):
                    result_flag = 1
                else:
                    result_flag = -1
                aggregate_flag = -1
                logs_flag = 1

            elif status == "CREATED":
                aggregate_flag = 1
                result_flag = 0
                logs_flag = 0

            elif status == "FAILED":
                aggregate_flag = -1
                result_flag = -1
                logs_flag = 1

            else:
                aggregate_flag = -1
                result_flag = 0
                logs_flag = 1

            if status == "CREATED" and os.path.exists("/results/logs/" + self.user + "_aggregator_" + task_name + ".log"):
                aggregate_flag = -1
                logs_flag = 1

        # It's a possible participant
        else:
            task["task_name"] = task_name

            if os.path.exists("/results/logs/" + self.user + "_participant_" + task_name + ".log"):
                logs_flag = 1
            else:
                logs_flag = -1

            aggregate_flag = -1
            delete_flag = -1
            result_flag = -1

            if status == "COMPLETE":
                if os.path.exists(result_path) \
                        or os.path.exists(old_result_path):
                    result_flag = 1

            if status == "CREATED" or status == "PENDING":

                participate_flag = 1
            else:

                participate_flag = -1

        # Add "actions" object
        task["actions"] = {
            "aggregate": aggregate_flag,
            "participate": participate_flag,
            "result": result_flag,
            "logs": logs_flag,
            "delete": delete_flag
        }

        return task

    def get_created_tasks(self):

        """
        Returns a list with all the tasks created by the current user.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """

        try:
            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                created_tasks = user.get_created_tasks()

            sorted_created_tasks = sorted(created_tasks, key=lambda k: k['added'], reverse=True)

            return sorted_created_tasks

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

    def get_joined_tasks(self):

        """
        Returns a list with all the joined tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """

        try:
            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                joined_tasks = user.get_joined_tasks()

            return joined_tasks

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

    def add_task(self, task_name, task_definition, topology):

        """
        Create a Federated ML task.
        :param topology: RING or STAR
        :param credentials: json file containing credentials.
        :type credentials: `str`
        :param user: user name for authentication as task creator.
        :type user: `str`
        :param password: password for authentication as task creator.
        :type password: `str`
        :param task_name: name of the task (must be unique).
        :type task_name: `str`
        :param task_definition: definition of the task.
        :type task_definition: `dict`
        """

        task_definition = compress_data_descriptions(task_definition)

        try:

            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                result = user.create_task(task_name, topology, task_definition)

            LOGGER.debug(result)
            LOGGER.info('Task ' + task_name + ' created.')

            return result

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

    def get_user_assignments(self):
        """
        Retrieve a list of all the tasks the user is participating in.
        :param credentials: json file containing credentials.
        :type credentials: `str`
        :param user: user name for authentication as task creator.
        :type user: `str`
        :param password: password for authentication as task creator.
        :type password: `str`
        :return: list of all the tasks the user is participating in.
        :rtype: `list`
        """

        try:

            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                return user.get_joined_tasks()

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

    def join_task(self, task_name):

        """
        Join a Federated ML task.
        :param credentials: json file containing credentials.
        :type credentials: `str`
        :param user: user name for authentication as task creator.
        :type user: `str`
        :param password: password for authentication as task creator.
        :type password: `str`
        :param task_name: name of the task (must be unique).
        :type task_name: `str`
        """

        try:
            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)
            with user:
                return user.join_task(task_name)
                LOGGER.debug('joined task')

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

    def delete_task(self, task_name):

        try:
            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                return user.delete_task(task_name)

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err
