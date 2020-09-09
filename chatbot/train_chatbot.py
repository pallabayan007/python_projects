import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
from configparser import SafeConfigParser
import random

import nltk
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import json
import pickle

# Reading the config file for the client details to train
# global parser
# parser = SafeConfigParser()
# parser.read('training.ini')

# words=[]
# classes = []
# documents = []
# ignore_letters = ['!', '?', ',', '.']

# # Reading the values for the client details to train
# intent_file_client = parser.get('chat_trainer', 'client')
# intent_file_name = parser.get(intent_file_client, 'intents')
# # intents_file = open('intents.json').read()
# intents_file = open(intent_file_name).read()
# intents = json.loads(intents_file)

# for intent in intents['intents']:
#     for pattern in intent['patterns']:
#         #tokenize each word
#         word = nltk.word_tokenize(pattern)
#         words.extend(word)
#         #add documents in the corpus
#         documents.append((word, intent['tag']))
#         # add to our classes list
#         if intent['tag'] not in classes:
#             classes.append(intent['tag'])
# print(documents)
# # lemmaztize and lower each word and remove duplicates
# words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
# words = sorted(list(set(words)))
# # sort classes
# classes = sorted(list(set(classes)))
# # documents = combination between patterns and intents
# print (len(documents), "documents")
# # classes = intents
# print (len(classes), "classes", classes)
# # words = all words, vocabulary
# print (len(words), "unique lemmatized words", words)

# # Details of class & word files from the config file
# word_name = parser.get(intent_file_client, 'words')
# class_name = parser.get(intent_file_client, 'class')
# pickle.dump(words,open(word_name,'wb'))
# pickle.dump(classes,open(class_name,'wb'))

# # create our training data
# training = []
# # create an empty array for our output
# output_empty = [0] * len(classes)
# # training set, bag of words for each sentence
# for doc in documents:
#     # initialize our bag of words
#     bag = []
#     # list of tokenized words for the pattern
#     pattern_words = doc[0]
#     # lemmatize each word - create base word, in attempt to represent related words
#     pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
#     # create our bag of words array with 1, if word match found in current pattern
#     for word in words:
#         bag.append(1) if word in pattern_words else bag.append(0)
        
#     # output is a '0' for each tag and '1' for current tag (for each pattern)
#     output_row = list(output_empty)
#     output_row[classes.index(doc[1])] = 1
    
#     training.append([bag, output_row])
# # shuffle our features and turn into np.array
# random.shuffle(training)
# training = np.array(training)
# # create train and test lists. X - patterns, Y - intents
# train_x = list(training[:,0])
# train_y = list(training[:,1])
# print("Training data created")

# # Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
# # equal to number of intents to predict output intent with softmax
# model = Sequential()
# model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
# model.add(Dropout(0.5))
# model.add(Dense(64, activation='relu'))
# model.add(Dropout(0.5))
# model.add(Dense(len(train_y[0]), activation='softmax'))

# # Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
# sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
# model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# #fitting and saving the model 
# hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

# # Details of model file from the config file
# model_name = parser.get(intent_file_client, 'model')
# model.save(model_name, hist)

# print("model created")

# Set the client name in the chat_trainer section of training.ini
def setclientfortraining(clientname):
    print('====Inside exectraining====')
    try:
        parser_setclient = SafeConfigParser()
        parser_setclient.read('chatbot/training.ini')
        if parser_setclient.has_option('chat_trainer','client'):
            if clientname.strip()=="":
                print("=====Inside setclientfortraining blank client name==== " + clientname)
                return False
            else:                
                print("=====Inside setclientfortraining==== " + clientname)               
                parser_setclient.set('chat_trainer','client',clientname)
                with open('chatbot/training.ini', 'w') as configfile:
                    parser_setclient.write(configfile)
                
                print(parser_setclient.get('chat_trainer','client'))
                return True
        else:
            return False
    except Exception as e:
        print('train_chatbot:: setclientfortraining Failed: '+ str(e))
        return False
    finally:
        parser_setclient.clear

def exectraining():
    try:
        print('====Inside exectraining====')
        global parser
        parser = SafeConfigParser()
        parser.read('chatbot/training.ini')
        print('====before word categorization====')
        words=[]
        classes = []
        documents = []
        ignore_letters = ['!', '?', ',', '.']
        print('==== before reading values from files====')
        # Reading the values for the client details to train
        intent_file_client = parser.get('chat_trainer', 'client')
        intent_file_name = parser.get(intent_file_client, 'intents')
        # intents_file = open('intents.json').read()
        intents_file = open(intent_file_name, encoding="UTF").read()        
        print("====before loading the intent file=====")
        intents = json.loads(intents_file)
        print("====after loading the intent file=====")

        for intent in intents['intents']:
            for pattern in intent['patterns']:
                #tokenize each word
                word = nltk.word_tokenize(pattern)
                words.extend(word)
                #add documents in the corpus
                documents.append((word, intent['tag']))
                # add to our classes list
                if intent['tag'] not in classes:
                    classes.append(intent['tag'])
        print(documents)
        # lemmaztize and lower each word and remove duplicates
        words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
        words = sorted(list(set(words)))
        # sort classes
        classes = sorted(list(set(classes)))
        # documents = combination between patterns and intents
        print (len(documents), "documents")
        # classes = intents
        print (len(classes), "classes", classes)
        # words = all words, vocabulary
        print (len(words), "unique lemmatized words", words)

        # Details of class & word files from the config file
        word_name = parser.get(intent_file_client, 'words')
        class_name = parser.get(intent_file_client, 'class')
        pickle.dump(words,open(word_name,'wb'))
        pickle.dump(classes,open(class_name,'wb'))

        # create our training data
        training = []
        # create an empty array for our output
        output_empty = [0] * len(classes)
        # training set, bag of words for each sentence
        for doc in documents:
            # initialize our bag of words
            bag = []
            # list of tokenized words for the pattern
            pattern_words = doc[0]
            # lemmatize each word - create base word, in attempt to represent related words
            pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
            # create our bag of words array with 1, if word match found in current pattern
            for word in words:
                bag.append(1) if word in pattern_words else bag.append(0)
                
            # output is a '0' for each tag and '1' for current tag (for each pattern)
            output_row = list(output_empty)
            output_row[classes.index(doc[1])] = 1
            
            training.append([bag, output_row])
        # shuffle our features and turn into np.array
        random.shuffle(training)
        training = np.array(training)
        # create train and test lists. X - patterns, Y - intents
        train_x = list(training[:,0])
        train_y = list(training[:,1])
        print("Training data created")

        # Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
        # equal to number of intents to predict output intent with softmax
        model = Sequential()
        model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(len(train_y[0]), activation='softmax'))

        # Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

        #fitting and saving the model 
        hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

        # Details of model file from the config file
        model_name = parser.get(intent_file_client, 'model')
        model.save(model_name, hist)

        print("model created")

        return str(True)
    except Exception as e:
        print('train_chatbot:: exectraining Failed: '+ str(e))
        return str(False)
    finally:
        parser.clear