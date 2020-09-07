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
-------------------------

A logger class.
"""

import logging


class Logger:
    """
    This class implements the logging facilities as well as some print methods.
    """

    def __init__(self, output_filename):
        """
        Create a :class:`Logger` instance.

        Parameters
        ----------
        output_filename : string
            path + filename to the file containing the output logs

        """
        self.logger = logging.getLogger()            # logger
        fhandler = logging.FileHandler(filename=output_filename, mode='w')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fhandler.setFormatter(formatter)
        self.logger.addHandler(fhandler)
        self.logger.setLevel(logging.INFO)

    def display(self, message, verbose=True):
        """
        Display on screen if verbose=True and prints to the log file

        Parameters
        ----------
        verbose : Boolean
            prints to screen if True
        """
        if verbose:
            print(message)
        self.logger.info(message)

    def info(self, message):
        self.logger.info(message)
