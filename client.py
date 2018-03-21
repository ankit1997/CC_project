from flask import Flask, request, jsonify
from helper import ClientHelper

app = Flask(__name__)
helper = ClientHelper()

@app.route('/')
def index():
	# TODO: show files using HTML
	return "Welcome to our cloud network"

# @app.route('/init', methods=['POST', 'GET'])
# def init():
# 	'''
# 		Initialize the client program.
# 		Jobs:
# 			1. Create a directory on the system. This is where all the files will be stored.
# 	'''
# 	json = request.get_json()
# 	helper.init(json)
# 	return "Done"

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

@app.route('/remaining_space', methods=['GET', 'POST'])
def get_remaining_space():
	return jsonify({'storage': helper.storage})

if __name__ == '__main__':
	helper.init({'dirname': 'cloud-client', 'storage': 10})
	app.run(debug=True)