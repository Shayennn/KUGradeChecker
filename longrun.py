#! /usr/bin/python3

import datetime
import time
import pickle
from getpass import getpass
import requests
from check_by_nisitku import GradeChecker
import twitter
import sys


if __name__ == "__main__":
    line_url = 'https://notify-api.line.me/api/notify'

    announce_file = open('announce_list.txt', 'r')
    announce_list = [line.replace('\n', '').replace('\r', '')
                     for line in announce_file.readlines()
                     if len(line.replace('\n', '').replace('\r', '')) == 8]
    announce_file.close()

    obj = GradeChecker()

    try:
        with open('credential_twitter.pkl', 'rb') as output:
            twitter_credential = pickle.load(output)
            consumer_key = twitter_credential[0]
            consumer_secret = twitter_credential[1]
            access_token_key = twitter_credential[2]
            access_token_secret = twitter_credential[3]
            output.close()
            useTwitter = True
            print("Using TwitterAPI", file=sys.stderr)
    except FileNotFoundError:
        useTwitter = False

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
            pickle.dump((obj.id, obj.token, line_token,
                         group_line_token), output)
            output.close()

    if useTwitter:
        api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token_key,
                          access_token_secret=access_token_secret)

    line_headers = {'content-type': 'application/x-www-form-urlencoded',
                    'Authorization': 'Bearer '+line_token}
    group_line_headers = {'content-type': 'application/x-www-form-urlencoded',
                          'Authorization': 'Bearer '+group_line_token}
    while True:
        try:
            with open('nisitku_data.pkl', 'rb') as output:
                old_data = pickle.load(output)
                output.close()
        except FileNotFoundError:
            old_data = {}
        print('=========================')
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print('=========================')
        ret, data = obj.getGrade()
        if ret:
            for code, sub_data in data.items():
                print('['+code+']', sub_data['name'],
                      'Credit:', sub_data['credit'])
                print('\tGrade:', sub_data['grade'])
                if sub_data['grade'] == 'N':
                    continue
                if (code not in old_data or old_data[code]['grade'] == 'N') and sub_data['grade'] != 'N':
                    print('\t', end='')
                    if code in announce_list:
                        msg = [sub_data['name']+' อัพโหลดเกรดขึ้นระบบแล้ว', '']
                        if useTwitter:
                            print(api.PostUpdate('BOT: '+msg[0]).text)
                        msg += ['สามารถดูได้ที่ https://goo.gl/kUBHfa',
                                'หรือผ่านแอพ NisitKU']
                        r = requests.post(line_url, headers=group_line_headers,
                                          data={
                                              'message': '\n'.join(msg)
                                          })
                        print("Announced & ", end='')
                    msg = ['['+code+'] '+sub_data['name'] +
                           ' Credit: '+sub_data['credit']]
                    msg += ['ได้บันทึกเกรดลงระบบแล้ว']
                    msg += ['Grade: '+sub_data['grade']]
                    r = requests.post(line_url, headers=line_headers,
                                      data={
                                          'message': '\n'.join(msg)
                                      })
                    print("Notified")
                elif code in old_data and old_data[code]['grade'] != sub_data['grade']:
                    print('\t', end='')
                    if code in announce_list:
                        msg = [sub_data['name']+' แก้ไขเกรดในระบบแล้ว', '']
                        if useTwitter:
                            print(api.PostUpdate('BOT: '+msg[0]).text)
                        msg += ['สามารถดูได้ที่ https://goo.gl/kUBHfa',
                                'หรือผ่านแอพ NisitKU']
                        r = requests.post(line_url, headers=group_line_headers,
                                          data={
                                              'message': '\n'.join(msg)
                                          })
                        print("Announced & ", end='')
                    msg = ['['+code+'] '+sub_data['name'] +
                           ' Credit: '+sub_data['credit']]
                    msg += ['ได้แก้ไขเกรดในระบบแล้ว']
                    msg += ['From: '+old_data[code]['grade']]
                    msg += ['Grade: '+sub_data['grade']]
                    r = requests.post(line_url, headers=line_headers,
                                      data={
                                          'message': '\n'.join(msg)
                                      })
                    print("Notified")
            with open('nisitku_data.pkl', mode='wb') as output:
                pickle.dump(data, output)
                output.close()
        else:
            print('GradeERR:', data)
        time.sleep(5)
