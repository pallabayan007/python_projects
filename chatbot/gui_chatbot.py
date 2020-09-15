import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
from configparser import SafeConfigParser
from pymongo import MongoClient

import json
import random
import re
import logging
import requests
import time
import asyncio

current_context = {}
current_seq = ""
current_tag = ""
tag = ""

# model = load_model('chatbot/chatbot_model.h5')
# intents = json.loads(open('chatbot/intents/intents.json').read())
# words = pickle.load(open('chatbot/words/words.pkl','rb'))
# classes = pickle.load(open('chatbot/classes/classes.pkl','rb'))

# It loads the client configuration from DB/Config files
def load_configs(client):
    # Reading the config file for the client details to train
    print('Inside load_configs: ' + client)

    global parser_chatbot  
    parser_chatbot = SafeConfigParser()

    # =================================================================================
    # Collecting the config data from file
    # parser_chatbot.read('chatbot/server_config/server_' + client + '.ini')
    # global intent_file_name
    # global word_name
    # global class_name
    # global model_name
    # global intents
    # global words
    # global classes
    # global model
    # intent_file_client = parser_chatbot.get('clients', 'client')
    # print('intent_file_client : '+ intent_file_client)
    # intent_file_name = parser_chatbot.get(intent_file_client, 'intents')
    # print('intent_file_name : '+ intent_file_name)
    # word_name = parser_chatbot.get(intent_file_client, 'words')
    # print('word_name : '+ word_name)
    # class_name = parser_chatbot.get(intent_file_client, 'class')
    # print('class_name : '+ class_name)
    # model_name = parser_chatbot.get(intent_file_client, 'model')
    # print('model_name : '+ model_name)
    # =================================================================================

    # =================================================================================
    # Collecting the config data from mongo db
    # global dbconn 
    global intent_file_name
    global word_name
    global class_name
    global model_name
    global intents
    global words
    global classes
    global model  
    global data

    try:
        # parser_chatbot.read('chatbot/config.ini')
        # print(parser_chatbot.get('mongo_db', 'connection'))
        # dbconn = MongoClient(parser_chatbot.get('mongo_db', 'connection'))
        conn = getdbconn()
        print(parser_chatbot.get('mongo_db', 'db'))
        db = conn[parser_chatbot.get('mongo_db', 'db')]
        collection = db[parser_chatbot.get('mongo_db', 'collection')]
        print("collection name: " + collection.name)    
        data = collection.find_one({"client":client})   
        print(data) 
        intent_file_name = data['intents']
        word_name = data['words']
        class_name = data['classes']     
        model_name = data['model']

        print('intent_file_name : '+ intent_file_name)    
        print('word_name : '+ word_name)    
        print('class_name : '+ class_name)
        print('model_name : '+ model_name)
    except Exception as e:
        print(' load_configs Failed: '+ str(e))
    finally:
        conn.close
    
    # =================================================================================
    try:
        intents = json.loads(open(intent_file_name, encoding="UTF").read())
        words = pickle.load(open(word_name,'rb'))
        classes = pickle.load(open(class_name,'rb'))
        model = load_model(model_name)
    except Exception as e:
        print('load_configs var Failed: '+ str(e))

# It returns the connection for the client config parameters
# It reads the db details from config.ini file
def getdbconn():
    print("Inside getdbconn")
    try:
        global parser_chatbot
        parser_chatbot = SafeConfigParser()
        parser_chatbot.read('chatbot/config.ini')
        dbconn = MongoClient(parser_chatbot.get('mongo_db', 'connection'))
    except Exception as e:
        print('getdbconn Failed: '+ str(e))
    
    return dbconn


# def get_db_collection():
#     print("Inside get_db_collection")
#     global dbconn
#     global parser_chatbot  
#     parser_chatbot = SafeConfigParser()
#     parser_chatbot.read('chatbot/config.ini')
#     print(parser_chatbot.get('mongo_db', 'connection'))
#     dbconn = MongoClient(parser_chatbot.get('mongo_db', 'connection'))
#     db = dbconn[parser_chatbot.get('mongo_db', 'db')]
#     collection = db[parser_chatbot.get('mongo_db', 'collection')]
#     print("collection name: " + collection.name)
#     return collection


def clean_up_sentence(sentence):
    # tokenize the pattern - splitting words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stemming every word - reducing to base form
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    # print(sentence_words)
    return sentence_words


