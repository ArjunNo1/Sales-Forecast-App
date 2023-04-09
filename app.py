import os
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from passlib.hash import pbkdf2_sha256
from sklearn import metrics
from math import sqrt
from sklearn.metrics import mean_squared_error
from dateutil import parser
import statsmodels.api as sm
from pylab import rcParams
import pymongo
from contextlib import nullcontext
import datetime
from functools import wraps
from http.client import HTTPException
from flask import Flask, request, jsonify, session
import json
from flask_cors import CORS

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore', ConvergenceWarning)


app = Flask(__name__)

CORS(app)


UPLOAD_FOLDER = 'upload_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def handle_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file included in request.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if file and allowed_file(file.filename):
        # Do something with the file
        return jsonify({'message': 'File uploaded successfully.'}), 200
    else:
        return jsonify({'error': 'Invalid file format.'}), 400


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'xls', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/form", methods=["GET", "POST"])
def postPrediction():
    if request.method == 'POST':
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        data = pd.read_csv(file_path, encoding='unicode_escape')
        num = request.form.get('num')
        to_drop = ['ADDRESSLINE2', 'STATE', 'POSTALCODE', 'TERRITORY', 'PRODUCTCODE',
                   'CUSTOMERNAME', 'PHONE', 'ADDRESSLINE1', 'CITY', 'CONTACTLASTNAME', 'CONTACTFIRSTNAME']
        data = data.drop(to_drop, axis=1)
        data['STATUS'].unique()
        data['STATUS'] = pd.factorize(data.STATUS)[0] + 1
        data['PRODUCTLINE'].unique()
        data['PRODUCTLINE'] = pd.factorize(data.PRODUCTLINE)[0] + 1
        data['COUNTRY'].unique()
        data['COUNTRY'] = pd.factorize(data.COUNTRY)[0] + 1
        data['DEALSIZE'].unique()
        data['DEALSIZE'] = pd.factorize(data.DEALSIZE)[0] + 1
        data['ORDERDATE'] = pd.to_datetime(data['ORDERDATE'])
        df = pd.DataFrame(data)
        data.sort_values(by=['ORDERDATE'], inplace=True)
        data.set_index('ORDERDATE', inplace=True)
        df.sort_values(by=['ORDERDATE'], inplace=True, ascending=True)
        df.set_index('ORDERDATE', inplace=True)
        new_data = pd.DataFrame(df['SALES'])
        new_data = pd.DataFrame(new_data['SALES'].resample('D').mean())
        new_data = new_data.interpolate(method='linear')

        # # Method to Checking for Stationary: A stationary process has the property that the mean, variance and autocorrelation structure do not change over time.
        train, test, validation = np.split(new_data['SALES'].sample(frac=1), [
            int(.6*len(new_data['SALES'])), int(.8*len(new_data['SALES']))])
        # print('Train Dataset')
        # print(train)
        # print('Test Dataset')
        # print(test)
        # print('Validation Dataset')
        # print(validation)
        met = {"mae": 0, "mape": 0, "mse": 0, "ForecastedData": {}}
        # # SARIMA MODEL
        mod = sm.tsa.statespace.SARIMAX(new_data,
                                        order=(1, 1, 1),
                                        seasonal_order=(1, 1, 1, 12),
                                        enforce_invertibility=False)
        results = mod.fit()
        # pred = results.get_prediction()
        pred = results.get_prediction(
            start=pd.to_datetime('2003-01-06'), dynamic=False)
        pred.conf_int()
        y_forecasted = pred.predicted_mean
        y_truth = new_data['SALES']

        mse = mean_squared_error(y_truth, y_forecasted)
        rmse = sqrt(mse)
        mae = metrics.mean_absolute_error(y_forecasted, y_truth)
        mape = metrics.mean_absolute_percentage_error(
            y_truth, y_forecasted)
        mape = round(mape*100, 2)
        forecast = results.forecast(steps=int(num))
        forecast = forecast.astype('int')
        forecast_df = forecast.to_frame()
        forecast_df.reset_index(level=0, inplace=True)
        forecast_df.columns = ['PredictionDate', 'PredictedColumn']
        # print(forecast_df)
        frame = pd.DataFrame(forecast_df)
        # print(frame)
        frameDict = frame.to_dict('records')
        # print(frameDict)
        predicted_date = []
        predicted_column = []
        frameDict = {}

        for i in range(len(frame)):
            tempStr = str(frame.iloc[i]['PredictionDate'])
            dt = parser.parse(tempStr)
            key = dt.strftime('%A')[0:3]+', '+str(dt.day) + \
                ' '+dt.strftime("%b")[0:3]+' '+str(dt.year)
            value = int(frame.iloc[i]['PredictedColumn'])
            frameDict[key] = value
            met = {"mae": mae, "mape": mape,
                   "mse": mse, "ForecastedData": frameDict}
            prediction = frame.to_csv(
                'upload_files/prediction.csv', index=False)
            # dfnew = pd.read_csv('upload_files/prediction.csv')
            # print("Metrics : ", met)
        
        return jsonify(met)
    else:
        print(f"Error processing file")

    # Return a success message
    return jsonify({'message': 'Prediction successfull'})


if __name__ == "__main__":
    app.run(debug=True)
