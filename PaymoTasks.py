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
    project_dict = dict()

    def get_user_id(self):
        return os.getenv('paymo_user_id')

    def api_key(self):
        key = os.getenv('paymo_api_key')
        if key:
            return (key, None)
        else:
            return (None, 'error: ~/.paymoapi.secret.json not found.\ncreate it.')
        # try:
        #     with open(self.filePath) as secret:
        #         data = json.load(secret)
        #         return  (data["secret"], None) if 'secret' in data else (None, "error: missing key 'secret'")
        # except FileNotFoundError:
        #     return (None, 'error: ~/.paymoapi.secret.json not found.\ncreate it.')
    def getClients(self):
        api_key ,_ = self.api_key()
        if not api_key:
            return []
        url = BASE_URL + '/clients'
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(api_key, 'X').encode('utf-8'))
        request = urllib.request.Request(url,
                                         headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        with urllib.request.urlopen(request) as f:
            try:
                clients = json.loads(f.read())['clients']
                clients = sorted(clients, key=lambda client: client['updated_on'], reverse=True)
                return clients
            except ValueError:
                return []
            else:
                return []

    def getUsers(self):
        api_key ,_ = self.api_key()
        if not api_key:
            return []
        url = BASE_URL + '/users'
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(api_key, 'X').encode('utf-8'))
        request = urllib.request.Request(url,
                                         headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        with urllib.request.urlopen(request) as f:
            try:
                return json.loads(f.read())
            except ValueError:
                return []
            else:
                return []

    def getProjects(self, client_id=None):
        api_key ,_ = self.api_key()
        if not api_key:
            return []
        url = BASE_URL + '/projects?where=client_id={}'.format(client_id) if client_id else BASE_URL + '/projects'
        print(url, file=sys.stderr)
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(api_key, 'X').encode('utf-8'))
        request = urllib.request.Request(url,
                                         headers={"Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        with urllib.request.urlopen(request) as f:
            try:
                project_dict = {}
                projects = json.loads(f.read())['projects']
                for proj in projects:
                    #print(proj.keys())
                    project_dict[proj['id']] = proj
                return project_dict
            except ValueError:
                return []
            else:
                return []

    def outputClients(self, client_list):
        func = lambda client: {'title': client['name'],
                              'match': client['name'],
                              'arg': client['id']}
        print(json.dumps( {'items': [func(client) for client in client_list]} ))

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

    def createTask(self, project_id, task_name, start=True):
        api_key ,_ = self.api_key()
        if not api_key:
            return []
        url = BASE_URL + '/tasks'
        basic_user_and_pasword = base64.b64encode('{}:{}'.format(api_key, 'X').encode('utf-8'))
        json_data = json.dumps({'project_id': project_id,
            'name': task_name }).encode('utf-8')
        print(json_data, file=sys.stderr)
        request = urllib.request.Request(url,
                                         data=json_data, 
                                         method='POST',
                                         headers={
                                             "Content-Type" : "application/json",
                                             "Authorization": "Basic " + basic_user_and_pasword.decode('utf-8')})
        try:
            with urllib.request.urlopen(request) as response:
                data = response.read().decode("utf-8")
                resp = json.loads(data)
                print(resp, file=sys.stderr)
                if start and 'tasks' in resp and len(resp['tasks']) > 0:
                    self.startTask(int(resp['tasks'][0]['id']))
        except urllib.error.HTTPError as identifier:
            print(identifier)
            print(identifier.read())

    def outputProjects(self, client_id=None):
        projects = self.getProjects(client_id)
        projects = [projects[key] for key in projects.keys()]
        projects = sorted(projects, key=lambda project: project['updated_on'], reverse=True)
        func = lambda proj: {'title': proj['name'],
                              'subtitle' : '',
                              'match': proj['name'],
                              'arg':proj['id']}
        print(json.dumps( {'items': [func(proj) for proj in projects]} ))

    def outputTasks(self):
        self.getProjects()
        func = lambda i: {'title': i['name'],
                         # 'subtitle' : self.project_dict[i['project_id']]['name'],
                          'match': '{} {} {}'.format(i['name'], i['code'], self.project_dict[i['project_id']]['name']),
                          'arg':i['id']}
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
    parser.add_argument('--client-id', nargs=1)
    parser.add_argument('--project-list', action='store_true')
    parser.add_argument('--client-list', action='store_true')
    parser.add_argument('--task-name', nargs=1)
    parser.add_argument('--project-id', nargs=1)
    args = parser.parse_args()
    task = PaymoTasks()
    (_, error) = task.api_key()

    if error:
        print( json.dumps({"items": [{'title': 'ERROR',
                                      'subtitle' : error,
                                      'arg':error
        }]}))
        sys.exit(0)

    if args.start:
        print(int(args.start[0]), file=sys.stderr)
        PaymoTasks().startTask(int(args.start[0]))
        sys.exit(0)
    elif args.project_list:
        if args.client_id and len(args.client_id)==1:
            PaymoTasks().outputProjects(client_id=args.client_id[0])
        else:
            PaymoTasks().outputProjects()
    elif args.client_list:
        PaymoTasks().outputClients(PaymoTasks().getClients())
    elif args.task_name and args.project_id:
        PaymoTasks().createTask(args.project_id[0], args.task_name[0] )
    else:
        PaymoTasks().outputTasks()
