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

import logging
import requests

import communication_abstract_interface as fflabc


logging.getLogger("httpcloudmessenger").setLevel(logging.CRITICAL)
LOGGER = logging.getLogger(__package__)


class Context(fflabc.AbstractContext):
    """
    Class holding connection details for an FFL service
    """
    def __init__(self, args: dict, user: str = None, password: str = None):
        super()
        self.config = args
        self.user = user
        self.password = password

    def __enter__(self):
        self

    def __exit__(self, ex_type, ex_val, tb):
        if ex_type is None:
            return True


class Messenger:
    """
    Class for communicating with an FFL service
    """

    def __init__(self, context: Context):
        """
        Class initializer
        :param context: connection details
        :type context: :class:`.Context`
        """
        self.context = context

    def __enter__(self):
        """
        Context manager enters.
        Throws: An exception on failure
        :return: self
        :rtype: :class:`.Messenger`
        """
        return self

    def _invoke_service(self, message: dict) -> dict:
        """
        Send a message and wait for a reply or until timeout.
        Throws: An exception on failure
        :param message: message to be sent
        :type message: `dict`
        :return: received message
        :rtype: `dict`
        """

        payload = {}

        config = self.context.config
        user_name = self.context.user
        password = self.context.password

        data_app_url = config.get('data_app_url', None)
        server_url = config.get('server_url', None)
        endpoint = message['endpoint']

        if not data_app_url:
            raise Exception("'data_app_url' must be specified")
        if not server_url:
            raise Exception("'server_url' must be specified")
        if not endpoint:
            raise Exception("'endpoint' must be specified")

        session = requests.Session()
        session.headers.update({'content-type': 'application/json'})
        message['username'] = user_name
        message['password'] = password

        payload["payload": message]
        payload['Forward-To'] = server_url+endpoint

        response = session.post(data_app_url, json=payload, verify=False)
        response.raise_for_status()
        session.close()

        return response.json()

    def user_change_password(self, user_name: str, password: str) -> None:
        """
        Change the user password
        Throws: An exception on failure
        :param user_name: user name (must be a non-empty string and unique;
                                     if a user with this name has not registered
                                     before, an exception is thrown).
        :type user_name: `str`
        :param password: password (must be a non-empty string)
        :type password: `str`
        """
        message = {"endpoint": "user_change_password", "user_name": user_name, "password": password}
        return self._invoke_service(message=message)

    def task_listing(self) -> dict:
        """
        Returns a list with all the available tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """
        message = {"endpoint": "task_listing"}
        return self._invoke_service(message=message)

    def task_create(self, task_name: str, topology: str, definition: dict) -> dict:
        """
        Creates a task with the given definition and returns a dictionary
        with the details of the created tasks.
        Throws: An exception on failure
        :param task_name: name of the task to create
        :type task_name: `str`
        :param topology: topology of the task participants' communication network
        :type topology: `str`
        :param definition: definition of the task to be created
        :type definition: `dict`
        :return: details of the created task
        :rtype: `dict`
        """
        message = {"endpoint": "create_task", "task_name": task_name, "topology": topology, "definition": definition}
        return self._invoke_service(message=message)

    def task_assignment_join(self, task_name: str) -> dict:
        """
        As a potential task participant, try to join the task.
        This will fail if the task status isn't 'CREATED'.
        Throws: An exception on failure
        :param task_name: name of the task to be joined
        :type task_name: `str`
        :return: details of the task assignment
        :rtype: `dict`
        """
        message = {"endpoint": "task_assignment_join", "task_name": task_name}
        return self._invoke_service(message=message)

    def task_info(self, task_name: str) -> dict:
        """
        Returns the details of a given task.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :return: details of the task
        :rtype: `dict`
        """
        message = {"endpoint": "task_info", "task_name": task_name}
        return self._invoke_service(message=message)

    def task_update(self, task_name: str, status: str, topology: str = None,
                    definition: dict = None) -> dict:
        """
        Updates a task with the given details.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :param status: task status (must be either 'CREATED', 'STARTED', 'FAILED', 'COMPLETE')
        :type status: `str`
        :param topology: topology of the task participants' communication network
        :type topology: `str`
        :param definition: task definition
        :type definition: `dict`
        :return: details of the updated task
        :rtype: `dict`
        """
        message = {"endpoint": "task_update", "task_name": task_name, "status": status, "topology": topology,
                   "definition": definition}
        return self._invoke_service(message=message)

    def task_quit(self, task_name: str) -> None:
        """
        As a task participant, leave the given task.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        """
        message = {"endpoint": "task_quit", "task_name": task_name}
        return self._invoke_service(message=message)

    def task_start(self, task_name: str, model: dict = None, participant: str = None,
                   topology: str = None) -> None:
        """
        As a task creator, start the given task and optionally send message
        including the given model to all task
        participants. The status of the task will be changed to 'STARTED'.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        :param model: model to be sent as part of the message
        :type model: `dict`
        """
        message = {"endpoint": "task_start", "task_name": task_name, "model": model, "participant": participant,
                   "topology": topology}
        return self._invoke_service(message=message)

    def task_stop(self, task_name: str, model: dict = None) -> None:
        """
        As a task creator, stop the given task.
        The status of the task will be changed to 'COMPLETE'.
        Throws: An exception on failure
        :param task_name: name of the task
        :type task_name: `str`
        """
        message = {"endpoint": "task_stop", "task_name": task_name, "model": model}
        return self._invoke_service(message=message)

    def user_assignments(self) -> list:
        """
        Returns all the tasks the user is participating in.
        :return: list of all the tasks, each of which is a dictionary
        :rtype: `list`
        """
        message = {"endpoint": "user_assignments"}
        return self._invoke_service(message)

    def model_delete(self, task_name: str):
        """
        Requests a model deletion
        Throws: An exception on failure
        Returns: None
        """
        message = {"endpoint": "model_delete", "task_name": task_name}
        return self._invoke_service(message)

    def model_lineage(self, task_name: str) -> list:
        """
        Requests the model lineage for task 'task_name'
        Throws: An exception on failure
        Returns: list
        """
        message = {"endpoint": "model_lineage", "task_name": task_name}
        return self._invoke_service(message)

    def model_info(self, task_name: str) -> dict:
        """
        Returns model info.
        Throws: An exception on failure
        :return: dict of model info
        :rtype: `dict`
        """
        message = {"endpoint": "model_info", "task_name": task_name}
        return self._invoke_service(message)

    def model_listing(self) -> dict:
        """
        Returns a list with all the available trained models.
        Throws: An exception on failure
        :return: list of all the available models
        :rtype: `list`
        """
        message = {"endpoint": "model_listing"}
        return self._invoke_service(message)

    def send(self, message: dict, task_name, role, participant=None, topology=None) -> None:
        """
        Send a message and return immediately.
        Throws: An exception on failure
        :param role: aggregator/participant
        :param task_name: the name of the task
        :param message: message to be sent
        :param topology:
        :param participant:
        :type message: `dict`
        """
        message = {"endpoint": "send_message", "message": message, "task_name": task_name, "role": role,
                   "participant": participant, "topology": topology}
        return self._invoke_service(message)

    def receive(self, task_name, role) -> dict:
        """
        Wait for a message to arrive or until timeout.
        Throws: An exception on failure
        :param role: aggregator/participant
        :param task_name: the name of the task
        :return: received message
        :rtype: `dict`
        """
        message = {"endpoint": "receive_message", "task_name": task_name, "role": role}
        return self._invoke_service(message)

