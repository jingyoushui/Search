import os
from os.path import join as pjoin
import json
filePath = './static/ocr/'
for i,j,k in os.walk(filePath):
    if i=="./static/ocr/" :
        continue
    else:
        path1 = i
        path2 = path1[12:]
        path3 = path1+path2
        jsonpath =path3+".json"
        jpgpath = path3+".jpg"
        fr = open(pjoin(jsonpath))
        model=json.load(fr)
        fr.close()
        string = {"jpgpath":jpgpath}

        for i in string:
                model[i] = string[i]
        jsObj = json.dumps(model)

        with open(pjoin(jsonpath), "w") as fw:
                fw.write(jsObj)
                fw.close()