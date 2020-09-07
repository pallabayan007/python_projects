from pymongo import MongoClient
from commonutils import configreader as cfgr


def getMongoConn():

    dataconfig = cfgr.dataconfigread()
    mongoClient = MongoClient(dataconfig['mongodb']['url'])
    db = mongoClient[dataconfig['mongodb']['database']]
    collection = db[dataconfig['mongodb']['collection']]

    return collection

