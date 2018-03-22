from flask import Flask, request, jsonify
from helper import ClientHelper
import os

app = Flask(__name__)
helper = ClientHelper()

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
	for f in os.listdir("cloud-client"):
		dir_size = dir_size + os.stat(os.path.join("cloud-client", f)).st_size

	dir_size = dir_size/(1024*1024) 
	return jsonify({'storage': helper.storage-(dir_size)})

if __name__ == '__main__':
	helper.init({'dirname': 'cloud-client', 'storage': 10})
	app.run(host="0.0.0.0", port=10001, debug=True)







	