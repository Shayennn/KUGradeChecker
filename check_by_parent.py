#! /usr/bin/python3

import requests
from lxml import html
import random
import time
from getpass import getpass

class GradeChecker:
    logged_in = False
    host = 'https://www.regis.ku.ac.th/cpcstk/KUParents'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.regis.ku.ac.th/cpcstk/KUParents/'
    }
    page_url = {
        'check': '/shownisit-parent.php',
    }
    userinfo = {
        'name': '',
        'stdcode': ''
    }

    def __init__(self):
        requests.packages.urllib3.disable_warnings()

    def bueaty_id(self,id):
        if len(id)==13:
            return '-'.join([id[0],id[1:5],id[5:10],id[10:12],id[12]])
        return id

    def login(self, std_id, parent_id, birthday):
        post_data = {
            'Std_id': std_id,
            'Parent_id': self.bueaty_id(parent_id),
            'Std_birthday': birthday,
            'flag': 'START'
        }
        req = requests.post(self.host+self.page_url['check'], data = post_data, headers = self.headers, verify=False)
        page_data = req.text.replace('&nbsp;',' ')
        self.doc = html.fromstring(req.text)
        bold = self.doc.findall('.//b')
        FONT = self.doc.findall('.//font')
        if page_data.count('ติดต่อผู้ดูแลระบบ'):
            return (False, FONT[0].text_content().strip())
        self.userinfo['name'] = FONT[4].text_content().strip()
        self.userinfo['stdcode'] = FONT[2].text_content().strip()
        self.logged_in = True
        return (True,self.userinfo)

    def getGrade(self):
        if not self.logged_in:
            return (False, 'Please call login function')
        grade = {}
        grade_table = self.doc.findall('.//table')[-1]
        tr = grade_table.findall('.//tr')
        for row in tr[-3::-1]:
            if 'Semester' in row.text_content():
                break
            td = row.findall('.//td')
            grade[td[0].text_content().strip()] = {
                'name': td[1].text_content().strip(),
                'section': '?',
                'credit': td[3].text_content().strip(),
                'grade': td[2].text_content().strip(),
                'status': 'Official',
            }
        return (True, grade)



if __name__ == "__main__":
    std_id = input('STD ID: ')
    parent_id = input('Parent ID: ')
    birthday = input('Birthday (dd/mm/yyyy ex. 29/07/2542): ')
    
    obj = GradeChecker()
    ret, err = obj.login(std_id, parent_id, birthday)
    if ret:
        ret, data = obj.getGrade()
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
