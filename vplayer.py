#!/usr/bin/env python

import os
import json
import random
import subprocess
import os.path
import time
from xml.dom.minidom import parseString

if 'VPLAYER_CONFIG_PATH' not in os.environ:
    print('please set VPLAYER_CONFIG_PATH')
    exit(1)

with open(os.environ['VPLAYER_CONFIG_PATH']) as f:
    config = json.load(f)

UNWATCHED_PATH = config['unwatched_path']
WATCHED_PATH = config['watched_path']
MAX_TIME = config['max_time_sec']
MAX_COUNT = config['max_movies_count']


def play_current():
    if os.path.isfile('playlist.json'):
        with open('playlist.json') as f:
            playlist = json.load(f)
            for file in playlist:
                print(f"running player for {file['path']}")
                subprocess.run(['omxplayer', '-o','hdmi', file['path']])
                time.sleep(1)
                while True:
                    i = subprocess.run(['pgrep', 'omxplayer'], stdout=subprocess.PIPE)
                    if not i.stdout:
                        break
                    time.sleep(1)

                try:
                    os.makedirs(os.path.join(WATCHED_PATH, file['dir']), exist_ok=True)
                    os.rename(file['path'], os.path.join(WATCHED_PATH, file['dir'], file['name']))
                except FileNotFoundError:
                    pass
        return True
    return False



def generate_list():

    fs = []

    for root, directories, _ in os.walk(os.path.join(UNWATCHED_PATH)):

        for directory in directories:
            print(f'checking {directory} as {os.path.join(root, directory)}')
            dir = dict(name=directory, path=os.path.join(root, directory), files=[])

            for droot, _, filenames in os.walk(os.path.join(root, directory)):
                for filename in filenames:
                    file_path = os.path.join(droot, filename)
                    i = subprocess.run(["mediainfo", "--Output=PBCore", file_path], stdout=subprocess.PIPE)
                    try:
                        xml = parseString(i.stdout.decode("utf-8"))
                        d = xml.getElementsByTagName('essenceTrackDuration')
                        dur = int(d[0].firstChild.nodeValue)
                        duration = int(dur/1000)
                        # print(duration)
                    except Exception:
                        print("can't get duration for", file_path)
                        print(i.stdout.decode("utf-8"))
                        continue

                    f = dict(name=filename, path=file_path, dir=directory, duration=int(float(duration)))
                    dir['files'].append(f)
            fs.append(dir)

    def add_movies():
        global total_time

        unused = []

        for i in range(0, len(fs)):
            unused.append(i)

        while True:
            if len(unused) == 0 or len(watch_next) >= MAX_COUNT:
                break

            random_dir_idx = (int(random.random() * len(unused)))  # выбираем случайную папку из доступных
            idx = unused.pop(random_dir_idx)
            dir = fs[idx]  # берём её и убираем из дальнейшего поиска

            while True:
                if len(dir['files']) == 0:  # если кончились файлы — уходим на следующий круг
                    break

                random_file_idx = (int(random.random() * len(dir['files'])))  # случайный индекс

                file = dir['files'].pop(random_file_idx)  # берём файл по индексу

                if len(watch_next) == 0:  # если это будет первый файл в списке, то добавляем любой
                    watch_next.append(file)
                    total_time += file['duration']
                    break  # выходим

                need_time = MAX_TIME - total_time  # сколько времени осталось добрать

                if file['duration'] <= need_time:
                    watch_next.append(file)
                    total_time += file['duration']
                    break

    while True:
        cur_total = total_time
        add_movies()
        if total_time == 0 or cur_total == total_time:
            break

    print('\navailable files:')
    print('='*20)
    for f in fs:
        print(f['name'])
        for file in f['files']:
            print(f'''  [ {str(file['duration']).zfill(3)} sec ] {file['name']} ''')
    print('=' * 20)




watch_next = []  # массив с результатом
total_time = 0  # счётчик набранного времени

if not play_current():
    generate_list()
    play_current()

generate_list()

if not watch_next:
    print('Закончились фильмы')

else:
    watch_next.sort(key=lambda a: a['dir'])

    print('Смотрите далее:')
    for n in watch_next:
        print(f"   {n['dir']} {n['duration']}")

    print(f'total: {total_time} sec')

with open('playlist.json', 'w') as outfile:
    json.dump(watch_next, outfile, ensure_ascii=False, indent=2)
