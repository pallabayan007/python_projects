import configparser
from commonutils import mongoconn as mc


def dataconfigread():
    config = configparser.ConfigParser(interpolation=None)
    config.read('configs/dataconfig.ini')
    return config

def clientconfigread(clientname):

    dataconfig = dataconfigread()
    collection = mc.getMongoConn()
    client_details = collection.find({}, {'_id': 0})
    client_details = list(client_details)

    clients = []

    for client in client_details:
        clients.append(client['client'])

    configs = {}

    for i in range (0, len(clients)):
        config = configparser.ConfigParser(interpolation=None)
        config.read('configs/'+clients[i]+'graphconfig.ini')
        configs[clients[i]] = config

    return configs[clientname]