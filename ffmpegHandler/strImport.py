from os import path, walk
import mysql.connector, json, re
fps = 10
mydb = mysql.connector.connect(
    host="192.168.152.113",
    port="3308",
    user="root",
    passwd="proszeniehackowac",
    database="debug",
    auth_plugin="mysql_native_password"
)
print('Connected to DB\nClearing table subs')
databaseFolder = path.expanduser('/mnt/hdd/ClipSelectDB')
mycursor = mydb.cursor()
sql = "TRUNCATE TABLE subs"
mycursor.execute(sql)
mydb.commit()
def pp(arg):
    print(json.dumps(arg, indent = '\t', separators=['\t', ':\t']))

def importSrt(f):
    def processText(text):
        cleanr = re.compile('<.*?>')
        text = re.sub(cleanr, '', text)
        cleanr = re.compile('\[.*?\]')
        text = re.sub(cleanr, '', text)
        cleanr = re.compile('[.,!?\\\"]')
        text = re.sub(cleanr, '', text)
        return text.replace('\n', ' ').replace('-', ' ').strip().lower()
    def timecode2frame(timecode):
        data = timecode.strip().split(':')
        try:
            time = float(data[-1])
        except:
            time = float(data[-1].replace(',', '.'))
        time += 60*int(data[-2])
        time += 60*60*int(data[-3])
        return int(time*10)
    data = [x.split('\n', 2) for x in f.split('\n\n')]
    res = []
    for sub in data:
        if len(sub) >= 3:
            text = processText(sub[2])
            if len(text) > 0:
                timecodes = [timecode2frame(x) for x in sub[1].split('-->')]
                entry = (int(sub[0]), timecodes[0], timecodes[1], text)
                res.append(entry)
    return tuple(res)

def importFromRoot(dir, series):
    for r, d, f in walk(dir):
        mycursor = mydb.cursor()
        records = list()
        for dir in d:
            with open(path.join(path.join(path.join(databaseFolder, r), dir), 'sub.srt')) as f:
                [records.append(x) for x in [(series, dir) +  x for x in importSrt(f.read())]]
        print('Adding {0} subtitles from {1}'.format(len(records), series))
        sql = "INSERT INTO subs (series, episode, n, begin_frame, end_frame, content) VALUES (%s, %s, %s, %s, %s, %s)"
        for x in records:
            mycursor.execute(sql, x)
        mydb.commit()
        break


for r, d, f in walk(databaseFolder):
    for dir in d:
        importFromRoot(path.join(databaseFolder, dir), dir)
    break
