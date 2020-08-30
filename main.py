from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, send
from chatbot.gui_chatbot import send
from configparser import SafeConfigParser
from admin import *
from twilio.twiml.messaging_response import MessagingResponse
import socketio, json
import socket
import requests

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5000        # Port to listen on (non-privileged ports are > 1023)

app = Flask(__name__)
sio = SocketIO(app, cors_allowed_origins="*", manage_session=False)

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
@app.route("/general")
def home_general():
    return render_template("chatbot.html")

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
    print("input json: " + str(request.json))
    print("input: " + request.json["input"]["text"])
    msg = request.json["input"]["text"]
    client = request.json["input"]["client"]
    print("msg : " + msg + ": client : " + client) 
    if msg == "welcome":
        event_name = request.json["input"]["socket_id"]+"_my_message"
        print("event_name: " + event_name)
        sio.emit(event_name,"Welcome to Lima Chat Support Agent")    
    else:
        try:
            if "id" in msg:
                event_name = request.json["input"]["socket_id"]+"_my_message"
                print("event_name: " + event_name)
                sio.emit(event_name,"Please wait this may take upto few minutes!!")
            # if msg != '' and client!='':
            if client!='':
                # ints = predict_class(msg)
                # result = getResponse(ints, intents, msg)
                result = send(sio,request.json)
        except Exception as e:
            print('train_chatbot:: /api/message Failed: '+ str(e))
            result = "Oops! it seems there is some difficulties in the system, please try again later"   
        
        res = '{"output":{"text":"' + result + '"}}'  
        print('response to chat window: ' + res)  
        reply = json.loads(res)
        print(reply["output"])
        
        return reply
    

# Running the training module
@app.route("/api/training", methods=['GET', 'POST'])
def systemtraining():
    print('====Inside systemtraining====')
    req_data=request.get_data()
    req_data_json = json.loads(req_data)
    print(req_data)
    print(req_data_json['client'])

    if settingclientfortraining(req_data_json['client']):
        reply = runtraining()
        # print('systemtraining: ' + str(reply))
        return reply
    else:
        return str(False)
    

# Uploading file from admin portal
@app.route("/api/fileupload", methods=['GET', 'POST'])
def systemfileupload():
    print('====Inside systemfileupload====')
    print('====Inside request==== ' + request.content_type)
    reply = fileupload(request)
    print('fileupload from main: ' + reply)
    return reply

# getting the client names
@app.route("/api/getclients", methods=['GET', 'POST'])
def getclients():    
    reply = gettrainingclients()
    # print('fileupload from main: ' + reply)
    return reply

# =================================================================================
    # Definition of facebook social media functions
# =================================================================================
@app.route("/api/fb", methods=['GET', 'POST'])
def fbchat():
    print("inside fbchat")

    if request.method == 'GET':
        verify_token = "abcd"

        mode = request.args['hub.mode']
        token = request.args['hub.verify_token']
        challenge = request.args['hub.challenge']

        print(mode, token, challenge)

        if token == verify_token:
            return challenge, 200
        else:
            return "Validation failed", 503

    else:
        body = request.json

        print(body)
        if body['object'] == "page":

            for entry in body['entry']:
                for message in entry['messaging']:
                    sender_id = message['sender']['id']
                    text = message['message']['text']
                    print("in for")
                    print(sender_id, text)
                    sendtofb(sender_id, text)

            return "success", 200

        else:
            return "error", 503


def sendtofb(sender_id, text):

    access_token = "EAAUmPFiFbvMBAGbLJAyLzvF4F1LzKG4nw9ZBcO8LNJCGdoQqAHAM0uGTpJZBCU11KaHG8f9lofZAz1exb9wFoEhZBAAh97kIVya30ZAwL7Taq3OChRFoXPpsZBbaQmI7dIVvZArTkcfVj8s3y9LaZC2XkYSVsnlHQdBQSLRPPnZCBx2OUZAIzSIbDc"
    url = "https://graph.facebook.com/v8.0/me/messages?access_token=" + access_token
    
    
    sender_json = {
                    "input": {
                            "text": text,
                            "client": "general",
                            "socket_id": ""
                        }
                    }
    
    msg = send(sio, sender_json)
    body = {"messaging_type": "RESPONSE",
            "recipient": {
                "id": sender_json["sender_id"]
            },
            "message": {
                "text": msg
            }}

    x = requests.post(url, json=body)

    print("in func")
    print(x.text)

# =================================================================================
    # Definition of facebook social media functions
# =================================================================================


# =================================================================================
    # Definition of WhatsApp social media functions
# =================================================================================
@app.route("/api/wa", methods=['GET', 'POST'])
def wachat():
    incoming_msg = request.values.get('Body', '')
    print("====Inside whatsapp chat ===========")
    print(incoming_msg)
    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    sender_json = {
                    "input": {
                            "text": incoming_msg,
                            "client": "general",
                            "socket_id": ""
                        }
                    }
    print("sender_json: " + str(sender_json))
    try:
        reply_msg = send(sio, sender_json)
    except Exception as e:
        print('train_chatbot:: /api/wa Failed: '+ str(e))
        reply_msg = "Oops! it seems there is some difficulties in the system, please try again later"
    
    msg.body(reply_msg)
    responded=True

    if not responded:
        msg.body('Not sure I understand, Please try again')
    return str(resp)


# =================================================================================
    # Definition of WhatsApp social media functions
# =================================================================================

if __name__ == "__main__":
    sio.run(app, debug=True)
    # app.run(debug=True)
    # socketio.run(app, debug = True, use_reloader = False, port=PORT)
   
# print("socket connected: " + str(sio.on('connect').__str__))
@sio.on('message')
def handle_my_custom_event(data):
    print('received json: ' + data)
# =================================================================================
    # Definition of socket activity functions
# =================================================================================
# @sio.on('client_connected')
# def handle_client_connected_event(data):
#     clients.append(request.sid)
#     # print('============size===================: ' + str(len(clients))
#     # for client in clients:
#     #     sio.emit('chat_msg_return', jsonify(data))

# sio.on("connected")
# def client_connected():
#     conn, addr = sio.accept()
#     sio.on_event("message",on_foo_event)
#     print("Connected by client")
#     # print('Connected by', addr1)

# def on_foo_event(data):  
#         print('received json: ' + data) 

# @sio.on("message")
# def handle_message(data:str):
#     print('inside chat_msg_return')
#     # print("Socket ID: " , sid)
#     print("message:", data)
#     sio.emit('response', '{"msg":"Hello"}')
