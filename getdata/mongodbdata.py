import pandas as pd
from pymongo import MongoClient

def getData(config, client):

    url, database, collection_input, collection_output = getClientDetails(config, client)

    mongoClient = MongoClient(url)
    db = mongoClient[database]
    inputcollection = db[collection_input]
    outputcollection = db[collection_output]

    inputdataset = inputcollection.find({}, {'_id': 0})
    outputdataset = outputcollection.find({}, {'_id': 0})

    input_df = pd.DataFrame(list(inputdataset))
    output_df = pd.DataFrame(list(outputdataset))

    input = input_df.to_numpy()
    output = output_df.to_numpy()

    return input, output, input_df.columns.values, output_df.columns.values

def getClientDetails(config, client):

    mongoClient = MongoClient(config['mongodb']['url'])
    db = mongoClient[config['mongodb']['database']]
    collection = db[config['mongodb']['collection']]
    client_details = collection.find({'client': client}, {'_id': 0})
    client_details = list(client_details)

    return client_details[0]['url'], client_details[0]['database'], client_details[0]['collection_input'], client_details[0]['collection_output']