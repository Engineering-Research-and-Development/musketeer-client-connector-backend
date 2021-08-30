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


from datetime import datetime
from services.cc.models import Dataset as DatasetModel
from bson.objectid import ObjectId

import os
import logging
import configparser

LOGGER = logging.getLogger('dataset')
LOGGER.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read('app.ini')

DATASET_CLASS_PATH = config["DATASET"]["DATASET_CLASS_PATH"]
SERVER_DB_PATH = config["SERVER"]["SERVER_DB_PATH"]


def get_datasets():

    try:

        datasets = DatasetModel.objects()
        datasets_list = []
        for dataset in datasets:
            dataset_dict = dataset.to_mongo().to_dict()
            dataset_dict['added'] = dataset.added.isoformat()
            datasets_list.append(dataset_dict)
        return datasets_list

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def add_dataset(type, spec):

    dataset = get_dataset_class(type, spec)
    DatasetModel(**dataset.dataset_dict).save()


def get_dataset_class(type, spec):

    dataset_class = get_class(DATASET_CLASS_PATH+str(type))
    return dataset_class(spec)


def delete_dataset_by_id(_id):

    DatasetModel.objects(_id=ObjectId(_id)).delete()


def update_dataset(_id, json):

    if json["format"] == "csv":
        DatasetModel.objects(_id=ObjectId(_id))[0].update(name=json["name"], path=json["path"], header=json["header"])
    elif json["format"] == "pkl":
        DatasetModel.objects(_id=ObjectId(_id))[0].update(name=json["name"], path=json["path"], label=json["label"])


def get_class(class_name):
    """
    Get a class module from its name.
    :param class_name: Full name of a class.
    :type class_name: `str`
    :return: The class `module`.
    :rtype: `module`
    """
    sub_mods = class_name.split(".")
    module_ = __import__(".".join(sub_mods[:-1]), fromlist=sub_mods[-1])
    class_module = getattr(module_, sub_mods[-1])

    return class_module


class Dataset:

    def __init__(self, spec):

        # self._id = str(uuid.uuid4())
        self.dataset_dict = {"name": spec["name"], "added": str(datetime.utcnow())}


class FileSystem(Dataset):

    def __init__(self, spec):

        super().__init__(spec)
        self.dataset_dict["path"] = "/input_data/" + spec["path"]
        self.dataset_dict["dimension"] = os.path.getsize("/input_data/" + spec["path"])
        self.dataset_dict["format"] = spec["format"]
        self.dataset_dict["module"] = spec["format"].capitalize()+"Connector"

        if spec["format"] == "csv":
            self.dataset_dict["header"] = spec["header"] if "header" in spec else None
        elif spec["format"] == "pkl":
            self.dataset_dict["label"] = spec["label"] if "label" in spec else False
