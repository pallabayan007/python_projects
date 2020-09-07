from django.shortcuts import render
from pymongo import MongoClient
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
import logging

import landing.configreader as cfgr


@api_view(['GET'])
def landing_prediction(request):
    return render(request, 'landing_prediction.html', {'clients': getClients()})


@api_view(['GET'])
def landing_training(request):
    return render(request, 'landing_training.html', {'clients': getClients()})


@api_view(['POST'])
@parser_classes([FileUploadParser])
def fileupload(request):

    try:
        upload_directory = ""
        filename = request.headers.get('filename')
        filetype = request.headers.get('filetype')

        if filetype.lower().find('training')>=0:
            upload_directory = "datasets/"
        if filetype.lower().find('config')>=0:
            upload_directory = "configs/"

        file = request.data['file']

        with open(upload_directory + filename, "wb+") as fp:
            for chunk in file.chunks():
                fp.write(chunk)

        return Response({'status': True})

    except Exception as e:
        logging.exception(e)
        return Response({'status': False})


def getClients():

    mongoClient = MongoClient(cfgr.config['mongodb']['url'])
    db = mongoClient[cfgr.config['mongodb']['database']]
    collection = db[cfgr.config['mongodb']['collection']]
    client_details = collection.find({}, {'_id': 0})
    client_details = list(client_details)

    clients = []

    for client in client_details:
        clients.append(client['client'])

    return clients