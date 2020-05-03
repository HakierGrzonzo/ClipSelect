import argparse
from os import system, path, walk, mkdir
from shutil import rmtree
import json, re, time

def quote(astr):
    return re.sub("(!|\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;)", r"\\\1", astr).replace(' ', r"\ ")

def pp(arg):
    print(json.dumps(arg, indent = ' ', separators = ('', ':\t')))

def dir_path(string):
    if path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def checkEqual(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

def strip_common_prefix_suffix(filenames):
    names = [filename.split(' ') for filename in filenames]
    i = 1
    while True:
        if checkEqual([x[:i] for x in names]):
            i += 1
        else:
            i -= 1
            break

    j = -1
    while True:
        if checkEqual([x[j:] for x in names]):
            j -= 1
        else:
            j += 1
            break
    res = dict()
    for x in range(len(names)):
        string = str()
        for y in names[x][i:j]:
            string += y + ' '
        string = string.strip()
        res[filenames[x]] = string
    return res



parser = argparse.ArgumentParser(prog='ffmpegHandler')
parser.add_argument('directory', type=dir_path)
parser.add_argument('--title', type=str)
databaseFolder = path.expanduser('/mnt/hdd/ClipSelectDB')
try:
    dir_path(databaseFolder)
except NotADirectoryError:
    print('Creating database directory')
    mkdir(databaseFolder)

tmpDir = '/tmp/ClipSelect'
try:
    rmtree(tmpDir)
except:
    pass
mkdir(tmpDir)

args = parser.parse_args()
if args.title == None:
    raise Exception("No title given")

out_json = None
for root, directories, files in walk(args.directory):
    # ignore dotfiles
    newFiles = list()
    for fileName in files:
        if fileName[0] != '.':
            newFiles.append(fileName)
    if len(newFiles) == 0:
        raise Exception('No files detected')
    print('Detected {0} files'.format(len(newFiles)))
    out_json = strip_common_prefix_suffix(newFiles)
    break # only handle first level

try:
    databaseFolder = path.join(databaseFolder, args.title)
    dir_path(databaseFolder)
    input('{0} already in database, press enter to delete '.format(args.title))
    rmtree(databaseFolder)
except NotADirectoryError:
    pass
mkdir(databaseFolder)
for k, v in out_json.items():
    sourcePath = path.join(args.directory, k)
    videoPath = path.join(databaseFolder, v)
    subPath = path.join(videoPath, 'sub.srt')
    mkdir(videoPath)
    sub = system('ffmpeg -i {0} {1}'.format(quote(sourcePath), quote(subPath)))
    if sub != 0:
        raise Exception('Subtitle extraction error' )
    tmp = system('cd {0};ffmpeg -i {1} -filter:v "fps=10, scale=1024:576, subtitles={2}" -q:v 3 {3}%05d.jpg'.format(quote(videoPath), quote(sourcePath), 'sub.srt', 'out'))
    if tmp != 0:
        raise Exception('Subtitle burn error')
