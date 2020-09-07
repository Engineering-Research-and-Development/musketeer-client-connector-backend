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


import json
import logging


# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger('catalogue')
LOGGER.setLevel(logging.DEBUG)

ALGORITHMS_PATH = 'db/mmll_config.json'
POMS_PATH = 'db/poms.json'


def get_algorithms():

    try:

        with open(ALGORITHMS_PATH) as json_file:
            return json.load(json_file)["mmll_algorithms"]

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def get_poms():

    try:
        with open(POMS_PATH) as json_file:
            return json.load(json_file)

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err