##########################################################################

##########################################################################
# Base class for participants/aggregators ################################


class BasicParticipant:
    """ Base class for an FFL general user """

    def __init__(self, context: Context):
        """
        Class initializer.
        Throws: An exception on failure
        :param context: connection details
        :type context: :class:`.Context`
        """
        if not context:
            raise Exception('Credentials must be specified.')

        self.messenger = None
        self.context = context

##########################################################################

##########################################################################
# Base class for participants/aggregators ################################


class BasicParticipant:
    """ Base class for an FFL general user """

    def __init__(self, context: Context):
        """
        Class initializer.
        Throws: An exception on failure
        :param context: connection details
        :type context: :class:`.Context`
        """
        if not context:
            raise Exception('Credentials must be specified.')

        self.context = context
        self.messenger = Messenger(self.context)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_val, tb):
        if ex_type is None:
            return True

    def connect(self):
        """
        Connect to the cloud system.
        Throws: An exception on failure
        :return: self
        :rtype: :class:`.BasicParticipant`
        """
        message = {"endpoint": "connect"}
        return self.messenger._invoke_service(message=message)

    def close(self) -> None:
        """
        Close the connection to the cloud system.
        Throws: An exception on failure
        """
        message = {"endpoint": "close"}
        return self.messenger._invoke_service(message=message)

##########################################################################

##########################################################################
# Class for general services, task management etc. #######################


