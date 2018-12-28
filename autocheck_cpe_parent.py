#! /usr/bin/python3

import pickle
from getpass import getpass
import requests
from check_by_parent import GradeChecker

if __name__ == "__main__":
    line_url = 'https://notify-api.line.me/api/notify'

    announce_list = [
        '01999011',
        '01420111'
    ]

    try:
        with open('parent_data.pkl','rb') as output:
            old_data = pickle.load(output)
            output.close()
    except FileNotFoundError:
        old_data = {}

    try:
        with open('credential_parent.pkl','rb') as output:
            std_id,parent_id,birthday,line_token,cpe_line_token = pickle.load(output)
            output.close()
    except FileNotFoundError:
        std_id = input('STD ID: ')
        parent_id = input('Parent ID: ')
        birthday = input('Birthday (dd/mm/yyyy ex. 29/07/2542): ')
        line_token = input('LineToken: ')
        cpe_line_token = input('CPE_Token: ')
        with open('credential_parent.pkl',mode='wb') as output:
            pickle.dump((std_id,parent_id,birthday,line_token,cpe_line_token),output)
            output.close()
    line_headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+line_token}
    cpe_line_headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+cpe_line_token}

    obj = GradeChecker()
    ret, err = obj.login(std_id,parent_id,birthday)
    if ret:
        ret, data = obj.getGrade()
        if ret:
            for code, sub_data in data.items():
                if sub_data['grade']=='':
                    continue
                print('['+code+']',sub_data['name'],'Credit:',sub_data['credit'])
                print('\tGrade:',sub_data['grade'])
                if code not in old_data:
                    if code in announce_list:
                        msg=[sub_data['name']+' อัพโหลดเกรดขึ้นระบบแล้ว','']
                        msg+=['สามารถดูได้ที่ https://goo.gl/kUBHfa','หรือผ่านแอพ NisitKU']
                        r = requests.post(line_url, headers=cpe_line_headers , data = {'message':'\n'.join(msg)})
                    msg=['['+code+'] '+sub_data['name']+' Credit: '+sub_data['credit']]
                    msg+=['ได้บันทึกเกรดลงระบบแล้ว']
                    msg+=['Grade: '+sub_data['grade']]
                    r = requests.post(line_url, headers=line_headers , data = {'message':'\n'.join(msg)})
            with open('parent_data.pkl',mode='wb') as output:
                pickle.dump(data,output)
                output.close()
        else:
            print('GradeERR:',data)
    else:
        print('LoginERR:',err)
