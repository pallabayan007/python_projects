from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, send
from chatbot.gui_chatbot import send, clear_expired_contexts
from configparser import SafeConfigParser
from admin import *
from twilio.twiml.messaging_response import MessagingResponse
import socketio, json
import socket
import requests
import re

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
    # if current_context != "" :
    if msg == "welcome" :
        # event_name = request.json["input"]["socket_id"]+"_my_message"
        # print("event_name: " + event_name)
        # sio.emit(event_name,"Welcome to Lima Chat Support Agent")   
        print("==================current_context from main===================")
        # print()
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
            print('chatcomm:: /api/message Failed: '+ str(e))
            result = "Oops! it seems there is some difficulties in the system, please try again later"   
        
        try:
            print(result)
            result_text = result['response']
            result_tag = result['tag']
            res = '{"output":{"tag": "' + result_tag + '", "text":"' + result_text + '"}}'  
            print('response to chat window: ' + res)
            reply = json.loads(res)
            print(reply["output"])
            print(reply)
        except Exception as e:
            print('chatcomm:: /api/message Failed: '+ str(e))
            # result = "Oops! it seems there is some difficultie(s) in the system, please try again later"
        
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
    print('====Inside getclients====')
    reply = gettrainingclients()
    # print('fileupload from main: ' + reply)
    return reply

# Clearing the expired sessions
@app.route("/api/clearsessions", methods=['GET', 'POST'])
def clear_context_sessions():    
    print('====Inside clear_context_sessions====')
    print(request.data)
    print(type(request.data))
    request_json = (json.loads(request.data))
    print(request_json)
    print(request_json['sockid'])
    reply = clear_expired_contexts(request_json['sockid'])
    return str(reply)

# =================================================================================
    # Definition of facebook social media functions
# =================================================================================
@app.route("/api/fb", methods=['GET', 'POST'])
def fbchat():
    try:
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
    except Exception as e:
        print('fbchat:: /api/fb Failed: '+ str(e))
        sendtofb(sender_id, "Thanks")
        return "success", 200
    

    


def sendtofb(sender_id, text):

    try:
        access_token = "EAAUmPFiFbvMBAGbLJAyLzvF4F1LzKG4nw9ZBcO8LNJCGdoQqAHAM0uGTpJZBCU11KaHG8f9lofZAz1exb9wFoEhZBAAh97kIVya30ZAwL7Taq3OChRFoXPpsZBbaQmI7dIVvZArTkcfVj8s3y9LaZC2XkYSVsnlHQdBQSLRPPnZCBx2OUZAIzSIbDc"
        url = "https://graph.facebook.com/v8.0/me/messages?access_token=" + access_token
        
        
        sender_json = {
                        "input": {
                                "text": text,
                                "client": "bank",
                                "socket_id": sender_id
                            }
                        }
        
        msg = send(sio, sender_json)
        reply_msg = msg['response']
        body = {"messaging_type": "RESPONSE",
                "recipient": {
                    "id": sender_id
                },
                "message": {
                    "text": reply_msg
                }}

        x = requests.post(url, json=body)

        print("in func")
        print(x.text)
    except Exception as e:
        print('sendtofb:: /api/fb Failed: '+ str(e))

    

# =================================================================================
    # Definition of facebook social media functions
# =================================================================================


# =================================================================================
    # Definition of WhatsApp social media functions
# =================================================================================
@app.route("/api/wa", methods=['GET', 'POST'])
def wachat():
    print(request.values)
    incoming_msg = request.values.get('Body', '')
    incoming_msg_id = request.values.get('AccountSid', '')
    incoming_ph_no_extract = request.values.get('From', '')
    incoming_ph_no_digit = re.findall(r'\d+', incoming_ph_no_extract)
    incoming_ph_no = (''.join(incoming_ph_no_digit)).strip()
    print("====Inside whatsapp chat ===========")
    print(incoming_msg)    
    print(incoming_msg_id)
    print(incoming_ph_no_extract)
    print(incoming_ph_no)
    print((''.join(incoming_ph_no)).strip())

    resp = MessagingResponse()
    msg = resp.message()
    responded = False

    sender_json = {
                    "input": {
                            "text": incoming_msg,
                            "client": "bank",
                            "socket_id": incoming_ph_no
                        }
                    }
    print("sender_json: " + str(sender_json))
    try:
        reply_msg_return = send(sio, sender_json)
        reply_msg = reply_msg_return['response']
    except Exception as e:
        print('train_chatbot:: /api/wa Failed: '+ str(e))
        reply_msg = "Oops! it seems there is some difficulties in the system, please try again later"
    
    print("reply_msg: " + reply_msg)
    msg.body(reply_msg)
    responded=True

    if not responded:
        msg.body('Not sure I understand, Please try again')
    return str(resp)


