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


from flask import Flask, request, Response, jsonify, session, g
from flask_cors import CORS, cross_origin
from services.comms import authentication
from services.comms.tasks import Tasks
from services.cc import dataset, configuration
from services.catalogue import catalogue
from services.fml import running_subprocess
from utils import charts_utils, platform_utils, logger
from utils.error_utils import RegistrationError
from communication_abstract_interface import ServerException, MalformedResponseException, DispatchException, BadNotificationException, TaskException
from user import User

import pika
import json
import uuid
import logging

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

app.config['CORS_HEADERS'] = 'Content-Type'
app.config.update(
    SESSION_COOKIE_HTTPONLY=False
)

CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG


credentials = "./config.json"
user_obj = None

"""
ERRORS HANDLER
"""


@app.errorhandler(RegistrationError)
def server_error(error):
    return jsonify({'message': str(error)}), 500, {'ContentType': 'application/json'}


@app.errorhandler(FileNotFoundError)
def file_not_found_error(error):
    return jsonify({'message': error.strerror}), 404, {'ContentType': 'application/json'}


@app.errorhandler(ServerException)
def server_error(error):
    return jsonify({'message': str(error)}), 500, {'ContentType': 'application/json'}


@app.errorhandler(MalformedResponseException)
def server_error(error):
    return jsonify({'message': str(error)}), 400, {'ContentType': 'application/json'}


@app.errorhandler(DispatchException)
def server_error(error):
    return jsonify({'message': str(error)}), 400, {'ContentType': 'application/json'}


@app.errorhandler(BadNotificationException)
def server_error(error):
    return jsonify({'message': str(error)}), 400, {'ContentType': 'application/json'}


@app.errorhandler(TaskException)
def server_error(error):
    return jsonify({'message': str(error)}), 400, {'ContentType': 'application/json'}


@app.errorhandler(pika.exceptions.AuthenticationError)
def authentication_error(error):
    return jsonify({'message': error.args[1]}), error.args[0], {'ContentType': 'application/json'}


@app.errorhandler(pika.exceptions.ProbableAuthenticationError)
def authentication_error(error):
    return jsonify({'message': error.args[1]}), error.args[0], {'ContentType': 'application/json'}


@app.errorhandler(pika.exceptions.ChannelError)
def authentication_error(error):
    return jsonify({'message': error.args[1]}), error.args[0], {'ContentType': 'application/json'}


@app.errorhandler(Exception)
def server_error(error):
    return jsonify({'message': str(error)}), 500, {'ContentType': 'application/json'}


"""
BEFORE REQUEST
"""


@app.before_request
def before_request():

    endpoints = ["login_user", "register_user",
                 "get_comm_configurations", "set_comm_configurations",
                 "get_mmll_configurations", "set_mmll_configurations",
                 "get_catalogue_configurations", "set_catalogue_configurations",
                 "get_step_configurations", "logout_user"]
    g.user = None
    logging.info('Endpoint: ' + str(request.endpoint) + ' ; Method: ' + str(request.method))

    # Manage OPTIONS preflight
    if request.method == 'OPTIONS':

        logging.info("Preflight OPTIONS")

    elif 'user_id' in session and user_obj is not None:
        if user_obj.id == session['user_id']:
            g.user = user_obj
            logging.info('User already logged: ' + str(g.user))

    elif request.endpoint not in endpoints:
        logging.info("Unauthorized..")
        return Response('Unauthorized', 401)


"""
AFTER REQUEST
"""


@app.after_request
def after_request(response):

    header = response.headers
    header['Access-Control-Allow-Credentials'] = "true"
    header['Access-Control-Allow-Headers'] = "Origin, Content-Type, X-Auth-Token, content-type"
    header["Access-Control-Allow-Origin-Methods"] = "GET,POST,OPTIONS"
    # header["Access-Control-Allow-Origin"] = "*"

    return response


"""
CATALOGUE
"""


@app.route('/cc/catalogue/algorithms', methods=['GET'])
def get_algorithms():
    """
    Retrieve list of algorithms registered
    """

    algorithms = catalogue.get_algorithms()

    return json.dumps({"algorithms": algorithms})


@app.route('/cc/catalogue/poms', methods=['GET'])
def get_poms():
    """
    Retrieve list of POMs registered
    """

    poms = catalogue.get_poms()

    return json.dumps({"poms": poms})


"""
CLIENT CONNECTOR / CONFIGURATIONS
"""


@app.route('/cc/configurations/step', methods=['GET'])
def get_step_configurations():

    step = configuration.get_step_configurations()

    return json.dumps({'step': step}), 200, {'ContentType': 'application/json'}


@app.route('/cc/configurations/comm', methods=['POST'])
def set_comm_configurations():

    data = request.json

    configuration.set_comm_json_configurations(data)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/cc/configurations/comm', methods=['GET'])
