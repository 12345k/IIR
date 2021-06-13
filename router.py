	
from wand.image import Image
import os
from PIL import Image as PILIMAGE
import pytesseract

def convert_pdf_img(pdf_file):
    files = []
    with(Image(filename=pdf_file, resolution = 500)) as conn: 
        for index, image in enumerate(conn.sequence):
            image_name = os.path.splitext(pdf_file)[0] + str(index + 1) + '.png'
            Image(image).save(filename = image_name)
            files.append(image_name)
    print(files)
    all_text = [pytesseract.image_to_string(PILIMAGE.open(file)) for file in files]
    print(all_text)

    return " ".join(all_text)