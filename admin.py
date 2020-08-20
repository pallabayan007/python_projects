from chatbot.train_chatbot import exectraining

# For running the system training
def runtraining():
    result = exectraining()
    return result
# For uploading files in project
def fileupload(request):
    print("Inside fileupload==== " + request.content_type)
    print("Inside fileupload headers==== " + request.headers.get('filename',type=str))
    f_header = request.headers.get('filename',type=str)
    filenames = f_header.split(",")
    for filename in filenames:
        print(filename)
    return str(True)
