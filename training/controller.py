from rest_framework.decorators import api_view
from rest_framework.response import Response
from commonutils import datasource as ds
from training.model import buildModel
from sklearn.model_selection import train_test_split
import logging


@api_view(['GET'])
def controller(request):

    client = request.GET.get('client')

    try:
        input_data, output_data = ds.getData(client, "train")

        input_train, input_test, output_train, output_test = train_test_split(input_data, output_data, test_size=0.3)

        buildModel(client, input_train, output_train)

        return Response({'status': True})
    except Exception as e:
        logging.exception(e)
        return Response({'status': False})


