from chatbot.train_chatbot import exectraining, setclientfortraining
from configparser import SafeConfigParser
import json

# For running the system training
def runtraining():
    result = exectraining()
    return result


# For getting the client names from the training.ini
def gettrainingclients():
    parser = SafeConfigParser()
    parser.read('chatbot/training.ini')
    print(parser._sections)
    sections = parser._sections
    client_dict = {}
    i=0
    for x in sections:
        if x != 'chat_trainer':
            client_dict["client"+str(i)]=x
            i=i+1
    i=0
    result = json.dumps(client_dict)
    print(result)
    return result

# For setting the client name for training
def settingclientfortraining(clientname):
    if setclientfortraining(clientname):
        print("====Inside settingclientfortraining====")        
        return True
    else:
        return False

# For uploading files in project
def fileupload(request):

    try:
        UPLOAD_DIRECTORY = ""
        print("Inside fileupload==== " + request.content_type)
        print("Inside fileupload headers==== " + request.headers.get('filename',type=str))
        print("Inside fileupload headers==== " + request.headers.get('filetype',type=str))
        f_header_filename = request.headers.get('filename',type=str)
        f_header_filetype = request.headers.get('filetype',type=str)

        print("Current file path======" + __file__.replace('admin.py',''))
        f_current_folder = __file__.replace('admin.py','')
        if f_header_filetype.lower().find('intents')>=0:
            UPLOAD_DIRECTORY = 'chatbot/intents/'        
        elif f_header_filetype.lower().find('config')>=0:
            UPLOAD_DIRECTORY = f_current_folder.replace('\\','/') + '/' 
        elif f_header_filetype.lower().find('training')>=0:
            UPLOAD_DIRECTORY = f_current_folder.replace('\\','/') + '/'  
        print("File content to be written =========")
        print(request.data)
        with open(UPLOAD_DIRECTORY + f_header_filename, "wb") as fp:
            fp.write(request.data)

        return str(True)

    except Exception as e:
        print('admin:: fileupload Failed: '+ str(e))        
        return str(False)
    

    # filenames = f_header.split(",")
    # for filename in filenames:
    #     print(filename)
    
