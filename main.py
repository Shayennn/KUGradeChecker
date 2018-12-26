#! /usr/bin/python3

import requests
import captcha_reader as cr
from lxml import html
import random
import time
from getpass import getpass

class GradeChecker:
    logged_in = False
    host = 'https://grade-std.ku.ac.th'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    page_url = {
        'home': '/GSTU_login_.php',
        'login': '/GSTU_login_.php',
        'course': '/GSTU_course_.php',
        'captcha': '/image_capt.php'
    }
    userinfo = {
        'name': '',
        'stdcode': ''
    }

    def __init__(self, sleep=False):
        self.req = requests.Session()
        self.sleep = sleep

    def login(self, username, password):
        self.req.get(self.host+self.page_url['login'], headers = self.headers)
        if self.sleep:
            sleeptime = random.randint(1,50)/100
            time.sleep(sleeptime)
        req = self.req.get(self.host+self.page_url['captcha'], headers = self.headers)
        rsv = cr.Resolver(req.content)
        
        # Uncomment this line to train the simple captcha resolver
        # rsv.__train__()

        captcha = rsv.resolve()
        # print(captcha)
        # rsv.showimg()
        post_data = {
            'UserName': username,
            'Password': password,
            'zone': 0,
            'captcha': captcha
        }
        if self.sleep:
            sleeptime = random.randint(200,500)/100
            time.sleep(sleeptime)
        req = self.req.post(self.host+self.page_url['login'], data = post_data, headers = self.headers)
        page_data = req.text.replace('&nbsp;',' ')
        doc = html.fromstring(req.text)
        if page_data.count('Wrong Code Entered')>0:
            rsv.saveresult()
            return (False, 'Wrong Code Entered')
        bold = doc.findall('.//b')
        FONT = doc.findall('.//font')
        if page_data.count('เข้าสู่ระบบ'):
            if len(bold)>1:
                return (False, bold[1].text_content())
            return (False, 'Something')
        userdata = FONT[1].text_content()
        self.userinfo['name']=userdata[12:]
        self.userinfo['stdcode']=userdata[0:10]
        self.logged_in = True
        return (True,self.userinfo)

    def getGrade(self,year,sem,campus='b'):
        if not self.logged_in:
            return (False, 'Please call login function')
        grade = {}
        post_data = {
            'YearS': year,
            'YearSem': sem,
            'UserName': campus+self.userinfo['stdcode'],
            'Password': '',
            'Campus': '',
            'Requery': 'Y'
        }
        if self.sleep:
            sleeptime = random.randint(200,300)/100
            time.sleep(sleeptime)
        req = self.req.post(self.host+self.page_url['course'], data = post_data, headers = self.headers)
        page_data = req.text.replace('&nbsp;',' ')
        doc = html.fromstring(req.text)
        table = doc.findall('.//table')
        if len(table)<=4:
            return (False, 'No grade')
        for tr in table[-1].findall('.//tr')[1:-3]:
            data = tr.findall('.//td')
            grade[data[1].text_content().strip()] = {
                'name': data[2].text_content().strip(),
                'section': data[3].text_content().strip(),
                'credit': data[5].text_content().strip(),
                'grade': data[4].text_content().strip(),
                'status': data[6].text_content().strip(),
            }
        return (True, grade)



if __name__ == "__main__":
    wantsleep = None
    while wantsleep == None:
        _wantsleep = input('Delay between each request? (y/n) [Y]: ').lower()
        if _wantsleep == 'y' or _wantsleep == '':
            wantsleep = True
        elif _wantsleep == 'n':
            wantsleep = False
    username = input('Username: ')
    password = getpass('Password: ')

    obj = GradeChecker(sleep=wantsleep)
    ret, err = obj.login(username, password)
    if ret:
        ret, data = obj.getGrade(61,1)
        if ret:
            for code, sub_data in data.items():
                if sub_data['grade']=='':
                    continue
                print('['+code+']',sub_data['name'],'Sec:',sub_data['section'],'Credit:',sub_data['credit'])
                print('\tGrade:',sub_data['grade'])
                print('\tGrade:',sub_data['status'])
        else:
            print('GradeERR:',data)
    else:
        print('LoginERR:',err)
