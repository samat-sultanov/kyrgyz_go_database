import xmltodict

def handle_uploaded_file(thisFile):
    with open('uploads/files/' + str(thisFile).replace(' ', '_').replace(',','').replace('(','').replace(')','')) as fd:
        doc = xmltodict.parse(fd.read())
    my_dict = doc['Tournament']
    #Здесь начинается парсинг