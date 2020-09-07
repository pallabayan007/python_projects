import pandas as pd
from pymongo import MongoClient


def getData(config, client):

    input_df = pd.read_json(config[client]["input_file"])
    input = input_df.to_numpy()

    output_df = pd.read_json(config[client]["output_file"])
    output = output_df.to_numpy()

    return input, output, input_df.columns.values, output_df.columns.values

def getClientDetails(config, client):

    mongoClient = MongoClient(config['mongodb']['url'])
    db = mongoClient[config['mongodb']['database']]
    collection = db[config['mongodb']['collection']]
    client_details = collection.find({'client': client}, {'_id': 0})
    client_details = list(client_details)

    return client_details[0]['endpoint'], client_details[0]['key'], client_details[0]['database_name'], client_details[0]['input_container_name'], client_details[0]['output_container_name'], client_details[0]['partitionKey']