from datetime import datetime
import os
import json
import logging

LOGGER = logging.getLogger('dataset')
LOGGER.setLevel(logging.DEBUG)

DATASET_CLASS_PATH = "services.cc.dataset."
SERVER_DB_PATH = "db/server_db.json"


def get_datasets():

    try:

        with open('db/server_db.json') as json_file:
            return json.load(json_file)["datasets"]

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def add_dataset(type, spec):

    with open(SERVER_DB_PATH, "r") as jsonFile:
        data = json.load(jsonFile)

    with open(SERVER_DB_PATH, "r") as jsonFileBackup:
        backup_data = json.load(jsonFileBackup)

    new_dataset = get_dataset_class(type, spec)
    data["datasets"][type].append(new_dataset.__dict__)

    try:
        with open(SERVER_DB_PATH, "w") as jsonFile:
            json.dump(data, jsonFile)
    except:
        print("Error: backup json")
        with open(SERVER_DB_PATH, "w") as jsonFileBackup:
            json.dump(backup_data, jsonFileBackup)
        raise


def get_dataset_class(type, spec):

    dataset_class = get_class(DATASET_CLASS_PATH+str(type))
    return dataset_class(spec)


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

        self.name = spec["name"]
        self.added = str(datetime.utcnow())


class FileSystem(Dataset):

    def __init__(self, spec):

        super().__init__(spec)
        self.path = spec["path"]
        self.dimension = os.path.getsize(spec["path"])
        self.format = spec["format"]
        self.header = spec["header"]
        self.module = self.format.capitalize()+"Connector"
