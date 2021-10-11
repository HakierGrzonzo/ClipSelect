FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV FLASK_APP /app/__init__.py
#RUN mkdir /app/static/ClipSelectDB

COPY ./app /app

RUN python3 -m pip install -r /app/requirements.txt

ENTRYPOINT python -m flask run -h 0.0.0.0
