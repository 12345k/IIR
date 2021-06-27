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

from NER.server.utils import preprocess_data, predict, idx2tag


BasePath = "static"

# For Model 
from transformers import BertTokenizerFast, BertForTokenClassification
MAX_LEN = 500
NUM_LABELS = 13
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = 'bert-base-uncased'
STATE_DICT = torch.load("NER/Resume Model/model-state.bin_1", map_location=DEVICE)
TOKENIZER = BertTokenizerFast("NER/vocab/vocab.txt", lowercase=True)

model = BertForTokenClassification.from_pretrained(
    'bert-base-uncased', state_dict=STATE_DICT['model_state_dict'], num_labels=NUM_LABELS)
model.to(DEVICE)


class Predict_method(BaseModel):
    URL: str

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
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



if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=6001,reload=True)