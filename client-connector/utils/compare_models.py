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


class CompareModels:

    def __init__(self):
        import pandas as pd
        self._models = pd.DataFrame(
            data=['r', 'R^2', 'RMSE', 'RMSRE', 'MAPE'],
            columns=['Model']
        ).set_index(keys='Model')

    def add(self, model_name, y_test, y_pred):
        import numpy as np
        from sklearn.metrics import r2_score, mean_squared_error
        self._models[model_name] = np.array(
            object=[
                np.corrcoef(y_test, y_pred)[0, 1], # r
                r2_score(y_true=y_test, y_pred=y_pred), # R^2
                np.sqrt(mean_squared_error(y_true=y_test, y_pred=y_pred)), # RMSE
                np.sqrt(np.mean(((y_test-y_pred)/y_test)**2)), # RMSRE
                np.mean(np.abs((y_test-y_pred) / y_test)) * 100 # MAPE
            ]
        )

    def R2AndRMSE(y_test, y_pred):
        import numpy as np
        from sklearn.metrics import r2_score, mean_squared_error
        return r2_score(y_true=y_test, y_pred=y_pred), np.sqrt(mean_squared_error(y_true=y_test, y_pred=y_pred))

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self, _):
        print('Cannot perform such task.')

    def show(self, **kwargs):
        import matplotlib.pyplot as plt
        kwargs['marker'] = kwargs.get('marker', 'X')
        self._models.plot(**kwargs)
        plt.xticks(range(len(self._models)), self._models.index)
        plt.xlabel('')
        plt.axis('auto')
        plt.show()

    def savefig(self, output_filename, **kwargs):

        import matplotlib.pyplot as plt
        kwargs['marker'] = kwargs.get('marker', 'X')
        self._models.plot(**kwargs)
        plt.xticks(range(len(self._models)), self._models.index)
        plt.xlabel('')
        plt.axis('auto')
        plt.savefig(output_filename)
