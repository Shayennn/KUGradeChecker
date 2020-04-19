#! /usr/bin/python3

import datetime
import pickle
from getpass import getpass
import requests
from check_by_nisitku import GradeChecker

if __name__ == "__main__":
    line_url = 'https://notify-api.line.me/api/notify'

    announce_file = open('announce_list.txt', 'r')
    announce_list = [line.replace('\n', '').replace('\r', '')
                     for line in announce_file.readlines()
                     if len(line.replace('\n', '').replace('\r', '')) == 8]
    announce_file.close()

    obj = GradeChecker()

    try:
        with open('nisitku_data.pkl', 'rb') as output:
            old_data = pickle.load(output)
            output.close()
    except FileNotFoundError:
        old_data = {}

    try:
        with open('credential_nisitku.pkl', 'rb') as output:
            obj.id, obj.token, line_token, group_line_token = pickle.load(
                output)
            output.close()
    except FileNotFoundError:
        username = input('Username: ')
        password = getpass('Password: ')
        line_token = input('LineToken: ')
        group_line_token = input('Group_Token: ')
        ret, err = obj.login(username, password)
        if not ret:
            print('LoginERR:', err)
            exit()
        with open('credential_nisitku.pkl', mode='wb') as output:
            pickle.dump((obj.id, obj.token,
                         line_token, group_line_token), output)
            output.close()
    line_headers = {'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Bearer '+line_token}
    group_line_headers = {'content-type': 'application/x-www-form-urlencoded',
                        'Authorization': 'Bearer '+group_line_token}

print('=========================')
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print('=========================')

ret, data = obj.getGrade()
if ret:
    for code, sub_data in data.items():
        if sub_data['grade'] == '':
            continue
        print('['+code+']', sub_data['name'],
              'Credit:', sub_data['credit'])
        print('\tGrade:', sub_data['grade'])
        if code not in old_data and sub_data['grade'] != 'N':
            if code in announce_list:
                msg = [sub_data['name']+' อัพโหลดเกรดขึ้นระบบแล้ว', '']
                msg += ['สามารถดูได้ที่ https://goo.gl/kUBHfa',
                        'หรือผ่านแอพ NisitKU']
                r = requests.post(line_url, headers=group_line_headers, data={
                    'message': '\n'.join(msg)})
            msg = ['['+code+'] '+sub_data['name'] +
                   ' Credit: '+sub_data['credit']]
            msg += ['ได้บันทึกเกรดลงระบบแล้ว']
            msg += ['Grade: '+sub_data['grade']]
            r = requests.post(line_url, headers=line_headers, data={
                'message': '\n'.join(msg)})
    with open('nisitku_data.pkl', mode='wb') as output:
        pickle.dump(data, output)
        output.close()
else:
    print('GradeERR:', data)
