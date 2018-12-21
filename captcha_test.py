#! /usr/bin/python3

import pickle
from getpass import getpass
import requests
from main import GradeChecker

if __name__ == "__main__":
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
    count = 0
    err_count = 0
    while True:
        obj = GradeChecker()
        ret, err = obj.login(username, password)
        count+=1
        if ret:
            print('Logged in (',err_count,'/',count,')')
        else:
            err_count+=1
            print('LoginERR:',err)
