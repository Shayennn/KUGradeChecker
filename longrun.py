#! /usr/bin/python3

import datetime
import time
import pickle
from getpass import getpass
import requests
from check_by_parent import GradeChecker

if __name__ == "__main__":
    line_url = 'https://notify-api.line.me/api/notify'

    announce_list = [
        '01204111',
        '01420113',
        '01417167',
        '01420111',
        '01999021',
        '01999111',
        '01420112'
    ]

    try:
        with open('credential_nisitku.pkl', 'rb') as output:
            username, password, line_token, cpe_line_token = pickle.load(
                output)
            output.close()
    except FileNotFoundError:
        username = input('Username: ')
        password = getpass('Password: ')
        line_token = input('LineToken: ')
        cpe_line_token = input('CPE_Token: ')
        with open('credential_nisitku.pkl', mode='wb') as output:
            pickle.dump((username, password, line_token,
                         cpe_line_token), output)
            output.close()
    line_headers = {'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Bearer '+line_token}
    cpe_line_headers = {'content-type': 'application/x-www-form-urlencoded',
                        'Authorization': 'Bearer '+cpe_line_token}

    obj = GradeChecker()
    while True:
        try:
            with open('parent_data.pkl', 'rb') as output:
                old_data = pickle.load(output)
                output.close()
        except FileNotFoundError:
            old_data = {}
        print('=========================')
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print('=========================')
        ret, err = obj.login(username, password)
        if ret:
            ret, data = obj.getGrade()
            if ret:
                for code, sub_data in data.items():
                    if sub_data['grade'] == '':
                        continue
                    print('['+code+']', sub_data['name'], 'Credit:', sub_data['credit'])
                    print('\tGrade:', sub_data['grade'])
                    print('\tStatus:', sub_data['status'])
                    if (code in old_data and old_data[code]['grade'] == '') or code not in old_data:
                        if code in announce_list:
                            msg = [sub_data['name']+' อัพโหลดเกรดขึ้นระบบแล้ว', '']
                            msg += ['สามารถดูได้ที่ https://goo.gl/kUBHfa',
                                    'หรือผ่านแอพ NisitKU']
                            r = requests.post(line_url, headers=cpe_line_headers, data={
                                              'message': '\n'.join(msg)})
                        msg = ['['+code+'] '+sub_data['name']+' Credit: '+sub_data['credit']]
                        msg += ['ได้บันทึกเกรดลงระบบแล้ว']
                        msg += ['Grade: '+sub_data['grade']]
                        msg += ['Status: '+sub_data['status']]
                        r = requests.post(line_url, headers=line_headers, data={
                                          'message': '\n'.join(msg)})
                    elif code in old_data and old_data[code]['status'] != sub_data['status']:
                        msg = ['['+code+'] '+sub_data['name']+' Credit: '+sub_data['credit']]
                        msg += ['ได้เปลี่ยนแปลงสถานะเกรด']
                        msg += ['Grade: '+sub_data['grade']]
                        msg += ['Status: '+old_data[code]
                                ['status']+'=>'+sub_data['status']]
                        r = requests.post(line_url, headers=line_headers, data={
                                          'message': '\n'.join(msg)})
                with open('parent_data.pkl', mode='wb') as output:
                    pickle.dump(data, output)
                    output.close()
            else:
                print('GradeERR:', data)
        else:
            print('LoginERR:', err)
        time.sleep(5)
