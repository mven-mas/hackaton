from flask import Flask, render_template, request, send_file
import os
import numpy as np
import cv2
import pathlib
import shutil
from ultralytics import YOLO
import csv
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def create_folders(path):
    folders = ['frame', r'frame/' + path, 'fail', r'fail/' + path, 'noler', r'noler/' + path]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

@app.route('/upload', methods=['POST'])
def upload():
    # Вызываем функцию для создания папок

    video_file = request.files['video']

    video_path = os.path.join('uploads', video_file.filename)
    video_file.save(video_path)

    # Код обработки видео
    a = np.array([])
    b = np.array([])
    model = YOLO('best.pt')
    file_name = video_path
    path = pathlib.Path(file_name)

    vc = cv2.VideoCapture(file_name)
    n = 1

    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False

    timeF = 12

    i = 0
    create_folders(path.name)
    print(path.name)
    while rval:
        rval, frame = vc.read()
        if (n % timeF == 0):
            i += 1
            print(i)
            cv2.imwrite(r'noler/'+path.name+'/{}.jpg'.format(i), frame)
        n = n + 1
        cv2.waitKey(1)
    vc.release()

    source_folder = 'noler'

    # Путь к папке "frame"
    destination_folder = 'frame'

    # Получаем список всех файлов в папке "noler"
    files = os.listdir(source_folder)

    # Переносим каждый файл из папки "noler" в папку "frame"
    for file_name in files:
        # Создаем полные пути к исходному и целевому файлам
        source_file = os.path.join(source_folder, file_name)
        destination_file = os.path.join(destination_folder, file_name)

        # Переносим файл
        shutil.move(source_file, destination_file)

    results = model('/Users/Dmitriy/PycharmProjects/pythonProject2/frame/' + path.name, classes=1, show=False, visualize=False)

    for r in results:
        if not a:
            a = [[r.verbose(), r.path]]
        else:
            a += [[r.verbose(), r.path]]

    for r, q in a:
        if "phone" in r:
            if not b:
                b = [q]
            else:
                b += [q]

    b = [x.split('/Users/Dmitriy/PycharmProjects/pythonProject2/frame/'+path.name)[1] for x in b]
    path_s = r'/Users/Dmitriy/PycharmProjects/pythonProject2/frame/'+path.name
    path_d = r'/Users/Dmitriy/PycharmProjects/pythonProject2/fail/'+path.name
    for file in os.listdir(path_s):
        for s in b:
            if file == s:
                shutil.copyfile(path_s + file, path_d + file)
    seco = np.array([])
    c = [(x[:-4]) for x in b]
    v = int(c[0])
    import time
    sec = v
    ty_res = time.gmtime(sec)
    seco = [time.strftime("%H:%M:%S", ty_res)]
    u = 1
    for s in c:
        if v == int(s):
            v = v + 1
        elif v < v + 10:
            v = int(s)
        else:
            u += 1
            v = int(s)
            sec = v
            ty_res = time.gmtime(sec)
            seco = [time.strftime("%H:%M:%S", ty_res)]
    columns = ['file', 'Time', 'Count']

    data = [
        [path.stem, seco, u],
    ]

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(r'/Users/Dmitriy/PycharmProjects/pythonProject2/f.csv')

if __name__ == '__main__':
    app.run()