class User(fflabc.AbstractUser, BasicParticipant):
    """ Class that allows a general user to avail of the FFL platform services """

    def change_password(self, user_name: str, password: str) -> None:
        """
        Change user password
        Throws: An exception on failure
        :param user_name: user name (must be a non-empty string and unique;
                                     if a user with this name has not registered
                                     before, an exception is thrown).
        :type user_name: `str`
        :param password: password (must be a non-empty string)
        :type password: `str`
        """
        return self.messenger.user_change_password(user_name, password)

    def get_tasks(self) -> list:
        """
        Returns a list with all the available tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """
        return self.messenger.task_listing()

    def create_task(self, task_name: str, topology: str, definition: dict) -> dict:
        """
        Creates a task with the given definition and returns a dictionary
        with the details of the created tasks.
        Throws: An exception on failure
        :param task_name: name of the task to create
        :type task_name: `str`
        :param topology: topology of the task participants' communication network
        :type topology: `str`
        :param definition: definition of the task to be created
        :type definition: `dict`
        :return: details of the created task
        :rtype: `dict`
        """
        return self.messenger.task_create(task_name, topology, definition)

    def join_task(self, task_name: str) -> dict:
        """
        As a potential task participant, try to join an existing task that has yet to start.
        Throws: An exception on failure
        :param task_name: name of the task to join
        :type task_name: `str`
        :return: details of the task assignment
        :rtype: `dict`
        """
        return self.messenger.task_assignment_join(task_name)

    def task_info(self, task_name: str) -> dict:
        """
        Returns the details of a given task.
        Throws: An exception on failure
        :param task_name: name of the task to join
        :type task_name: `str`
        :return: details of the task
        :rtype: `dict`
        """
        return self.messenger.task_info(task_name)

    def get_joined_tasks(self) -> list:
        """
        Returns a list with all the joined tasks.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """
        return self.messenger.user_assignments()

    def get_created_tasks(self) -> list:
        """
        Returns a list with all the tasks created by the current user.
        Throws: An exception on failure
        :return: list of all the available tasks
        :rtype: `list`
        """
        return self.messenger.user_tasks()

    def get_models(self) -> list:
        """
        Returns a list with all the available trained models.
        Throws: An exception on failure
        :return: list of all the available models
        :rtype: `list`
        """
        return self.messenger.model_listing()

    def get_model(self, task_name: str) -> list:
        """
        Returns a list with all the available trained models.
        Throws: An exception on failure
        :return: list of all the available models
        :rtype: `list`
        """
        return self.messenger.model_info(task_name)

    def model_lineage(self, task_name: str) -> list:
        """
        Returns a list with model lineage
        Throws: An exception on failure
        :return: list of all the available models
        :rtype: `list`
        """
        return self.messenger.model_lineage(task_name)

    def delete_model(self, task_name: str):
        """
        Deletes a model for given task
        Throws: An exception on failure
        :return: nothing
        """
        return self.messenger.model_delete(task_name)
##########################################################################


##########################################################################
# Class for participating in federated learning (training) ###############

class Participant(fflabc.AbstractParticipant, BasicParticipant):
    """ This class provides the functionality needed by the
        participants of a federated learning task.  """

    def __init__(self, context: Context, task_name: str = None):
        """
        Class initializer.
        Throws: An exception on failure
        :param context: connection details
        :type context: :class:`.Context`
        :param task_name: name of the task (the user needs to be a participant of this task).
        :type task_name: `str`
        """
        super().__init__(context)

        self.task_name = task_name
        self.messenger = Messenger(self.context)

    def send(self, message: dict = None):
        """
        Send a message to the aggregator and return immediately (not waiting for a reply).
        Throws: An exception on failure
        :param message: message to be sent (needs to be serializable)
        :type message: `dict`
        """
        return self.messenger.send(message, self.task_name, "participant")

    def receive(self):
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure
        :return: received message
        :rtype: `class Response`
        """
        return self.messenger.receive()

    def leave_task(self):
        """
        As a task participant, leave the given task.
        Throws: An exception on failure
        """
        return self.messenger.task_quit(self.task_name)

##########################################################################


##########################################################################
# Class for aggregating federated learning contributions #################

class Aggregator(fflabc.AbstractAggregator, BasicParticipant):
    """ This class provides the functionality needed by the
        aggregator of a federated learning task. """

    def __init__(self, context: Context, task_name: str = None):
        """
        Class initializer.
        Throws: An exception on failure
        :param context: Connection details
        :type context: :class:`.Context`
        :param task_name: Name of the task (note: the user must be the creator of this task)
        :type task_name: `str`
        """
        super().__init__(context)

        self.task_name = task_name
        self.messenger = Messenger(self.context)

    def send(self, message: dict = None, participant: str = None, topology: str = None):
        """
        Send a message to all task participants and return immediately (not waiting for a reply).
        Throws: An exception on failure
        :param message: message to be sent
        :type message: `dict`
        """
        self.messenger.send(message, self.task_name, "aggregator", participant, topology)

    def receive(self):
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure
        :return: received message
        :rtype: `class Response`
        """
        return self.messenger.receive(self.task_name, "aggregator")
