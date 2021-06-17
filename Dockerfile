# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
# RUN apt-get install libmagickwand-dev

# COPY ./app/requirements.txt /app/requirements.txt
# RUN pip install -r /app/requirements.txt
# RUN sed -i 's/^.*policy.*coder.*none.*PDF.*//' /etc/ImageMagick-6/policy.xml
# EXPOSE 8000
# EXPOSE 6001

# COPY ./app /app
# WORKDIR /app
# RUN pip install -r requirements.txt

FROM python:3.7-alpine
COPY ./app /app
WORKDIR /app
RUN apk add imagemagick
RUN pip install Wand
RUN export MAGICK_HOME=/usr
RUN ln -s /usr/lib/libMagickCore-7.Q16HDRI.so.6 /usr/lib/libMagickCore-7.Q16HDRI.so
RUN ln -s /usr/lib/libMagickWand-7.Q16HDRI.so.6 /usr/lib/libMagickWand-7.Q16HDRI.so
RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers \
    && pip install Pillow
COPY ./app/requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

# RUN pip install -r /app/requirements.txt

CMD ["python", "main.py"]