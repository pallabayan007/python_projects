from azure.cosmos import exceptions, CosmosClient, PartitionKey
import json
import matplotlib.pyplot as plt

# Initialize the Cosmos client
endpoint = "https://codb.documents.azure.com:443/"
key = 'A1fRVJmZWPE6DIgoWIDArTgcYINE86TqVF5pWaLss46hht7RKObNJ9FEqkAILJJ4kWtE18b58GeG7xQepR9lWg=='

# <create_cosmos_client>
client = CosmosClient(endpoint, key)
# </create_cosmos_client>

# Create a database
# <create_database_if_not_exists>
database_name = 'analytics'
database = client.create_database_if_not_exists(id=database_name)
# </create_database_if_not_exists>

# Create a container
# Using a good partition key improves the performance of database operations.
# <create_container_if_not_exists>
container_name = 'raspberrypi'
container = database.create_container_if_not_exists(
    id=container_name,
    partition_key=PartitionKey(path="/partkey"),
    offer_throughput=400
)
# </create_container_if_not_exists>

# Query these items using the SQL query syntax.
# Specifying the partition key value in the query allows Cosmos DB to retrieve data only from the relevant partitions, which improves performance
# <query_items>
query = "SELECT * FROM c WHERE c.messageId>70 AND c.messageId<76"

items = list(container.query_items(
    query=query,
    enable_cross_partition_query=True
))

items.sort(key = lambda i: i['messageId'])

#print(json.dumps(items, indent=2))
# </query_items>

temperature = []
humidity = []
time = []

for item in items:
    t = item["dateTime"].split()
    temperature.append(item["temperature"])
    humidity.append(item["humidity"])
    time.append(t[1])

plt.title("Temperature Plot")
plt.plot(time, temperature)
plt.show()

plt.title("Humidity Plot")
plt.plot(time, humidity)
plt.show()