# return bag of words array: 0 or 1 for words that exist in sentence
def bag_of_words(sentence, words, show_details=True):
    # tokenizing patterns
    sentence_words = clean_up_sentence(sentence)
    # print(sentence_words)
    # bag of words - vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,word in enumerate(words):
            # print(word)
            # print(s)
            if word == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % word)
    # print(np.array(bag))
    return(np.array(bag))

def predict_class(sentence):
    # filter below  threshold predictions
    # print(sentence)
    # print(words)
    p = bag_of_words(sentence, words, show_details=False)
    # print(p)
    # print(np.array([p]))
    res = model.predict(np.array([p]))[0]
    print("predict_class - res")
    print(res)
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    print("predict_class - results")
    print(results)
    # sorting strength probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    # return_context = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        # return_context.append({"context": classes[r[0]], "probability": str(r[1])})
    print(return_list)
    # print(return_context)
    return return_list

# It implements the context & sequencing
# & returns the response to the chatbot
# def checkcontext(ints, intents_json, json_msg):
#     global current_context
#     global current_seq
#     global current_tag
#     global tag
#     global seq_err_occurred
#     seq_err_occurred = False
#     try:
#         # msg = json_msg["input"]["text"]
#         sockid = json_msg["input"]["socket_id"]
#         event_name = sockid+"_my_message"
#         print("event_name from checkcontext: " + event_name)
#         tag = ints[0]['intent']
#         list_of_intents = intents_json['intents']
#         for j in list_of_intents:
#             if(j['tag']== tag):
#                 print("current_context: " + current_context)
#                 print("current_seq: " + current_seq)
#                 print("current_tag: " + current_tag)
#                 print(j)
#                 print(type(j))
#                 print(j["context"])
#                 print(j["sequence"])
#                 print('j[tag]: ' + j['tag'] + ' :tag: ' + tag)
#                 if current_context != None and current_context.strip() != "" and current_context == (j['context']).strip():
#                     print("Inside current context if: " + current_context)
#                     if current_seq != None and current_seq.strip() != "":
#                         print("Inside current seq if: " + current_seq)
#                         if int(j['sequence']) == (int(current_seq)+1):
#                             print("=====Inside current seq increment if:========== " + current_seq)
#                             # tag = ints[0]['intent']
#                             result = getResponse(ints, intents_json, json_msg)
#                             current_tag = tag
#                             current_context = j['context'].strip()
#                             current_seq = j['sequence'].strip()
#                             break
#                         else:
#                             print("=====Inside current seq increment else:========== " + current_seq)
#                             seq_err_occurred = True
#                             tag = current_tag
#                             # sio.emit(event_name,"Sorry, can't understand your input")
#                             result = getResponse(ints, intents_json, json_msg)
#                             break
#                     else:
#                         print("Inside current seq else: " + current_seq)
#                         tag = ints[0]['intent']
#                         result = getResponse(ints, intents_json, json_msg)
#                         current_tag = tag
#                         current_context = j['context'].strip()
#                         current_seq = j['sequence'].strip()
#                         break
#                 else:
#                     print("Inside current context else: " + current_context)
#                     tag = ints[0]['intent']
#                     result = getResponse(ints, intents_json, json_msg)
#                     current_tag = tag
#                     current_context = j['context'].strip()
#                     current_seq = j['sequence'].strip()
#                     break        
#     except Exception as e:
#         print('gui_chatbot:: checkcontext Failed: '+ str(e))
#         result = "Oops! it seems there is some difficulties faced in the system, please try again later" 
    
#     if seq_err_occurred:
#         # sio.emit(event_name,"Sorry, can't understand your input")
#         # return_socket_msg(event_name,"Sorry, can't understand your input")
#         seq_err_occurred = False
#         return ("Sorry, can't understand your input."+"\\n"+result)
#     else:
#         return result

def return_socket_msg(event_name, msg):
    sio.emit(event_name,msg)

