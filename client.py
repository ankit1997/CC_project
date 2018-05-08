import os
from helper import ClientHelper
from flask import Flask, request, jsonify

app = Flask(__name__)
helper = ClientHelper()
STORAGE_DIR = "client-storage"

@app.route('/')
def index():
    # TODO: show files using HTML
    return "Welcome to our cloud network"

@app.route('/add_file', methods=['GET', 'POST'])
def add_file():
    '''
        Adds a file in the client program.
        JSON keys:
        1. fname : Name of the file
        2. fdata : File data.
            - for text based files, it is a string
            - for images, it is a python list
    '''
    json = request.get_json()
    res = helper.save_file(json)
    return jsonify(res)

@app.route('/get_file', methods=['GET', 'POST'])
def get_file():
    json = request.get_json()
    res = helper.get_file(json)
    return jsonify(res)

@app.route('/remaining_space', methods=['GET', 'POST'])
def get_remaining_space():
    dir_size = 0
    for f in os.listdir(STORAGE_DIR):
        dir_size = dir_size + os.stat(os.path.join(STORAGE_DIR, f)).st_size

    dir_size = dir_size/(1024*1024) 
    return jsonify({'storage': helper.storage-(dir_size)})

@app.route('/evaluate_students', methods=['GET', 'POST'])
def evaluate_students():
	json = request.get_json()

	res = helper.test(json)
	return jsonify(res)

if __name__ == '__main__':
    helper.init({'dirname': STORAGE_DIR, 'storage': 10})
    app.run(host="0.0.0.0", port=10001, debug=True)
    