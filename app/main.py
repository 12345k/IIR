from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiofiles
import router
import os
import shutil
import uvicorn
import random
import string
import torch
from pdfminer.high_level import extract_text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from NER.server.utils import preprocess_data, predict, idx2tag
import pandas as pd
import io

path = "./data/annotation.csv"
if not os.path.isfile(path):
    df=pd.DataFrame(columns=["quote","ranges","text"])
    df.to_csv(path,index=False)



BasePath = "static"

# For Model 
# from transformers import BertTokenizerFast, BertForTokenClassification
# MAX_LEN = 500
# NUM_LABELS = 13
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# MODEL_PATH = 'bert-base-uncased'
# STATE_DICT = torch.load("NER/Resume Model/model-state.bin_1", map_location=DEVICE)
# TOKENIZER = BertTokenizerFast("NER/vocab/vocab.txt", lowercase=True)

# model = BertForTokenClassification.from_pretrained(
#     'bert-base-uncased', state_dict=STATE_DICT['model_state_dict'], num_labels=NUM_LABELS)
# model.to(DEVICE)


class Predict_method(BaseModel):
    URL: str

class AnnotationData(BaseModel):
    quote:str
    ranges: List
    text: str
    
    # {"quote":"gsfdsfgds","ranges":[{"start":"/p[2]","startOffset":0,"end":"/p[2]","endOffset":9}],"text":"dsffsd"}
app = FastAPI()

origins = [
    "http://annotateit.org"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/js", StaticFiles(directory="js"), name="js")

templates = Jinja2Templates(directory="templates")


def generate_random_id():
    """To Generate Random ID
    """
    N = 7
    res = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k = N))
    return res

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.post("/uploadfiles/", response_class=HTMLResponse)
async def create_upload_files(request: Request,file: UploadFile = File(...)):
    path = os.path.join(BasePath,generate_random_id())
    os.mkdir(path)
    file_path=path+"/"+file.filename
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)

    text = router.convert_pdf_img(file_path)
    response= {"request": request,"filename": file.filename,"text":text }
    shutil.rmtree(path)
    return templates.TemplateResponse("index.html",response)

@app.post("/predict")
def predict_Method(req_obj:Predict_method):
    output = extract_text(req_obj.URL)
    resume_text = preprocess_data(output)
    entities = predict(model, TOKENIZER, idx2tag,DEVICE, resume_text, MAX_LEN)
    return{'entities': entities}


@app.post("/store/annotations")
def annotation(req_obj:AnnotationData):
   
    temp = pd.DataFrame(req_obj.__dict__)
    df = pd.read_csv(path)
    df =pd.concat([df,temp])
    # df = df.drop_duplicates()
    df.to_csv(path,index=False)
    return {'request': req_obj}

@app.get("/store/search")
def search():
     return{}

@app.get("/download/annotations")
def download():
    df = pd.read_csv(path)
    
    stream = io.StringIO()

    df.to_csv(stream, index = False)

    response = StreamingResponse(iter([stream.getvalue()]),
                        media_type="text/csv"
    )

    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response


@app.get("/download/ocrtext")
def ocrtext():
    df = pd.read_csv(path)
    
    stream = io.StringIO()

    df.to_csv(stream, index = False)

    response = StreamingResponse(iter([stream.getvalue()]),
                        media_type="text/csv"
    )

    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=6001,reload=True)