# It returns the response to the chatbot
def getResponse(ints, intents_json, json_msg):    

    try:
        global current_context
        seq_err_occurred = False
        flow_func_err = False
        msg = json_msg["input"]["text"]
        sockid = json_msg["input"]["socket_id"]
        event_name = sockid+"_my_message"
        if not sockid in current_context.keys() :
            current_context[sockid] = ""
        print(current_context)
        print("event_name from getResponse: " + event_name)
        print(ints)
        print(intents_json)
        print('Current context sock id=============')
        print(current_context[sockid])
        if current_context[sockid]!= None and current_context[sockid].strip()!= "" and current_context[sockid]!=ints[0]['intent']:
            print("Inside current_context is not blank")
            if ints[0]['intent'].lower() == "thanks":
                tag = ints[0]['intent']
                seq_err_occurred = False
            else:
                tag = "noanswer"
                seq_err_occurred = True
        # elif current_context!= None and current_context.strip()== "":
        else:
            print("Inside current_context for else")
            tag = ints[0]['intent']
            seq_err_occurred = False
        # tag = ints[0]['intent']
        print("tag: " + tag)
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            # print(current_context[sockid])
            if(i['tag']== tag):
                # if not seq_err_occurred:
                #     current_context[sockid] = i['context'][0]
                # print('current_context after update: =====' + current_context[sockid])
                # print(current_context)
                if i['tag']=='cust_id':
                    # current_context = i['context'][0]
                    print('msg is: ' + msg)
                    customerid_from_msg = re.findall(r'\d+', msg.replace(" ",""))
                    # print(''.join(customerid_from_msg))
                    if (''.join(customerid_from_msg)).strip() == "":
                        print('customerid_from_msg[0] is blank: ')
                        msg_split = re.split('[ ,;:./\-+#]', msg)
                        print(msg_split)
                        print(len(msg_split))
                        customerid = msg_split[len(msg_split)-1]
                    else:
                        customerid = customerid_from_msg[0]
                    print("customer id: " + str(customerid))
                    # if not socketemitmsg(event_name):
                    #     break      
                    # getbankaccounts(event_name,str(customerid))
                    # sio.emit(event_name,"Please wait this may take upto few minutes!!")                 
                    # result = random.choice(i['responses'])
                    # print("result: " + result)                
                    response = getbankaccounts(str(customerid))
                    # loop = asyncio.new_event_loop()
                    # asyncio.set_event_loop(loop)
                    # loop.run_until_complete(getbankaccounts(event_name,str(customerid)))
                    if response is None:
                        print('within if')
                        flow_func_err = True
                        result = "Oops! it seems there is some problem in the system, please try again later"
                    elif "validation error" in response:
                        print('within elif')
                        flow_func_err = True
                        result = response.replace('validation error:', '')
                    else:
                        print('within else')
                        result = "Please select the account from the list:" + json.loads(response)["account number"]    
                    # return result
                    break
                    
                elif i['tag']=='bankac_balance': 
                    # current_context = i['context'][0]
                    accno_from_msg = re.findall(r'\d+', msg.replace(" ",""))
                    if (''.join(accno_from_msg)).strip() == "":
                        print('accno_from_msg[0] is blank: ')
                        msg_split = re.split('[ ,;:./\-+#]', msg)
                        print(msg_split)
                        print(len(msg_split))
                        accno = msg_split[len(msg_split)-1]
                    else:
                        accno = accno_from_msg[0]
                    print("account number: " + str(accno))         
                    # sio.emit(event_name,"Please wait this may take upto few minutes!!")        
                    response = getbankbalance(str(accno))
                    if response is None:
                        flow_func_err = True
                        result = "Oops! it seems there is some problem in the system, please try again later"
                    elif "validation error" in response:
                        print('within elif')
                        flow_func_err = True
                        result = response.replace('validation error:', '')                
                    else:
                        result = "Your account balance is $" + json.loads(response)["balance"]  
                    # return result
                    break               
                    
                else:              
                    # current_context = i['context'][0]
                    result = random.choice(i['responses'])
                    # return result
                    break
    except Exception as e:
        flow_func_err = True
        print('gui_chatbot:: getResponse Failed: '+ str(e))
        result = "Oops! it seems there is some difficulties faced in the system, please try again later"
    
    if not flow_func_err:
        if not seq_err_occurred:
            current_context[sockid] = i['context'][0]
    else:
        flow_func_err = False
    print('current_context after update: =====' + current_context[sockid])
    print(current_context)

    result_json = { 
                    "tag": tag,                  
                    "response": result
                  }
    # return result
    return result_json

# clearing the contexts with expired socket ids
def clear_expired_contexts(sockid):
    print(len(current_context))
    try:        
        if len(current_context)>0:
            print('Inside clear_expired_contexts length > 0: ' + sockid)
            del current_context[sockid]
            return True
        else:
            print('Inside clear_expired_contexts length 0')
            return False      
    except Exception as e:
        print('gui_chatbot:: clear_expired_contexts Failed: '+ str(e))  
        return False

