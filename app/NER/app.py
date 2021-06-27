import io
from zipfile import ZipFile
import argparse
import torch
import os
import pandas as pd   
from transformers import BertTokenizerFast, BertForTokenClassification
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from server.utils import preprocess_data, predict, idx2tag
import json

app = Flask(__name__, static_url_path ="/static")
app.config['JSON_SORT_KEYS'] = False
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
static_url="https://ed8470694768.ngrok.io/"

MAX_LEN = 500
NUM_LABELS = 13
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = 'bert-base-uncased'
STATE_DICT = torch.load("model-state.bin_1", map_location=DEVICE)
TOKENIZER = BertTokenizerFast("./vocab/vocab.txt", lowercase=True)

model = BertForTokenClassification.from_pretrained(
    'bert-base-uncased', state_dict=STATE_DICT['model_state_dict'], num_labels=NUM_LABELS)
model.to(DEVICE)

@app.route('/file/<string:path>', methods=['GET'])
def get_file(path=''):
    return send_file(path)

@app.route('/api/predict', methods=['POST'])
def predict_api():
    if request.method == 'POST':
        data = io.BytesIO(request.files.get('resume').read())
        resume_text = preprocess_data(data)
        entities = predict(model, TOKENIZER, idx2tag,
                           DEVICE, resume_text, MAX_LEN)
        return jsonify({'entities': entities})

@app.route('/api/test', methods=['POST'])
def test_api():
        pdfList = []
        docList = []
        with ZipFile(request.files.get('resume'), 'r') as zip: 
            zip.extractall('static') 
            for info in zip.infolist():
                print(info.filename)
                li = list((info.filename).split(".")) 
                if(li[1] == 'pdf'):
                    pdfList.append(info.filename)
                else:
                    docList.append(info.filename)
            print(pdfList) 
            print(docList)

        final_list = []
        full_obj = {}
        with ZipFile(request.files.get('resume'), 'r') as zip: 
            for pdfFile in pdfList:
                my_data = zip.read(pdfFile)
                data = io.BytesIO(zip.read(pdfFile))
                resume_text = preprocess_data(data)
                entities = predict(model, TOKENIZER, idx2tag, DEVICE, resume_text, MAX_LEN)
                newObj = {}
                for data in entities:
                    keyName = (data['entity']).replace(" ", "_")
                    if keyName in newObj:
                        keyValue = (data['text']).replace(",", " ")
                        keyValue = (keyValue).strip()
                        if(keyValue != ""):
                            newObj[keyName] = newObj[keyName]+', '+keyValue
                    else:
                        newObj[keyName] = data['text']
                newObj['Pdf_url'] = request.url_root+'api/uploads/'+pdfFile
                #newObj['Pdf_url'] = static_url+'api/uploads/'+pdfFile
                full_obj[pdfFile.strip()] = newObj
                final_list.append(newObj)
        df = pd.DataFrame(final_list)
        excel_fileName = 'output-excel.csv'
        path = app.root_path+'/static/'+excel_fileName
        df.to_csv(path)
        # path = app.root_path+'/static/'
        # return send_from_directory(directory=path, filename=excel_fileName)
        new_path = request.url_root+'api/uploads/'+excel_fileName
        #new_path = static_url+'api/uploads/'+excel_fileName
        final_response = [{"excel_path": new_path,"json_data":final_list,"newObj":full_obj}]
        return jsonify(final_response)

@app.route('/api/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    path = app.root_path+'/static/'
    return send_from_directory(directory=path, filename=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
