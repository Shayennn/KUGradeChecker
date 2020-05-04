#! /usr/bin/python3

import requests
from getpass import getpass
import json


class GradeChecker:
    userinfo = {
        'name': None,
        'stdcode': None
    }

    def __init__(self):
        try:
            with open('api_url.txt', 'r') as output:
                self.api = output.read().replace('\n', '')
                output.close()
        except FileNotFoundError:
            self.api = input('API: ')
            with open('api_url.txt', mode='w') as output:
                output.write(self.api)
                output.close()
        requests.packages.urllib3.disable_warnings()

    def login(self, username, password):
        return (True, self.userinfo)

    def getGrade(self):
        res = requests.get(self.api)
        if not res.ok:
            return (False, [])
        data = res.json()
        if not data['status']:
            return (False, data['error_msg'])
        grade = {}
        for course in data['data']:
            if course['grade'] is None:
                course['grade'] = ''
            if course['status'] == 0:
                course['status'] = 'ทางการ'
            else:
                course['status'] = 'ไม่เป็นทางการ'
            grade[course['code']] = {
                'name': course['name'],
                'section': str(course['section']),
                'credit': '0',
                'grade': course['grade'],
                'status': course['status'],
            }
        return (True, grade)


if __name__ == "__main__":
    obj = GradeChecker()
    ret, data = obj.getGrade()
    if ret:
        for code, sub_data in data.items():
            if sub_data['grade'] == '':
                continue
            print('['+code+']', sub_data['name'], 'Sec:',
                  sub_data['section'], 'Credit:', sub_data['credit'])
            print('\tGrade:', sub_data['grade'])
            print('\tStatus:', sub_data['status'])
    else:
        print('GradeERR:', data)
