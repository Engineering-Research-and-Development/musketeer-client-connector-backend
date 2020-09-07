from abc import ABC, abstractmethod
from subprocess import Popen, PIPE

import sys


class Client:

    def __init__(self, credentials, user, password, task_name, datasets=None, platform="cloud"):

        self.credentials = credentials
        self.user = user
        self.password = password
        self.task_name = task_name
        self.datasets = datasets
        self.platform = platform

    @abstractmethod
    def run(self):
        pass


class AggregatorSubProcess(Client):

    def __init__(self, credentials, user, password, task_name):
        Client.__init__(self, credentials, user, password, task_name)

    def run(self):
        print("SubProcess Aggregator started")
        Popen([sys.executable, 'aggregator.py', "--credentials", self.credentials, "--user", self.user,
               "--password", self.password, "--task_name", self.task_name], stdout=PIPE)


class ParticipantSubProcess(Client):

    def __init__(self, credentials, user, password, task_name):
        Client.__init__(self, credentials, user, password, task_name)

    def run(self):
        print("SubProcess Participant started")
        Popen([sys.executable, 'participant.py', "--credentials", self.credentials, "--user", self.user,
               "--password", self.password, "--task_name", self.task_name], stdout=PIPE)


class AggregatorSubProcessV2(Client):

    def __init__(self, credentials, user, password, task_name, datasets, platform="cloud"):
        Client.__init__(self, credentials, user, password, task_name, datasets, platform)

    def run(self):
        print("SubProcess Aggregator started")
        Popen([sys.executable, 'master.py', "--credentials", self.credentials, "--user", self.user,
               "--password", self.password, "--task_name", self.task_name, "--datasets", self.datasets,
               "--platform", self.platform], stdout=PIPE)


class ParticipantSubProcessV2(Client):

    def __init__(self, credentials, user, password, task_name, datasets, platform="cloud"):
        Client.__init__(self, credentials, user, password, task_name, datasets, platform)

    def run(self):
        print("SubProcess Participant started")
        Popen([sys.executable, 'worker.py', "--credentials", self.credentials, "--user", self.user,
               "--password", self.password, "--task_name", self.task_name, "--datasets", self.datasets,
               "--platform", self.platform], stdout=PIPE)
