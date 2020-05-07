from app import app
from os import path
from flaskext.mysql import MySQL
from flask import render_template, request, abort, jsonify, send_from_directory
import mysql.connector
from urllib.parse import quote

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'proszeniehackowac'
app.config['MYSQL_DATABASE_DB'] = 'debug'
app.config['MYSQL_DATABASE_HOST'] = '192.168.152.113'
app.config['MYSQL_DATABASE_PORT'] = 3308
mysql.init_app(app)

@app.route('/')
@app.route('/index')
def mainpage():
    mydb = mysql.connect()
    cursor = mydb.cursor()
    sql = 'SELECT series FROM subs GROUP BY series ORDER BY series'
    cursor.execute(sql)
    result = cursor.fetchall()
    shows = list()
    for x in result:
        shows.append({'name': x[0], 'url': 'shows/' + quote(x[0], safe='')})
    cursor.close()
    mydb.close()
    return render_template('index.html', shows = shows)

@app.route('/quoteCard/<id>')
def quoteCard(id):
    mydb = mysql.connect()
    cursor = mydb.cursor()
    sql = 'SELECT id, raw_content FROM subs WHERE (episode, series, n) = (SELECT episode, series, n + 1 FROM subs WHERE id = %s)'
    data = (int(id), )
    cursor.execute(sql, data)
    try:
        id2, raw_content2 = cursor.fetchall()[0]
    except IndexError:
        id2, raw_content2 = None, None
    sql = 'SELECT id, raw_content FROM subs WHERE (episode, series, n) = (SELECT episode, series, n - 1 FROM subs WHERE id = %s)'
    cursor.execute(sql, data)
    try:
        id, raw_content = cursor.fetchall()[0]
    except:
        id, raw_content = None, None
    cursor.close()
    mydb.close()
    return jsonify([{'id': id, 'content': raw_content}, {'id': id2, 'content': raw_content2}])


@app.route('/shows/<title>')
def shows(title):
    mydb = mysql.connect()
    cursor = mydb.cursor()
    sql = 'SELECT episode FROM subs WHERE series = %s GROUP BY episode ORDER BY episode'
    cursor.execute(sql, (title,))
    result = cursor.fetchall()
    quotes = None
    if len(result) == 0:
        abort(404)
    if len(list(request.args.items())) > 0:
        if request.args.get('episode') == 'ALL':
            sql = 'SELECT id, episode, raw_content FROM subs WHERE series = %s AND content LIKE %s ORDER BY episode, n'
            data = (title, '%' + request.args.get('quote').lower() + '%')
        else:
            sql = 'SELECT id, episode, raw_content FROM subs WHERE series = %s AND content LIKE %s AND episode = %s ORDER BY episode, n'
            data = (title, '%' + request.args.get('quote').lower() + '%', request.args.get('episode'))
        cursor.execute(sql, data)
        quotes = list([{'id': num, 'episode': episode, 'content': content.replace('\n', '</br>')} for num, episode, content in cursor.fetchall()])
    result = [{'name': x[0], 'url': 'shows/{0}/{1}'.format(quote(title, safe=''), quote(x[0], safe=''))} for x in result]
    cursor.close()
    mydb.close()
    return render_template('shows.html', episodes = result, title=title, quotes = quotes)

@app.route('/gif/<id>')
def gifSite(id):
    mydb = mysql.connect()
    cursor = mydb.cursor()
    sql = 'SELECT result_filepath, status FROM jobs WHERE gif_id = %s'
    cursor.execute(sql, (int(id), ))
    job = cursor.fetchall()
    if len(job) == 0:
        sql = 'INSERT INTO jobs (gif_id, status) VALUES (%s, %s)'
        cursor.execute(sql, (int(id), 0))
        mydb.commit()
        cursor.close()
        mydb.close()
        return render_template('gif.html')
    elif job[0][1] == 1:
        cursor.close()
        mydb.close()
        return send_from_directory('static', path.join('ClipSelectDB', job[0][0]))
    else:
        cursor.close()
        mydb.close()
        return render_template('gif.html')
