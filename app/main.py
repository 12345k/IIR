from typing import Optional,List
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
BasePath = "static"
app = FastAPI()
print(os.getcwd())
print(os.listdir())
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


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=6001,reload=True)