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
