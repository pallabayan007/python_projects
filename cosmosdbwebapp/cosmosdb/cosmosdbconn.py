from django.shortcuts import render
from rest_framework.views import APIView
import matplotlib.pyplot as plt
import io
import urllib, base64

def graphs(request):
    temperature = [28, 21.5, 21, 22.5, 28]
    humidity = [74.5, 63.5, 65, 63, 66]
    time = ["12:10:00", "12:20:00", "12:30:00", "12:40:00", "12:50:00"]

    plt.title("Temperature Plot")
    plt.plot(time, temperature)

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri1 = urllib.parse.quote(string)

    plt.clf()

    plt.title("Humidity Plot")
    plt.plot(time, humidity)

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri2 = urllib.parse.quote(string)

    return render(request, 'home.html', {'data1':uri1, 'data2':uri2})