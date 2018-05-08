import os
import re
import sys
import glob
import json
import getpass
import requests
import traceback
import numpy as np
import pandas as pd
from PIL import Image

TIMEOUT = 2
DATA_PATH = 'data'
LAST_USER = '.lastUser'
CREDENTIALS_FILE = ".credentials"
MAP_FILE = ".mapping"
NODES_FILE = ".node-list"
FORBIDDEN_CHARS = ['+', ',', '*']

def INIT_SERVER(cmd_args, mode='w'):
    if len(cmd_args) == 0:
        print("No arguments found. Give IP addresses of the nodes.")
        return

    with open(NODES_FILE, mode) as file:
        file.write('\n' + '\n'.join(cmd_args))
    print("Done.")

def validate_input(word):
    for c in FORBIDDEN_CHARS:
        if c in word:
            print("{} not allowed in username or password.".format(c))
            return False
    return True

def setLastUser(username, password):
    with open(LAST_USER, 'w') as file:
        file.write(username)

def clearLastUser():
    if os.path.isfile(LAST_USER):
        os.remove(LAST_USER)

def check_file_location(*fnames):
    for f in fnames:
        parts = f.split(os.sep)
        if 'data' not in parts:
            print("Files at server must be stored in data/ directory. See {}".format(f))
            exit()

class ServerHelper:
    def __init__(self):
        self.TEXT_EXTENSIONS = ['.txt', '.py', '.c', '.cpp']
        self.IMG_EXTENSIONS = ['.jpg', '.png', '.jpeg']
        
        self.user = self._logged()

        # Load mappings
        if os.path.isfile(MAP_FILE):
            with open(MAP_FILE) as f:
                self.map = json.load(f)
                if self.user not in self.map.keys():
                    self.map[self.user] = {}
        else:
            self.map = {}
            self.map[self.user] = {}

        # Load nodes
        if os.path.isfile(NODES_FILE):
            self.nodes = open(NODES_FILE).read().split('\n')
            self.nodes = list(filter(lambda x: len(x.strip())>0, self.nodes))
        else:
            self.nodes = []

        if len(self.nodes) == 0:
            print("Please initialize server.")
            exit()

    def select_node(self):
        '''
            Select a node for sending the file.
        '''

        max_size = -1
        max_node = None
        for node in self.nodes:
            # Get remaining storage from all nodes
            resp = self.send_request(reqtype='get', node=node, route='remaining_space')
            if resp == 'timeout':
                continue

            size = resp.json()['storage']
            print('{}: {}'.format(node, size))
            if size > max_size:
                max_size = size
                max_node = node
        print("Node {} has maximum storage - {}".format(node, max_size))
        return max_node

    def send_file(self, fname):
        assert os.path.isfile(fname), "{} is not a valid file.".format(fname)

        print("Sending {} ...".format(fname))
        basename = os.path.basename(fname)
        extension = os.path.splitext(basename)[1]

        json = {}
        if extension in self.TEXT_EXTENSIONS:
            data = open(fname).read()
            json['fname'] = basename
            json['fdata'] = data
        elif extension in self.IMG_EXTENSIONS:
            img = np.array(Image.open(fname)).tolist()
            json['fname'] = basename
            json['fdata'] = img
        else:
            print("Extension cannot be passed to client.")
            return

        node = self.select_node()
        resp = self.send_request(reqtype='post', node=node, route='add_file', json=json)
        if resp.status_code == 200:
            self.map[self.user][basename] = node
        self._save_map() # save the new map

        if resp.json()['meta']:
            print(resp.json()['meta'])

    def get_file(self, fname):
        fname = os.path.basename(fname)
        extension = os.path.splitext(fname)[1]
        try:
            node = self.map[self.user][fname]
        except:
            print("No track of {} for user: {}".format(fname, self.user))
            exit()

        resp = self.send_request('post', node=node, route='get_file', json={'fname': fname})
        if resp.status_code != 200:
            print("Connection problem.")
            return

        json = resp.json()
        if json['success']:
            fdata = json['fdata']
            if extension in self.TEXT_EXTENSIONS:
                self._save_text_file(fname, fdata)
            elif extension in self.IMG_EXTENSIONS:
                self._save_img_file(fname, fdata)
            else:
                print("Unreachable code.")
        else:
            print("Cannot get file. REASON: {}".format(json['error']))

    def send_request(self, reqtype, node, route, json=None):
        '''
            Args:either
                reqtype : Type of http request. Should be either 'get' or 'post'
                node : IP address of the client node
                route : Route of the url. #TODO: improve description of `route`
                json : JSON/Dict object to pass to the client in case of 'post' requests.
            Return:
                Response object.
        '''
        resp = ''
        try:
            if reqtype == 'post':
                resp = requests.post('{}/{}'.format(node, route), json=json, timeout=TIMEOUT)
            elif reqtype == 'get':
                resp = requests.get('{}/{}'.format(node, route), timeout=TIMEOUT)
            
        except requests.exceptions.ConnectTimeout:
            resp = 'timeout'

        return resp

    def evaluate_programs(self, regex, inputFile, outputFile):
        # Find all the files matching the regex.
        fnames = self.map[self.user].keys()
        fnames = [fname for fname in fnames if re.match(regex, fname)]

        if len(fnames) == 0:
            print("No file found with matching regex.")
            return

        for fname in fnames:
            node = self.map[self.user][fname]

            fname = os.path.join(DATA_PATH, fname)
            if not os.path.isfile(fname):
                print("{} missing.".format(fname))
                exit()

            resp = self.send_request(reqtype='post', 
                                    node=node, 
                                    route='evaluate_students',
                                    json={
                                        'fname': fname,
                                        'fdata': open(fname).read(),
                                        'inputFile': inputFile,
                                        'inputData': open(inputFile).read(),
                                        'outputFile': outputFile,
                                        'outputData': open(outputFile).read(),
                                        })
            print(resp.json()['result'])

    def _save_map(self):
        '''
            Save the map file.
        '''
        with open(MAP_FILE, 'w') as f:
            json.dump(self.map, f, indent=4)

    def _save_text_file(self, fname, data):
        fname = os.path.join(DATA_PATH, fname)
        with open(fname, 'w') as file:
            file.write(data)

    def _save_img_file(self, fname, data):
        fname = os.path.join(DATA_PATH, fname)
        try:
            img = Image.fromarray(np.asarray(data, dtype=np.uint8))
            img.save(fname)
        except:
            print(traceback.format_exc())

    def _logged(self):
        if os.path.isfile(LAST_USER):
            data = open(LAST_USER).read().strip()
            if data:
                return data
        print("Login to operate!")
        exit()

