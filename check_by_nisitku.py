#! /usr/bin/python3

import requests
from getpass import getpass
import json


class GradeChecker:
    logged_in = False
    host = 'https://kuappstore.ku.ac.th/nisitku/nisit/Controller.php'
    userinfo = {
        'name': '',
        'stdcode': ''
    }
    token = ''

    def __init__(self):
        requests.packages.urllib3.disable_warnings()

    def login(self, username, password):
        post_data = {
            "action": "login",
            "id": username,
            "pass": password
        }
        req = requests.post(
            self.host, data=json.dumps(post_data), verify=False)
        res = req.json()[0]
        if res['status'] == 'false':
            return (False, res['err_desc'])
        self.userinfo['name'] = res['name_th']
        self.userinfo['stdcode'] = res['surname_th']
        self.token = res['token']
        self.id = res['id']
        return (True, self.userinfo)

    def sortCond(sem):
        return int(sem['year']+sem['semester'])

    def getGrade(self):
        if self.token == '':
            return (False, 'Please call login function')
        grade = {}
        post_data = {
            "action": "grade",
            "id": self.id,
            "token": self.token
        }
        req = requests.post(
            self.host, data=json.dumps(post_data), verify=False)
        res = req.json()[0]
        if res['status'] == 'false':
            return (False, res['err_desc'])
        last_sem_courses = sorted(res['grade'], key=GradeChecker.sortCond, reverse=True)[0]['courses']
        for course in last_sem_courses:
            grade[course['course_id']] = {
                'name': course['course_name'],
                'section': '?',
                'credit': course['credit'],
                'grade': course['grade'],
                'status': 'Official',
            }
        return (True, grade)


if __name__ == "__main__":
    username = input('Username: ')
    password = getpass('Password: ')

    obj = GradeChecker()
    ret, err = obj.login(username, password)
    if ret:
        ret, data = obj.getGrade()
        if ret:
            for code, sub_data in data.items():
                if sub_data['grade'] == '':
                    continue
                print('['+code+']', sub_data['name'], 'Sec:',
                      sub_data['section'], 'Credit:', sub_data['credit'])
                print('\tGrade:', sub_data['grade'])
                print('\tGrade:', sub_data['status'])
        else:
            print('GradeERR:', data)
    else:
        print('LoginERR:', err)
