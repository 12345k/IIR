from typing import Optional,List
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiofiles
import router
import os
import shutil

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/iir", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})



@app.post("/uploadfiles/", response_class=HTMLResponse)
async def create_upload_files(request: Request,file: UploadFile = File(...)):
    dir="./static/temp/"
    file_path=dir+file.filename
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)

    text = router.convert_pdf_img(file_path)
    response= {"request": request,"filename": file.filename,"text":text }
    
    shutil.rmtree(dir)
    return templates.TemplateResponse("index.html",response)

