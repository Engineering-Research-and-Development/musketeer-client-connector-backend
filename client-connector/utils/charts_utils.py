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

from PIL import Image
from io import BytesIO
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix
from utils.compare_models import CompareModels

import json
import traceback
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sn
import logging
import configparser

# Set up logger
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('chart utils')
logger.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read('app.ini')

SERVER_DB_PATH = config["SERVER"]["SERVER_DB_PATH"]


def create_chart(user, master_node, pom, algorithm_name, type, task_name, model, x, y_tst):

    if algorithm_name == "LC_pm":

        x_b = master_node.add_bias(x)
        preds = model.predict(x_b)

    else:

        preds = model.predict(x)

    if type in ['clustering']:

        clustering_pca(user.lower(), x, preds, task_name)

    elif type in ['classification']:

        y = np.argmax(y_tst, axis=-1)  # Convert to labels
        preds = np.argmax(preds, axis=-1)  # Convert to labels

        try:
            classes = np.arange(y_tst.shape[1])
        except:
            classes = np.unique(y_tst)
            y = y_tst
            preds = (model.predict(x) > 0.5).astype('int32')

        plot_cm_seaborn(user.lower(), preds, y, classes, task_name=task_name, normalize=True)

    elif type in ['regression']:

        preds = model.predict(x)

        plt = CompareModels()
        try:
            plt.add(model_name="Regression - evaluation metrics", y_test=y_tst, y_pred=preds)
        except:
            plt.add(model_name="Regression - evaluation metrics", y_test=y_tst.flatten(), y_pred=preds.flatten())

        output_filename = 'results/' + task_name + '_' + user + '.png'
        plt.savefig(output_filename)


def clustering_pca(user, x, preds, task_name):

    if len(x[0]) == 2:

        try:
            fig = plt.figure(figsize=(10, 8))
            plt.scatter(x[:, 0], x[:, 1], c=preds)
            plt.xlabel('x')
            plt.ylabel('y')
            plt.title('Clustering')
            plt.grid(True)
            output_filename = 'results/' + task_name + '_' + user + '.png'
            plt.savefig(output_filename)

        except Exception:
            traceback.print_exc()
    else:
        try:
            # PCA 2D Visualisation of the data
            pca = PCA(n_components=2)
            pca_input = x
            X_pca = pca.fit(pca_input).transform(pca_input)
            fig = plt.figure(figsize=(10, 8))
            plt.scatter(X_pca[:,0], X_pca[:, 1], c=preds)
            plt.xlabel('PCA component 1')
            plt.ylabel('PCA component 2')
            plt.title(' Clustering with 2 PCA components')
            plt.grid(True)
            output_filename = 'results/' + task_name + '_' + user + '.png'
            plt.savefig(output_filename)

        except Exception:
            traceback.print_exc()


def plot_cm_seaborn(user, preds, y, classes, task_name, normalize=False, cmap=plt.cm.GnBu):

    cnf_matrix = confusion_matrix(y, preds)

    if normalize:
        cnf_matrix = cnf_matrix.astype('float') / cnf_matrix.sum(axis=1)[:, np.newaxis]
        fmt = '.2f'
    else:
        fmt = 'd'

    df = pd.DataFrame(cnf_matrix, columns=classes, index=classes)
    plt.figure(figsize=(10, 8))
    ax = sn.heatmap(df, annot=True, cmap=cmap, linewidths=.5, cbar=False, fmt=fmt)
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom + 0.5, top - 0.5)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.title("Confusion Matrix - " + task_name)
    output_filename = 'results/' + task_name + '_' + user + '.png'
    plt.savefig(output_filename)


def add_image_result(task_name, relative_path):

    with open(SERVER_DB_PATH, "r") as jsonFile:
        data = json.load(jsonFile)

    with open(SERVER_DB_PATH, "r") as jsonFileBackup:
        backup_data = json.load(jsonFileBackup)

    data["image-results"][task_name] = os.getcwd()+"/"+relative_path

    try:
        with open(SERVER_DB_PATH, "w") as jsonFile:
            json.dump(data, jsonFile)
    except:
        print("Error: backup json")
        with open(SERVER_DB_PATH, "w") as jsonFileBackup:
            json.dump(backup_data, jsonFileBackup)
        raise
    return


def get_chart(url):

    im = Image.open(url)
    io = BytesIO()
    im.save(io, format='PNG')

    return io.getvalue()
