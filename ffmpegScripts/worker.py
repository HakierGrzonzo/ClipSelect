"""Script that uses ImageMaigick to convert pngs to gifs"""

import mysql.connector
import os, json, time, re
from multiprocessing import Pool, cpu_count

parameters = json.load(open('parameters.json'))
databaseFolder = os.path.expanduser(parameters['databaseFolder'])

process_count = int(cpu_count() // 2)

try:
    os.mkdir(os.path.join(databaseFolder, 'gifs'))
except Exception as e:
    pass

def quote(astr):
    return re.sub("(!|\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;)", r"\\\1", astr).replace(' ', r"\ ")

def processGif(data):
    """Returns relative path to gif for job query"""
    begin_frame, end_frame, series, episode, id = data
    print('processing {} from {}'.format(id, episode))
    pathToImages = os.path.join(databaseFolder, series, episode)
    images = [os.path.join(pathToImages, 'out{:05d}.jpg'.format(x)) for x in range(int(begin_frame + 2), int(end_frame - 2))]
    imageString = str()
    for image in images:
        imageString += quote(image) + ' '
    imageString = imageString.strip()
    db_path = os.path.join('gifs', str(id)+'.gif')
    resultPath = os.path.join(databaseFolder, db_path)
    # make gif
    x = os.system('convert -fuzz 1% -delay 1x10 -loop 0 {0} -layers OptimizeTransparency {1}'.format(imageString, resultPath))
    if x == 0:
        return db_path, id
    else:
        raise Exception('oh shit')

workers = Pool(process_count)

def doWork():
    """fetches work and if available does it"""
    mydb = mysql.connector.connect(
        host = parameters['mysql_host'],
        port = parameters['mysql_host_port'],
        user = "admin",
        passwd = parameters['mysql_password'],
        database = parameters['mysql_database'],
        auth_plugin="mysql_native_password"
    )
    cursor = mydb.cursor()
    sql = """SELECT subs.begin_frame, subs.end_frame, subs.series, subs.episode, subs.id FROM subs
        INNER JOIN jobs ON jobs.gif_id = subs.id WHERE jobs.status = 0
        ORDER BY jobs.job_id LIMIT %s"""
    cursor.execute(sql, (process_count, ))
    work = cursor.fetchall()
    if len(work) > 0:
        print('processing {} queries'.format(len(work)), flush=True)
        sql = 'UPDATE jobs SET status = 1, result_filepath = %s WHERE gif_id = %s'
        paths = workers.map(processGif, work)
        for path in paths:
            cursor.execute(sql, path)
            mydb.commit()
        print('finished')
        cursor.close()
        mydb.close()
    else:
        cursor.close()
        mydb.close()
        time.sleep(2)

try:
    while True:
        try:
            doWork()
        except Exception as e:
            print(e, flush=True)
            print("try to do that again")
            time.sleep(10)

except KeyboardInterrupt:
    pass