# =================================================================================
    # Definition of WhatsApp social media functions
# =================================================================================


# =================================================================================
    # Definition of Google Voice social media functions
# =================================================================================
@app.route("/api/googlevoice", methods=['GET', 'POST'])
def googlevoicechat():

    try:
        print("Inside google voice")   
        print("input json: " + str(request.json)) 
        print(request.host_url)
        print("handler: " + request.json["handler"]["name"])
        # handler = request.json["handler"]["name"]
        print("intent-query: " + request.json["intent"]["query"])
        intent_query = request.json["intent"]["query"]
        print("session-id: " + request.json["session"]["id"])
        session_id = request.json["session"]["id"]

        sender_json = {
                        "input": {
                                "text": intent_query,
                                "client": "bank",
                                "socket_id": session_id
                            }
                        }
        
        msg = send(sio, sender_json)
        reply_msg = msg['response']
        if msg['tag']=="goodbye" or msg['tag']=="thanks":
            next_scene = "actions.scene.END_CONVERSATION"
            clear_expired_contexts(session_id)
        else:
            next_scene = ""

        print(next_scene)
        print(reply_msg)
        body = {
                "session": {
                    "id": session_id,
                    "params": {}
                },
                "prompt": {
                    "override": "false",
                    "firstSimple": {
                    "speech": reply_msg,
                    "text": ""
                    }
                },
                "scene": {
                    "name": "SceneName",
                    "slots": {},
                    "next": {
                        "name": next_scene
                    }
                  }
                }

        # json_reply_to_google_voice = requests.post(url, json=body)
        return body

    except Exception as e:
        print('googlevoicechat:: /api/googlevoice Failed: '+ str(e))      


# =================================================================================
    # Definition of Google Voice social media functions
# =================================================================================


# =================================================================================
    # Definition of Alexa Voice functions
# =================================================================================

@app.route("/api/alexa", methods=['GET', 'POST'])
def alexachat():
    print(json.dumps(request.json, indent=2))

    session_id = request.json['session']['sessionId']

    reply_msg = "Please respond"
    endsession = False

    if request.json['request']['type'] == 'LaunchRequest':
        sender_json = {
            "input": {
                "text": "lima chat",
                "client": "bank",
                "socket_id": session_id
            }
        }
        endsession = False
        msg = send(sio, sender_json)
        reply_msg = msg['response']
    else:
        if request.json['request']['type'] == 'IntentRequest':
            try:
                text = request.json['request']['intent']['slots']['sentence']['value']
                print(text)
                sender_json = {
                    "input": {
                        "text": text,
                        "client": "bank",
                        "socket_id": session_id
                    }
                }
                msg = send(sio, sender_json)
                reply_msg = msg['response']
                if msg['tag'] == "goodbye" or msg['tag'] == "thanks":
                    endsession = True
                    clear_expired_contexts(session_id)
                else:
                    endsession = False
            except Exception as e:
                logging.exception(e)
                print('alexachat:: /api/alexa Failed: ' + str(e))
                reply_msg = "Sorry, cannot fulfill your request right now. Try again later."
                endsession = False

    response_body = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reply_msg
            },
            "card": {
                "type": "Simple",
                "title": "Lima Chat",
                "content": reply_msg
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Please give me further information"
                }
            },
            "shouldEndSession": endsession
        }
    }

    return response_body, 200

# =================================================================================
    # Definition of Alexa Voice functions
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
