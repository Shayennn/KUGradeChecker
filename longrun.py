#! /usr/bin/python3

import datetime
import time
import pickle
from getpass import getpass
import requests
from check_by_api import GradeChecker
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
        with open('credential_api.pkl', 'rb') as output:
            line_token, group_line_token = pickle.load(
                output)
            output.close()
    except FileNotFoundError:
        line_token = input('LineToken: ')
        group_line_token = input('Group_Token: ')
        with open('credential_api.pkl', mode='wb') as output:
            pickle.dump((line_token, group_line_token), output)
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
            with open('api_data.pkl', 'rb') as output:
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
                      'Section:', sub_data['section'])
                print('\tGrade:', sub_data['grade'])
                print('\tStatus:', sub_data['status'])
                if sub_data['grade'] == '':
                    continue
                if (code not in old_data or old_data[code]['grade'] == '') and sub_data['grade'] != '':
                    print('\t', end='')
                    if code in announce_list:
                        msg = [code+' '+sub_data['name'] + ' Sec: ' + sub_data['section'] +
                               ' บันทึกเกรดขึ้นระบบแล้ว', '']
                        if useTwitter:
                            try:
                                print(api.PostUpdate('BOT: '+msg[0]).text)
                            except twitter.error.TwitterError as e:
                                print(e)
                        r = requests.post(line_url, headers=group_line_headers, data={
                            'message': '\n'.join(msg)})
                        print("Announced & ", end='')
                    msg = ['['+code+'] '+sub_data['name'] +
                           ' Section: '+sub_data['section']]
                    msg += ['ได้บันทึกเกรดลงระบบแล้ว']
                    msg += ['Grade: '+sub_data['grade']]
                    msg += ['Status: '+sub_data['status']]
                    r = requests.post(line_url, headers=line_headers, data={
                        'message': '\n'.join(msg)})
                    print("Notified")
                elif code in old_data and (old_data[code]['grade'] != sub_data['grade'] or old_data[code]['status'] != sub_data['status']):
                    print('\t', end='')
                    changed_data = []
                    changed_detail = []
                    if old_data[code]['grade'] != sub_data['grade']:
                        changed_data.append('แก้ไขเกรด')
                        changed_detail += ['แก้เกรดจาก '+old_data[code]
                                           ['grade']+' เป็น '+sub_data['grade']]
                    if old_data[code]['status'] != sub_data['status']:
                        changed_data += ['เปลี่ยนสถานะจาก '+old_data[code]
                                         ['status']+' เป็น '+sub_data['status']]
                        changed_detail += ['เปลี่ยนสถานะจาก '+old_data[code]
                                           ['status']+' เป็น '+sub_data['status']]
                    if code in announce_list:
                        msg = [code+' '+sub_data['name'] + ' Sec: ' + sub_data['section'] +
                               ' แก้ไขข้อมูลในระบบแล้ว', '']
                        if useTwitter:
                            try:
                                print(api.PostUpdate(
                                    'BOT: '+msg[0]+'\nนั่นคือ '+' และ'.join(changed_data)).text)
                            except twitter.error.TwitterError as e:
                                print(e)
                        msg += ['นั่นคือ '+' และ'.join(changed_data)]
                        r = requests.post(line_url, headers=group_line_headers, data={
                            'message': '\n'.join(msg)})
                        print("Announced & ", end='')
                    msg = ['['+code+'] '+sub_data['name'] +
                           ' Section: '+sub_data['section']]
                    msg += ['ได้แก้ไขข้อมูลในระบบแล้ว']
                    msg += changed_detail
                    r = requests.post(line_url, headers=line_headers, data={
                        'message': '\n'.join(msg)})
                    print("Notified")
            with open('api_data.pkl', mode='wb') as output:
                pickle.dump(data, output)
                output.close()
        else:
            print('GradeERR:', data)
        time.sleep(5)
