#!/usr/bin/python3


import urllib.request
import base64
import json
import os
import sys
import argparse
from datetime import datetime

BASE_URL='https://app.paymoapp.com/api'

class PaymoTasks:
    homePath = os.path.expanduser('~')
    filePath = homePath + "/.paymoapi.secret.json"
    def api_key(self):
        try:
            with open(self.filePath) as secret:
                data = json.load(secret)
                return  (data["secret"], None) if 'secret' in data else (None, "error: missing key 'secret'")
        except FileNotFoundError:
            return (None, 'error: ~/.paymoapi.secret.json not found.\ncreate it.')


    def getTasks(self):
        api_key ,_ = self.api_key()
        if not api_key:
            return []
        url = BASE_URL + '/tasks?where=complete=false'
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(api_key, 'X').encode('utf-8'))
        request = urllib.request.Request(url,
                                         headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        with urllib.request.urlopen(request) as f:
            try:
                return json.loads(f.read())['tasks']
            except ValueError:
                return []
            else:
                return []

    def outputTasks(self):
        func = lambda i: {'title': i['name'], 'subtitle' : i['code'], 'arg':i['id']}
        print(json.dumps({'items':[func(task) for task in self.getTasks()]}))

    def me(self):
        api_key, _ = self.api_key()
        if not api_key:
            return []
        url = BASE_URL + '/me'
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(api_key, 'X').encode('utf-8'))
        request = urllib.request.Request(url,
                                         headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        with urllib.request.urlopen(request) as f:
            try:
                users = json.loads(f.read())['users']
                if len(users) <  1 or 'id' not in users[0]:
                    return None
                return users[0]['id']
            except ValueError:
                return None

    def startTask(self, task_id):
        user_id = self.me()
        print("user_id={}".format(user_id), file=sys.stderr)
        if not user_id:
            return
        api_key, _ = self.api_key()
        if not api_key:
            return []
        url = BASE_URL + '/entries'
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(api_key, 'X').encode('utf-8'))
        now = datetime.utcnow().isoformat()
        obj = {"task_id" : task_id, "user_id" : user_id, "description":"start from alred workflow", "start_time":now}
        json_data = json.dumps(obj).encode("utf-8")
        print(json_data, file=sys.stderr)
        request = urllib.request.Request(url,
                                         headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8'),
                                                  'Content-Type': 'application/json'},
                                         data=json_data,
                                         method='POST')
        try:
            with urllib.request.urlopen(request) as response:
                print(response, file=sys.stderr)
                response_body = response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
                print(e.msg, file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--start', nargs=1)
    args = parser.parse_args()
    task = PaymoTasks()
    (_, error) = task.api_key()
    if error:
        print( json.dumps({"items": [{'title': 'ERROR', 'subtitle' : error, 'arg':error}]}))
        sys.exit(0)

    if args.start:
        print(int(args.start[0]), file=sys.stderr)
        PaymoTasks().startTask(int(args.start[0]))
        sys.exit(0)
    PaymoTasks().outputTasks()