def get_comm_configurations():

    configurations = configuration.get_comm_json_configurations()

    return json.dumps({'configurations': configurations}), 200, {'ContentType': 'application/json'}


@app.route('/cc/configurations/mmll', methods=['POST'])
def set_mmll_configurations():

    data = request.json

    configuration.set_mmll_json_configurations(data)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/cc/configurations/mmll', methods=['GET'])
def get_mmll_configurations():

    configurations = configuration.get_mmll_json_configurations()

    return json.dumps({'configurations': configurations}), 200, {'ContentType': 'application/json'}


@app.route('/cc/datasets', methods=['GET'])
def get_datasets():

    datasets = dataset.get_datasets()

    return json.dumps(datasets)


@app.route('/cc/results/image', methods=['GET'])
def get_result_task_image():

    task_name = request.args.get('task')

    url = "results/"+task_name+".png"

    image = charts_utils.get_chart(url)

    return Response(image, mimetype='image/png')


@app.route('/cc/results/stream/logs', methods=['GET'])
@cross_origin()
def get_result_task_log_stream_json():

    user = g.user.username
    task_name = request.args.get('task')
    mode = request.args.get('mode')  # participant or aggregator

    response = Response(mimetype='text/event-stream')
    response.headers.add_header('Cache-Control', 'no-cache')
    response.headers.add_header('Connection', 'keep-alive')

    return response


@app.route('/cc/datasets', methods=['POST'])
def add_dataset():

    data = request.json

    type = data["type"]
    spec = data["spec"]

    dataset.add_dataset(type, spec)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


"""
COMMUNICATIONS
"""


@app.route('/cc/comms/login', methods=['POST'])
def login_user():

    data = request.json

    user = data['user']
    password = data['password']

    if authentication.login(credentials, user, password):

        user_id = uuid.uuid4()
        session['user_id'] = user_id
        global user_obj
        user_obj = User(id=user_id, username=user, password=password)
        logging.info('User logged: ' + str(user_obj.username))

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/cc/comms/logout", methods=['POST'])
@cross_origin()
def logout_user():

    del session['user_id']
    global user_obj
    user_obj = None

    return json.dumps({'success': True}), 200


@app.route('/cc/comms/registration', methods=['POST'])
def register_user():

    data = request.json

    user = data['user']
    password = data['password']
    org = data['org']

    authentication.registration(credentials=credentials, user=user, password=password, org=org)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/cc/comms/tasks', methods=['GET', 'POST'])
@cross_origin()
def tasks():

    user = g.user.username
    password = g.user.password

    if request.method == 'GET':

        result = Tasks(credentials=credentials, user=user, password=password).get_tasks()

    elif request.method == 'POST':

        data = request.json

        user = g.user.username
        password = g.user.password
        task_name = data['task_name']
        task_definition = data['definition']

        result = Tasks(credentials=credentials, user=user, password=password).add_task(task_name, task_definition)

    return json.dumps(result), 200, {'ContentType': 'application/json'}


@app.route('/cc/comms/tasks/assigned', methods=['GET'])
def get_user_assignments():

    user = g.user.username
    password = g.user.password

    tasks = Tasks(credentials=credentials, user=user, password=password).get_user_assignments()

    return json.dumps(tasks), 200, {'ContentType': 'application/json'}


"""
FEDERATED MACHINE LEARNING
"""


# TO REMOVE
@app.route('/cc/fml/join', methods=['POST'])
def join_task():

    data = request.json

    user = g.user.username
    password = g.user.password
    task_name = data['task_name']

    result = Tasks(credentials=credentials, user=user, password=password).join_task(task_name=task_name)

    return json.dumps(result), 200, {'ContentType': 'application/json'}


@app.route('/cc/fml/aggregate', methods=['POST'])
def aggregate_task():

    data = request.json

    user = g.user.username
    password = g.user.password
    task_name = data['task_name']
    datasets = json.dumps(data['datasets'])

    # Run the aggregator
    running_subprocess.AggregatorSubProcessV2(credentials, user, password, task_name, datasets).run()

    return json.dumps({"message": "Task " + str(task_name) + " started as aggregator."}), 200, {'ContentType': 'application/json'}


@app.route('/cc/fml/participate', methods=['POST'])
def participate_task():

    data = request.json

    user = g.user.username
    password = g.user.password
    task_name = data['task_name']
    datasets = json.dumps(data['datasets'])

    # Join the task
    Tasks(credentials=credentials, user=user, password=password).join_task(task_name=task_name)

    # Run the participant
    running_subprocess.ParticipantSubProcessV2(credentials, user, password, task_name, datasets).run()

    return json.dumps({"message": "Task " + str(task_name) + " started as participant."}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0')
