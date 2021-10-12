FROM tiangolo/meinheld-gunicorn-flask:python3.9

#ENV MODULE_NAME __init__

COPY ./app/requirements.txt /app/app/requirements.txt

RUN python3 -m pip install -r /app/app/requirements.txt

COPY ./main.py /app/main.py
COPY ./app /app/app
#ENTRYPOINT python -m flask run -h 0.0.0.0
