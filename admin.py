from chatbot.train_chatbot import exectraining

# For running the system training
def runtraining():
    result = exectraining()
    return result


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
        
        with open(UPLOAD_DIRECTORY + f_header_filename, "wb") as fp:
            fp.write(request.data)

        return str(True)

    except Exception as e:
        print('admin:: fileupload Failed: '+ str(e))        
        return str(False)
    

    # filenames = f_header.split(",")
    # for filename in filenames:
    #     print(filename)
    