def getbankaccounts(customerid):
    # sock_reply = "Please wait while I fetch the data, it may take upto few minutes!!!"
    # sio.emit(event_name,sock_reply)
    # bad_chars = ['[', ']', "'", "'"]
    # for i in bad_chars : 
    #     customerid = customerid.replace(i, '')
    print(customerid)
    print(data['ac_api'])
    resp = requests.get(data['ac_api'],
                            headers={'customerid':customerid})
    if resp.status_code != 200:
        # This means something went wrong.
        # raise ApiError('GET /tasks/ {}'.format(resp.status_code))
        print('error happened:' + str(resp.status_code) + ":" + resp.text)
        if "Incorrect Header" in resp.text:
            return "validation error:" + resp.text.replace('Incorrect Header.','') + ", please provide the correct id"
            # sock_reply = "Customer ID is less than 10 digits, please provide the correct id"
            # sio.emit(event_name,sock_reply)             
        else:
            # sock_reply = "Oops! it seems there is some problem in the system, please try again later"
            # sio.emit(event_name,sock_reply) 
            return None
        
    # for todo_item in resp.json():
    else:
        # print('Response: ' + json.dumps(resp.json))
        print('response received: ' + resp.text)
        # print('resp["account number"]: ' + json.loads(resp.text)["account number"])
        # sock_reply = "Please select the account from the list:" + json.loads(resp.text)["account number"]
        # sio.emit(event_name,sock_reply)  
        return resp.text
    # time.sleep(5)
    # sio.emit(event_name,sock_reply) 
    

def getbankbalance(accno):
    # bad_chars = ['[', ']', "'", "'"]
    # for i in bad_chars : 
    #     accno = accno.replace(i, '')
    print(accno)
    resp = requests.get(data['balance_api'],
                            headers={'accno':accno})
    if resp.status_code != 200:
        # This means something went wrong.
        # raise ApiError('GET /tasks/ {}'.format(resp.status_code))
        print('error happened:' + str(resp.status_code) + ":" + resp.text)
        if "Incorrect Header" in resp.text:
            return "validation error:" + resp.text.replace('Incorrect Header.','') + ", please provide the correct id"
        else:
            return None      
    # for todo_item in resp.json():
    else:
        # print('Response: ' + json.dumps(resp.json))
        print('response received: ' + resp.text)
    # for todo_item in resp.text:
    #     print(todo_item)
        # print('{} {}'.format(todo_item['id'], todo_item['summary']))
        return resp.text

def send(socket,json_data):
    global sio
    sio = socket
    print('msg from send(): ' + json_data["input"]["text"])
    print('client from send(): ' + json_data["input"]["client"])
    try:
        load_configs(json_data["input"]["client"])
        print('loading config is successful')
    except:
        return 'There is some problem in the getting to the chat assistance; please try later!' 
    
    ints = predict_class(json_data["input"]["text"])
    result = getResponse(ints, intents, json_data)
    return result

# #Creating tkinter GUI
# import tkinter
# from tkinter import *

# def send():
#     msg = EntryBox.get("1.0",'end-1c').strip()
#     EntryBox.delete("0.0",END)

#     if msg != '':
#         ChatBox.config(state=NORMAL)
#         ChatBox.insert(END, "You: " + msg + '\n\n')
#         ChatBox.config(foreground="#446665", font=("Verdana", 12 ))
    
#         ints = predict_class(msg)
#         # if ints=='cust_id' or 'bankac_balance':
#         #     ChatBox.insert(END, "Bot: " + "Please wait while I fetch the data" + '\n\n')
        
#         res = getResponse(ints, intents, msg)
        
#         ChatBox.insert(END, "Bot: " + res + '\n\n')
            
#         ChatBox.config(state=DISABLED)
#         ChatBox.yview(END)
 

# root = Tk()
# root.title("Chatbot")
# root.geometry("400x500")
# root.resizable(width=FALSE, height=FALSE)

# #Create Chat window
# ChatBox = Text(root, bd=0, bg="white", height="8", width="50", font="Arial",)

# ChatBox.config(state=DISABLED)

# #Bind scrollbar to Chat window
# scrollbar = Scrollbar(root, command=ChatBox.yview, cursor="heart")
# ChatBox['yscrollcommand'] = scrollbar.set

# #Create Button to send message
# SendButton = Button(root, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
#                     bd=0, bg="#f9a602", activebackground="#3c9d9b",fg='#000000',
#                     command= send )

# #Create the box to enter message
# EntryBox = Text(root, bd=0, bg="white",width="29", height="5", font="Arial")
# #EntryBox.bind("<Return>", send)


# #Place all components on the screen
# scrollbar.place(x=376,y=6, height=386)
# ChatBox.place(x=6,y=6, height=386, width=370)
# EntryBox.place(x=128, y=401, height=90, width=265)
# SendButton.place(x=6, y=401, height=90)

# root.mainloop()
