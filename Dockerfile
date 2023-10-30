FROM python:3.10.6-slim-buster

WORKDIR /usr/share/menu

COPY requirements.txt /usr/share/menu/requirements.txt
RUN pip install -r /usr/share/menu/requirements.txt

COPY menu /usr/share/menu

ENV PYTHONPATH "${PYTHONPATH}:/usr/share/menu/"
