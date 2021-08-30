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

import pickle
import base64
import jsonpickle
import dill


class SerializerABC(ABC):
    """Basic serialization"""

    @abstractmethod
    def serialize(self, message: any) -> str:
        """Convert message to serializable format"""

    @abstractmethod
    def deserialize(self, message: bytes) -> any:
        """Convert serialized message to dict"""


class Base64Serializer(SerializerABC):
    """Base64 encoder"""

    def serialize(self, message: any) -> str:
        """Convert message to serializable format"""
        try:
            return base64.b64encode(
                pickle.dumps(message)
            ).decode('utf-8')
        except:
            return base64.b64encode(dill.dumps(message))

    def deserialize(self, message: bytes) -> any:
        """Convert serialized message to dict"""
        try:
            return pickle.loads(base64.b64decode(message))
        except:
            return dill.loads(base64.b64decode(message))


class JsonPickleSerializer(SerializerABC):
    """Json pickle serialization"""

    def serialize(self, message: any) -> str:
        """Convert message to serializable format"""
        return jsonpickle.encode(message)

    def deserialize(self, message: bytes) -> any:
        """Convert serialized message to dict"""
        return jsonpickle.decode(message)


