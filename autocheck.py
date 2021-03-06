#! /usr/bin/python3

import pickle
from getpass import getpass
import requests
from main import GradeChecker

if __name__ == "__main__":
    line_url = 'https://notify-api.line.me/api/notify'

    try:
        with open('data.pkl','rb') as output:
            old_data = pickle.load(output)
            output.close()
    except FileNotFoundError:
        old_data = {}

    try:
        with open('credential.pkl','rb') as output:
            username,password,line_token = pickle.load(output)
            output.close()
    except FileNotFoundError:
        username = input('Username : ')
        password = getpass('Password : ')
        line_token = input('LineToken: ')
        with open('credential.pkl',mode='wb') as output:
            pickle.dump((username,password,line_token),output)
            output.close()
    line_headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+line_token}

    obj = GradeChecker()
    ret, err = obj.login(username, password)
    if ret:
        ret, data = obj.getGrade(61,1)
        if ret:
            for code, sub_data in data.items():
                if sub_data['grade']=='':
                    continue
                print('['+code+']',sub_data['name'],'Sec:',sub_data['section'],'Credit:',sub_data['credit'])
                print('\tGrade:',sub_data['grade'])
                print('\tStatus:',sub_data['status'])
                if (code in old_data and old_data[code]['grade'] == '') or code not in old_data:
                    msg=['['+code+'] '+sub_data['name']+' Sec: '+sub_data['section']+' Credit: '+sub_data['credit']]
                    msg+=['ได้บันทึกเกรดลงระบบแล้ว']
                    msg+=['Grade: '+sub_data['grade']]
                    msg+=['Status: '+sub_data['status']]
                    r = requests.post(line_url, headers=line_headers , data = {'message':'\n'.join(msg)})
                elif code in old_data and old_data[code]['status'] != sub_data['status']:
                    msg=['['+code+'] '+sub_data['name']+' Sec: '+sub_data['section']+' Credit: '+sub_data['credit']]
                    msg+=['ได้เปลี่ยนแปลงสถานะเกรด']
                    msg+=['Grade: '+sub_data['grade']]
                    msg+=['Status: '+old_data[code]['status']+'=>'+sub_data['status']]
                    r = requests.post(line_url, headers=line_headers , data = {'message':'\n'.join(msg)})
            with open('data.pkl',mode='wb') as output:
                pickle.dump(data,output)
                output.close()
        else:
            print('GradeERR:',data)
    else:
        print('LoginERR:',err)
