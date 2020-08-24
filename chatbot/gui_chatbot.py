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
        intents = json.loads(open(intent_file_name).read())
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
    return sentence_words


# return bag of words array: 0 or 1 for words that exist in sentence
def bag_of_words(sentence, words, show_details=True):
    # tokenizing patterns
    sentence_words = clean_up_sentence(sentence)
    # bag of words - vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,word in enumerate(words):
            if word == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % word)
    return(np.array(bag))

def predict_class(sentence):
    # filter below  threshold predictions
    p = bag_of_words(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sorting strength probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

# It returns the response to the chatbot
def getResponse(ints, intents_json, msg):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            if i['tag']=='cust_id': 
                print('msg is: ' + msg)  
                customerid = re.findall(r'\d+', msg)
                print("customer id: " + str(customerid))  
                response = getbankaccounts(str(customerid))
                if response is None:
                    print('within if')
                    result = "Oops! it seems there is some problem in the system, please try again later"
                elif "validation error" in response:
                    print('within elif')
                    result = response.replace('validation error:', '')
                else:
                    print('within else')
                    result = "Please select the account from the list:" + json.loads(response)["account number"]    
                
                
            elif i['tag']=='bankac_balance': 
                accno = re.findall(r'\d+', msg) 
                print("account number: " + str(accno))                
                response = getbankbalance(str(accno))
                if response is None:
                    result = "Oops! it seems there is some problem in the system, please try again later"
                elif "validation error" in response:
                    print('within elif')
                    result = response.replace('validation error:', '')                
                else:
                    result = "Your account balance is $" + json.loads(response)["balance"]                 
                
            else:                
                result = random.choice(i['responses'])
                break
    return result


def getbankaccounts(customerid):
    bad_chars = ['[', ']', "'", "'"]
    for i in bad_chars : 
        customerid = customerid.replace(i, '')
    print(customerid)
    print(data['ac_api'])
    resp = requests.get(data['ac_api'],
                            headers={'customerid':customerid})
    if resp.status_code != 200:
        # This means something went wrong.
        # raise ApiError('GET /tasks/ {}'.format(resp.status_code))
        print('error happened:' + str(resp.status_code) + ":" + resp.text)
        if "Customer ID is less than 10 digits" in resp.text:
            return "validation error:" + resp.text.replace('Incorrect Header.','') + ", please provide the correct id"
        else:
            return None
        
    # for todo_item in resp.json():
    else:
        # print('Response: ' + json.dumps(resp.json))
        print('response received: ' + resp.text)
        return resp.text
    

def getbankbalance(accno):
    bad_chars = ['[', ']', "'", "'"]
    for i in bad_chars : 
        accno = accno.replace(i, '')
    print(accno)
    resp = requests.get(data['balance_api'],
                            headers={'accno':accno})
    if resp.status_code != 200:
        # This means something went wrong.
        # raise ApiError('GET /tasks/ {}'.format(resp.status_code))
        print('error happened:' + str(resp.status_code) + ":" + resp.text)
        if "Account number is less than 11 digits" in resp.text:
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

def send(msg,client):
    print('msg from send(): ' + msg)
    print('client from send(): ' + client)
    try:
        load_configs(client)
        print('loading config is successful')
    except:
        return 'There is some problem in the getting to the chat assistance; please try later!' 
    
    ints = predict_class(msg)
    result = getResponse(ints, intents, msg)
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
