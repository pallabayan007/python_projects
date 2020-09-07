import json
from django.shortcuts import render
from rest_framework.decorators import api_view
from commonutils import datasource as ds
from prediction.prediction import getPrediction
from sklearn.model_selection import train_test_split
import logging
from commonutils import configreader as cfgr
from operator import itemgetter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import urllib, base64

@api_view(['GET'])
def controller(request):

    client = request.GET.get('client')

    try:
        input_max, input_data, output_max, output_data, input_columns, output_columns = ds.getData(client, "predict")

        input_train, input_test, output_train, output_test = train_test_split(input_data, output_data, test_size=0.3)

        predictions = getPrediction(client, input_test, output_test)

        if len(cfgr.clientconfigread(client).sections()) < 1:
            return render(request, 'error.html')
        else:
            uri = {}
            print(cfgr.clientconfigread(client).sections())
            for i in range (0, len(cfgr.clientconfigread(client).sections())):
                par = cfgr.clientconfigread(client)['graph'+str(i)]['x']
                uri['data'+str(i)] = getGraph(par, client, input_test*input_max, predictions, input_columns)

            return render(request, 'graphs.html', {'uri': json.dumps(uri), 'client': client.upper()})

    except Exception as e:
        logging.exception(e)
        return render(request, 'error.html')

def getGraph(par, client, input, y, column):

    input = np.ndarray.tolist(input)
    y = np.ndarray.tolist(y)
    x = []

    for i in range (0, len(input)):
        x.append(input[i][np.where(column == par)[0][0]])

    data = []

    for i in range (0, len(x)):
        data.append({'x': x[i], 'y': y[i][0]})

    data = sorted(data, key=lambda i:i['x'])

    x = list(map(itemgetter('x'), data))
    y = list(map(itemgetter('y'), data))

    plt.title(par + " graph")
    plt.plot(x, y)
    plt.xlabel(par)
    plt.ylabel("Probability")
    plt.grid(which='both', axis='both', linestyle='-')

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    plt.clf()

    return uri