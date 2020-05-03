from app import app
from flask import render_template, request

@app.route('/')
@app.route('/index')
def mainpage():
    return 'hello world'
