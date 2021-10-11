FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app/

RUN python3 -m pip install -r /app/requirements.txt

ENV FLASK_APP /app/__init__.py
ENTRYPOINT python -m flask run -h 0.0.0.0
