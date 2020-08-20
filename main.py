from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, send
from chatbot.gui_chatbot import send
from configparser import SafeConfigParser
from admin import *
import socketio, json

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

app = Flask(__name__)
sio = SocketIO(app, manage_session=False)

parser = SafeConfigParser()


# # create a Socket.IO server
# sio = socketio.Server()

# # wrap with a WSGI application
# app = socketio.WSGIApp(sio, app)

clients = []

# =================================================================================================
# Section for client routing
# =================================================================================================
# These routing are made for different client's chatbot landing page
# The url is used to get the client name from the end 
# The client name is passed in to sendrequest of api.js
@app.route("/bank")
def home_bank():
    # parser['clients']['client'] = 'bank'
    # parser.add_section('clients')
    # parser.set('clients', 'client', 'bank')
    # # with open('chatbot/server.ini', 'w') as configfile:
    # #         parser.write(configfile)
    # parser.clear
    return render_template("chatbot.html")

@app.route("/healthcare")
def home_healthcare():
    # parser.add_section('clients')
    # parser['clients']['client'] = 'healthcare'
    # # with open('chatbot/server.ini', 'w') as configfile:
    # #         parser.write(configfile)
    # parser.clear
    return render_template("chatbot.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

# =================================================================================================

@app.route("/api/message", methods=['GET', 'POST'])
def chatcomm():
    print('inside api message')
    print("input: " + request.json["input"]["text"])
    msg = request.json["input"]["text"]
    client = request.json["input"]["client"]
    print("msg : " + msg + ": client : " + client) 
    try:
        if msg != '' and client!='':
            # ints = predict_class(msg)
            # result = getResponse(ints, intents, msg)
            result = send(msg,client)
    except:
        result = "Oops! it seems there is some difficulties in the system, please try again later"   
    
    res = '{"output":{"text":"' + result + '"}}'  
    print('response to chat window: ' + res)  
    reply = json.loads(res)
    # print("response type: " + reply["output"])
    return reply

# Running the training module
@app.route("/api/training", methods=['GET', 'POST'])
def systemtraining():
    print('====Inside systemtraining====')
    reply = runtraining()
    # print('systemtraining: ' + str(reply))
    return reply

# Uploading file from admin portal
@app.route("/api/fileupload", methods=['GET', 'POST'])
def systemfileupload():
    print('====Inside systemfileupload====')
    print('====Inside request==== ' + request.content_type)
    reply = fileupload(request)
    print('fileupload from main: ' + reply)
    return str(True)

if __name__ == "__main__":
    sio.run(app, app.debug==True)
    # app.run(debug=True)
    # socketio.run(app, debug = True, use_reloader = False, port=PORT)
    
    
# =================================================================================
    # Definition of socket activity functions
# =================================================================================
@sio.on('client_connected')
def handle_client_connected_event(data):
    clients.append(request.sid)
    # print('============size===================: ' + str(len(clients))
    # for client in clients:
    #     sio.emit('chat_msg_return', jsonify(data))

@sio.on("connected")
@sio.on("message")
def handle_message(data:str):
    print('inside chat_msg_return')
    # print("Socket ID: " , sid)
    print("message:", data)
    sio.emit('response', "hello")
