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

from io import BytesIO

import gzip
import logging
import base64

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger('compressor')
LOGGER.setLevel(logging.DEBUG)


def decompress_bytes_to_string(input_bytes):
    """
    decompress the given byte array (which must be valid
    compressed gzip data) and return the decoded text (utf-8).
    """
    bio = BytesIO()
    stream = BytesIO(input_bytes)
    decompressor = gzip.GzipFile(fileobj=stream, mode='r')
    while True:  # until EOF
        chunk = decompressor.read(8192)
        if not chunk:
            decompressor.close()
            bio.seek(0)
            return bio.read().decode("utf-8")
        bio.write(chunk)
    return None


def compress_string_to_bytes(input_string):
    """
    read the given string, encode it in utf-8,
    compress the data and return it as a byte array.
    """
    bio = BytesIO()
    bio.write(input_string.encode("utf-8"))
    bio.seek(0)
    stream = BytesIO()
    compressor = gzip.GzipFile(fileobj=stream, mode='w')
    while True:  # until EOF
        chunk = bio.read(8192)
        if not chunk:  # EOF?
            compressor.close()
            return stream.getvalue()
        compressor.write(chunk)


def compress_data_descriptions(task):

    try:

        if "input_data_description" in task:
            task["input_data_description"] = compress_string_to_bytes(str(task["input_data_description"]))

        if "target_data_description" in task:
            task["target_data_description"] = compress_string_to_bytes(str(task["target_data_description"]))

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err

    return task


def decompress_data_descriptions(task_definition):

    try:

        if "input_data_description" in task_definition:

            # Input data description
            base64_idd = task_definition["input_data_description"]["py/b64"]
            base64_bytes_idd = base64_idd.encode('ascii')
            message_bytes_idd = base64.b64decode(base64_bytes_idd)

            task_definition["input_data_description"] = decompress_bytes_to_string(message_bytes_idd)

        if "target_data_description" in task_definition:

            # Target data description
            base64_tdd = task_definition["target_data_description"]["py/b64"]
            base64_bytes_tdd = base64_tdd.encode('ascii')
            message_bytes_tdd = base64.b64decode(base64_bytes_tdd)

            task_definition["target_data_description"] = decompress_bytes_to_string(message_bytes_tdd)

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err

    return task_definition
