from utils import platform_utils as utils

import logging
import communication_abstract_interface as ffl


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

            return tasks

        except Exception as err:
            LOGGER.error('error: %s', err)
            raise err

    def add_task(self, task_name, task_definition):

        """
        Create a Federated ML task.
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

        try:

            context = utils.platform(self.credentials, self.user, self.password)
            user = ffl.Factory.user(context)

            with user:
                result = user.create_task(task_name, ffl.Topology.star, task_definition)

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
