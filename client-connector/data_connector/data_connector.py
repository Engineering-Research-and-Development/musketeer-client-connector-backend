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


import pandas as pd
import json

from data_connector.abstract_data_connector import ABCDataConnector


class CsvConnector(ABCDataConnector):

    def __init__(self, spec_dataset, data_description):

        super().__init__(spec_dataset)

        self.data_description = json.loads(data_description)

        path = self.spec_dataset["path"]
        header = self.spec_dataset["header"]
        features = self.data_description["features"]
        labels = self.data_description["labels"]

        if header is False:
            data = pd.read_csv(path, header=None)
        else:
            data = pd.read_csv(path)

        self.x = data.iloc[:, 0: features].values

        if labels > 0:
            self.y = data.iloc[:, features: features+labels].values
        else:
            self.y = None

    def get_data(self):
        """
        Read Csv file from File System

        :return:
        'x' and 'y' data as numpy array
        """

        return self.x, self.y
