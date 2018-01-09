FROM frolvlad/alpine-python3

MAINTAINER Siman Chou <simanchou@foxmail.com>

WORKDIR /opt/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD python statusCheck.py