FROM python:latest

COPY ./requirement.txt /
RUN pip install -r /requirement.txt
WORKDIR /src
ADD . /src

ENTRYPOINT python /src/heimbot.py
