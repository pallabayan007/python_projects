import numpy as np
from commonutils import mongoconn as mc
from commonutils import configreader as cfgr
from getdata import cosmosdbdata, csvdata, jsondata, mongodbdata


def getData(client, operation):

    collection = mc.getMongoConn()
    client_details = collection.find({'client': client}, {'_id': 0})
    client_details = list(client_details)

    type = client_details[0]['type']

    if type == "cosmosdb":
        input, output, input_columns, output_columns = cosmosdbdata.getData(cfgr.dataconfigread(), client)
        input_max, input = normalize(input)
        output_max, output = normalize(output)
        if operation == "train":
            return input, output
        if operation == "predict":
            return input_max, input, output_max, output, input_columns, output_columns
    elif type == "csv":
        input, output, input_columns, output_columns = csvdata.getData(cfgr.dataconfigread(), client)
        input_max, input = normalize(input)
        output_max, output = normalize(output)
        if operation == "train":
            return input, output
        if operation == "predict":
            return input_max, input, output_max, output, input_columns, output_columns
    elif type == "json":
        input, output, input_columns, output_columns = jsondata.getData(cfgr.dataconfigread(), client)
        input_max, input = normalize(input)
        output_max, output = normalize(output)
        if operation == "train":
            return input, output
        if operation == "predict":
            return input_max, input, output_max, output, input_columns, output_columns
    elif type == "mongodb":
        input, output, input_columns, output_columns = mongodbdata.getData(cfgr.dataconfigread(), client)
        input_max, input = normalize(input)
        output_max, output = normalize(output)
        if operation == "train":
            return input, output
        if operation == "predict":
            return input_max, input, output_max, output, input_columns, output_columns

def normalize(data):

    maximums = np.amax(abs(data), axis=0)

    if hasattr(maximums, "__len__"):
        for i in range (0, len(maximums)):
            if maximums[i]==0 :
                maximums[i]=1

        return maximums, data/maximums
    else:
        if maximums == 0:
            maximums = 1
        return maximums, data/maximums
