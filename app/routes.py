from app import app
from flask import render_template, request, abort, jsonify
import mysql.connector
from urllib.parse import quote
mydb = mysql.connector.connect(
    host="192.168.152.113",
    port="3308",
    user="root",
    passwd="proszeniehackowac",
    database="debug",
    auth_plugin="mysql_native_password"
)

cursor = mydb.cursor()
@app.route('/')
@app.route('/index')
def mainpage():
    sql = 'SELECT series FROM subs GROUP BY series ORDER BY series'
    cursor.execute(sql)
    result = cursor.fetchall()
    shows = list()
    for x in result:
        shows.append({'name': x[0], 'url': 'shows/' + quote(x[0], safe='')})
    return render_template('index.html', shows = shows)

@app.route('/quoteCard/<id>')
def quoteCard(id):
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
    return jsonify([{'id': id, 'content': raw_content}, {'id': id2, 'content': raw_content2}])


@app.route('/shows/<title>')
def shows(title):
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
    return render_template('shows.html', episodes = result, title=title, quotes = quotes)