if __name__ == '__main__':

    os.makedirs(DATA_PATH, exist_ok=True)

    if len(sys.argv) == 1:
        print("Use -h for help.")
        exit()

    if sys.argv[1] == 'init':
        clearLastUser()
        INIT_SERVER(sys.argv[2:])

    elif sys.argv[1] == 'add-node':
        INIT_SERVER(sys.argv[2:], mode='a')

    elif sys.argv[1] == 'list-nodes':
        print(open(NODES_FILE).read())

    elif sys.argv[1] == 'store':
        fnames = sys.argv[2:]
        check_file_location(*fnames)

        print("Storing files on clients...")
        for i in range(len(fnames)):
            fname = fnames[i]
            helper = ServerHelper()

            # Send the file to a client.
            helper.send_file(fname)

    elif sys.argv[1] == 'get':
        fname = sys.argv[2]

        helper = ServerHelper()
        helper.get_file(fname) # Get file from the appropriate client.

    elif sys.argv[1] == 'test':
        regex = sys.argv[2] # Get the regular expression sent by the teacher.
        inputFile = sys.argv[3]
        outputFile = sys.argv[4]

        check_file_location(inputFile, outputFile)

        helper = ServerHelper()
        helper.evaluate_programs(regex, inputFile, outputFile)

    elif sys.argv[1] == 'login':
        username = input("Username: ")
        password = getpass.getpass()

        if not validate_input(username) or not validate_input(password):
            exit()

        data = open(CREDENTIALS_FILE).read()
        if "+{}, {}+".format(username, password) in data:
            setLastUser(username, password)
            print("Logged in.")
            exit()
        print("Invalid credentials. Signup instead?")

    elif sys.argv[1] == 'signup':
        username = input("Username: ")
        password = getpass.getpass()

        if not validate_input(username) or not validate_input(password):
            exit()

        if os.path.isfile(CREDENTIALS_FILE):
            data = open(CREDENTIALS_FILE).read()

            if "+{}, ".format(username) in data:
                print("Username already exists.")
                exit()

        with open(CREDENTIALS_FILE, 'a') as file:
            file.write("+{}, {}+".format(username, password))

        setLastUser(username, password)

    elif sys.argv[1] == 'logout':
        clearLastUser()
        print("Signing off.")

    elif sys.argv[1] == 'user':
        if os.path.isfile(LAST_USER):
            data = open(LAST_USER).read().strip()
            if data:
                print(data)
        else:
            print("No user found.")

    elif sys.argv[1] == '-h' or sys.argv[1] == 'help':
        helpString = '''Command line options:
        init : Initialize Server.
        login : Login with username and password.
        signup : Signup with username and password.
        logout : Logout.
        user : Get current logged in user.
        add-node : Add a node to list of clients.
        list-nodes : List all available nodes.
        store : Store one or more files on client.
        get : Download a previously saved file to server from corresponding client.
        quiz : Test quiz of students.
        '''
        print(helpString)
        exit()

    else:
        print("Invalid command line arg. Use -h for help.")
        exit()