from azure.cosmos import exceptions, CosmosClient, PartitionKey
import pandas as pd
from pymongo import MongoClient


def getData(config, client):

    endpoint, key, database_name, input_container_name, output_container_name, partitionkey = getClientDetails(config, client)

    cosmosClient = CosmosClient(endpoint, key)

    database = cosmosClient.create_database_if_not_exists(id=database_name)

    query = "SELECT * FROM c"

    container = database.create_container_if_not_exists(
        id=input_container_name,
        partition_key=PartitionKey(path=partitionkey),
        offer_throughput=400
    )

    input = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    container = database.create_container_if_not_exists(
        id=output_container_name,
        partition_key=PartitionKey(path=partitionkey),
        offer_throughput=400
    )

    output = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    timestamp = []

    for item in input:
        timestamp.append(item['timestamp'])
        item.pop('timestamp')
        item.pop('id')
        item.pop('_rid')
        item.pop('_self')
        item.pop('_etag')
        item.pop('_attachments')
        item.pop('_ts')

    for item in output:
        item.pop('id')
        item.pop('_rid')
        item.pop('_self')
        item.pop('_etag')
        item.pop('_attachments')
        item.pop('_ts')

    input_df = pd.DataFrame(list(input))
    output_df = pd.DataFrame(list(output))

    input = input_df.to_numpy()
    output = output_df.to_numpy()

    return input, output, input_df.columns.values, output_df.columns.values

def getClientDetails(config, client):

    mongoClient = MongoClient(config['mongodb']['url'])
    db = mongoClient[config['mongodb']['database']]
    collection = db[config['mongodb']['collection']]
    client_details = collection.find({'client': client}, {'_id': 0})
    client_details = list(client_details)

    return client_details[0]['endpoint'], client_details[0]['key'], client_details[0]['database_name'], client_details[0]['input_container_name'], client_details[0]['output_container_name'], client_details[0]['partitionKey']