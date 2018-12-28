import requests
import cv2
import numpy
import time
from os import listdir
from os.path import isfile, join
import tensorflow as tf

class Resolver:
    def __init__(self, imgbyte):
        imgarr = numpy.fromstring(imgbyte, numpy.uint8)
        self.img = cv2.imdecode(imgarr,cv2.IMREAD_COLOR)
        self.model = tf.keras.models.load_model('model.h5')
        self.filterimg()
        
    def __train_from_file__(self):
        number = []
        tag = []
        for num in range(0,10):
            for f in listdir('img/'+str(num)):
                if isfile(join('img/'+str(num), f)):
                    thisimg = cv2.imread('img/'+str(num)+'/'+f)
                    thisimg = cv2.cvtColor(thisimg, cv2.COLOR_RGB2HSV_FULL)
                    bw = cv2.inRange(thisimg,(0,0,200),(0,0,255))
                    bw=bw.reshape(80)/255
                    number.append(bw.copy())
                    tag.append(num)
        number = numpy.array(number)
        tag = numpy.array(tag)
        clf = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation=tf.nn.softmax)
        ])
        clf.compile(optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy'])
        print(number.shape)
        clf.fit(number,tag, epochs=5)
        print('Trained')
        clf.save('model.h5')
        exit()

    def __train__(self):
        number = []
        tag = []
        for _ in range(1000):
            req = requests.get('https://grade-std.ku.ac.th/image_capt.php')
            imgarr = numpy.fromstring(req.content, numpy.uint8)
            self.img = cv2.imdecode(imgarr,cv2.IMREAD_COLOR)
            self.filterimg()
            cv2.imshow('Captcha training',cv2.resize(self.img, (0,0),fx=5,fy=5))
            cv2.imshow('Captcha training2',cv2.resize(self.filtered, (0,0),fx=5,fy=5))
            digtag = list(self.model.predict(self.digit))
            print(digtag)
            while True:
                key = cv2.waitKey(0)
                if len(digtag)==4 and chr(key)==' ':
                    break
                elif len(digtag)==4 and (key >= ord('0') and key <= ord('9')):
                    digtag = []
                if chr(key)=='x':
                    digtag = []
                else:
                    digtag.append(int(chr(key)))
                print(digtag)
            for i in range(4):
                number.append(self.digit[i].copy())
                millis = int(round(time.time() * 1000))
                cv2.imwrite('img/'+int(digtag[i])+'/'+str(millis)+str(i)+'.png',self.digit[i].reshape(10,8)*255)
            tag+=digtag
            print('----------')
        number = numpy.array(number)
        tag = numpy.array(tag)
        clf = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation=tf.nn.softmax)
        ])
        clf.compile(optimizer='adam',
                    loss='sparse_categorical_crossentropy',
                    metrics=['accuracy'])
        print(number.shape)
        clf.fit(number,tag, epochs=5)
        print('Trained')
        clf.save('model.h5')
        exit()

    def resolve(self):
        self.result = self.model.predict_classes(numpy.array(self.digit))
        self.result = [str(x) for x in self.result]
        return ''.join(self.result)

    def showimg(self):
        cv2.imshow('Captcha',cv2.resize(self.img, (0,0),fx=5,fy=5))
        cv2.waitKey(0)

    def saveresult(self):
        millis = int(round(time.time() * 1000))
        cv2.imwrite('error/'+''.join(self.result)+'.png',self.img)

    def filterimg(self):
        self.filtered = cv2.cvtColor(self.img, cv2.COLOR_RGB2HSV_FULL)
        self.filtered = cv2.inRange(self.filtered,(0,0,200),(0,0,255))
        self.digit=[]
        self.digit.append(self.filtered[8:18, 5:13].reshape(80)/255)
        self.digit.append(self.filtered[8:18, 14:22].reshape(80)/255)
        self.digit.append(self.filtered[8:18, 23:31].reshape(80)/255)
        self.digit.append(self.filtered[8:18, 32:40].reshape(80)/255)
