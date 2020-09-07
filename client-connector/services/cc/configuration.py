import json
import logging
import importlib
import subprocess
import sys

LOGGER = logging.getLogger('configuration')
LOGGER.setLevel(logging.DEBUG)

COMM_DB_PATH = "db/comm_config.json"
COMMS_CONFIG_PATH = "config.json"

MMLL_DB_PATH = "db/mmll_config.json"

'''
Methods to configure and manage external necessary components to integrate into the CC:

    - comms_git_url: Git URL where to download the comms package 
    - comms_module: module name to import
    - comms_config: JSON configuration for the comms instance used
    
    - mmll_git_url: Git URL where to download the mmll package 
    - mmll_masternode_classpath
    - mmll_workernode_classpath
    - mmll_comms_wrapper_classpath
    
    - algorithms JSON file
'''


def set_comm_json_configurations(config_data):

    if "comms_git_user" not in config_data:
        config_data["comms_git_user"] = None
    if "comms_git_password" not in config_data:
        config_data["comms_git_password"] = None

    check_comm_type_configurations(config_data)
    install_package_from_git(config_data["comms_git_url"], config_data["comms_git_user"], config_data["comms_git_password"])
    check_import_module(config_data["comms_module"])

    try:
        with open(COMM_DB_PATH, "w") as jsonFile:
            json.dump(config_data, jsonFile)

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err

    comms_config = config_data["comms_config"]

    try:
        with open(COMMS_CONFIG_PATH, "w") as jsonFile:
            json.dump(comms_config, jsonFile)
    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def set_mmll_json_configurations(config_data):

    if "mmll_git_user" not in config_data:
        config_data["comms_git_user"] = None
    if "mmll_git_password" not in config_data:
        config_data["comms_git_password"] = None

    check_mmll_type_configurations(config_data)
    install_package_from_git(config_data["mmll_git_url"], config_data["mmll_git_user"], config_data["mmll_git_password"])
    check_class_from_classpath(config_data["mmll_masternode_classpath"])
    check_class_from_classpath(config_data["mmll_workernode_classpath"])
    check_class_from_classpath(config_data["mmll_comms_master_wrapper_classpath"])
    check_class_from_classpath(config_data["mmll_comms_worker_wrapper_classpath"])

    validate_catalogue_json(config_data["mmll_algorithms"])

    try:
        with open(MMLL_DB_PATH, "w") as jsonFile:
            json.dump(config_data, jsonFile)

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def validate_catalogue_json(algorithms):

    # Check type
    if type(algorithms) is not list:
        raise TypeError("Insert algorithms as list of json")

    if type(algorithms[0]) is not dict:
        raise TypeError("Each algorithm has to be described using json format")

    return


def check_comm_type_configurations(config_data):

    # Check type
    if type(config_data["comms_git_url"]) is not str:
        raise TypeError("Insert 'comms_git_url' as string type")

    if config_data["comms_git_user"] is not None and config_data["comms_git_password"] is not None:

        if type(config_data["comms_git_user"]) is not str:
            raise TypeError("Insert 'comms_git_user' as string type")

        if type(config_data["mmll_git_password"]) is not str:
            raise TypeError("Insert 'comms_git_password' as string type")

    if type(config_data["comms_module"]) is not str:
        raise TypeError("Insert 'comms_module' as string type")

    if type(config_data["comms_config"]) is not dict:
        raise TypeError("Insert 'comms_config' as json type")


def check_mmll_type_configurations(config_data):

    # Check type
    if type(config_data["mmll_git_url"]) is not str:
        raise TypeError("Insert 'mmll_git_url' as string type")

    if config_data["mmll_git_user"] is not None and config_data["mmll_git_password"] is not None:

        if type(config_data["mmll_git_user"]) is not str:
            raise TypeError("Insert 'mmll_git_user' as string type")

        if type(config_data["mmll_git_password"]) is not str:
            raise TypeError("Insert 'mmll_git_password' as string type")

    if type(config_data["mmll_masternode_classpath"]) is not str:
        raise TypeError("Insert 'mmll_masternode_classpath' as string type")

    if type(config_data["mmll_workernode_classpath"]) is not str:
        raise TypeError("Insert 'mmll_workernode_classpath' as str type")

    if type(config_data["mmll_comms_master_wrapper_classpath"]) is not str:
        raise TypeError("Insert 'mmll_comms_master_wrapper_classpath' as str type")

    if type(config_data["mmll_comms_worker_wrapper_classpath"]) is not str:
        raise TypeError("Insert 'mmll_comms_worker_wrapper_classpath' as str type")

    if type(config_data["mmll_algorithms"]) is not list:
        raise TypeError("Insert 'mmll_algorithms' as dict type")


def get_comm_json_configurations():

    try:
        with open(COMM_DB_PATH, "r") as jsonFile:
            config_data = json.load(jsonFile)
        return config_data

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def get_mmll_json_configurations():

    try:
        with open(MMLL_DB_PATH, "r") as jsonFile:
            config_data = json.load(jsonFile)
        return config_data

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def install_package_from_git(package, user, password):

    if user is not None and password is not None:

        if package.find("git+https://") == 0:
            package = package[0:12] + user + ":" + password + "@" + package[12:]
        elif package.find("git+http://") == 0:
            package = package[0:11] + user + ":" + password + "@" + package[11:]
        else:
            raise TypeError("Package has to start with: git+https://")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        LOGGER.info(str(package) + " package installed")

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def check_import_module(module):

    try:
        importlib.import_module(module)
        LOGGER.info(str(module) + " module checked")

    except ImportError as err:
        LOGGER.error('error: %s', err)
        raise err


def check_class_from_classpath(classpath):

    try:
        mod = __import__(classpath[::-1].split(".", 1)[1][::-1], fromlist=[classpath[::-1].split(".", 1)[0][::-1]])
        getattr(mod, classpath[::-1].split(".", 1)[0][::-1])

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


def get_mmll_class_from_classpath(key):

    with open(MMLL_DB_PATH) as json_file:
        classpath = json.load(json_file)[key]

    mod = __import__(classpath[::-1].split(".", 1)[1][::-1], fromlist=[classpath[::-1].split(".", 1)[0][::-1]])
    return getattr(mod, classpath[::-1].split(".", 1)[0][::-1])


def get_step_configurations():

    comm_json = get_comm_json_configurations()
    mmll_json = get_mmll_json_configurations()

    if comm_json == {} or comm_json is None:
        return 1
    if mmll_json == {} or mmll_json is None:
        return 2

    return -1
