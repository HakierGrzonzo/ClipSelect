from app import app
from os import path
from flaskext.mysql import MySQL
from flask import render_template, request, abort, jsonify, send_from_directory
import mysql.connector
from urllib.parse import quote

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'proszeniehackowac'
app.config['MYSQL_DATABASE_DB'] = 'production'
app.config['MYSQL_DATABASE_HOST'] = '192.168.152.113'
app.config['MYSQL_DATABASE_PORT'] = 3308
mysql.init_app(app)

@app.route('/')
@app.route('/index')
def mainpage():
    """Render main page with list of shows"""
    mydb = mysql.connect()
    cursor = mydb.cursor()
    try:
        sql = 'SELECT series FROM subs GROUP BY series ORDER BY series'
        cursor.execute(sql)
        result = cursor.fetchall()
        shows = list()
        for x in result:
            shows.append({'name': x[0], 'url': 'shows/' + quote(x[0], safe='')})
        return render_template('index.html', shows = shows)
    finally:
        cursor.close()
        mydb.close()

@app.route('/quoteCard/<id>')
def quoteCard(id):
    """Give more context on hover"""
    mydb = mysql.connect()
    cursor = mydb.cursor()
    try:
        #get next subtitle for given id
        sql = 'SELECT id, raw_content FROM subs WHERE (episode, series, n) = (SELECT episode, series, n + 1 FROM subs WHERE id = %s)'
        data = (int(id), )
        cursor.execute(sql, data)
        try:
            id2, raw_content2 = cursor.fetchall()[0]
        except IndexError:
            # If there was none → set it to None
            id2, raw_content2 = None, None
        # Get previous subtitle
        sql = 'SELECT id, raw_content FROM subs WHERE (episode, series, n) = (SELECT episode, series, n - 1 FROM subs WHERE id = %s)'
        cursor.execute(sql, data)
        try:
            id, raw_content = cursor.fetchall()[0]
        except:
            id, raw_content = None, None
        return jsonify([{'id': id, 'content': raw_content}, {'id': id2, 'content': raw_content2}])
    finally:
        cursor.close()
        mydb.close()

@app.route('/shows/<title>')
def shows(title):
    """Display page for quote searching"""
    mydb = mysql.connect()
    cursor = mydb.cursor()
    try:
        # get list of episodes
        sql = 'SELECT episode FROM subs WHERE series = %s GROUP BY episode ORDER BY episode'
        cursor.execute(sql, (title,))
        result = cursor.fetchall()
        quotes = None
        if len(result) == 0:
            abort(404)
        if len(list(request.args.items())) > 0:
            # search for quotes in given episode or in all episodes
            if request.args.get('episode') == 'ALL':
                sql = 'SELECT id, episode, raw_content FROM subs WHERE series = %s AND content LIKE %s ORDER BY episode, n'
                data = (title, '%' + request.args.get('quote').lower() + '%')
            else:
                sql = 'SELECT id, episode, raw_content FROM subs WHERE series = %s AND content LIKE %s AND episode = %s ORDER BY episode, n'
                data = (title, '%' + request.args.get('quote').lower() + '%', request.args.get('episode'))
            cursor.execute(sql, data)
            # format for flask template
            quotes = list([{'id': num, 'episode': episode, 'content': content.replace('\n', '</br>')} for num, episode, content in cursor.fetchall()])
        result = [{'name': x[0], 'url': 'shows/{0}/{1}'.format(quote(title, safe=''), quote(x[0], safe=''))} for x in result]
        return render_template('shows.html', episodes = result, title=title, quotes = quotes)
    finally:
        cursor.close()
        mydb.close()

@app.route('/gif/<id>')
def gifSite(id):
    """Request gif and display it"""
    mydb = mysql.connect()
    cursor = mydb.cursor()
    try:
        # try to find it if already rendered
        sql = 'SELECT result_filepath, status FROM jobs WHERE gif_id = %s'
        cursor.execute(sql, (int(id), ))
        job = cursor.fetchall()
        if len(job) == 0:
            # add to render queue
            sql = 'INSERT INTO jobs (gif_id, status, hits) VALUES (%s, %s, 0)'
            cursor.execute(sql, (int(id), 0))
            mydb.commit()
            sql = 'SELECT count(*) from jobs where status = 0'
            cursor.execute(sql)
            try:
                return render_template('gif.html', jobs = cursor.fetchone()[0])
            except:
                return render_template('gif.html')
        elif job[0][1] == 1:
            # incrament hits if available
            sql = 'UPDATE jobs set hits = 1+ hits where gif_id = %s'
            cursor.execute(sql, (int(id),))
            mydb.commit()
            return send_from_directory('static', path.join('ClipSelectDB', job[0][0]))
        else:
            # display waiting page
            sql = 'SELECT count(*) from jobs where status = 0'
            cursor.execute(sql)
            try:
                return render_template('gif.html', jobs = cursor.fetchone()[0])
            except:
                return render_template('gif.html')
    finally:
        cursor.close()
        mydb.close()

