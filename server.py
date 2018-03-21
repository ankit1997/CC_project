import requests
import os
import sys
from PIL import Image
import numpy as np

class ServerHelper:
	def __init__(self):
		self.TEXT_EXTENSIONS = ['.txt', '.py', '.c', '.cpp']
		self.IMG_EXTENSIONS = ['.jpg', '.png', '.jpeg']

	def send_file(self, fname):
		extension = os.path.splitext(os.path.basename(fname))[1]

		json = {}
		if extension in self.TEXT_EXTENSIONS:
			data = open(fname).read()
			json['fname'] = fname
			json['fdata'] = data
		elif extension in self.IMG_EXTENSIONS:
			img = np.array(Image.open(fname)).tolist()
			json['fname'] = fname
			json['fdata'] = img
		else:
			print("Extension cannot be passed to client.")
			return

		self.send_request(json)

	def send_request(self, json):
		# resp = requests.post('http://127.0.0.1:5000/add_file', json=json)
		resp = requests.post('http://192.168.43.220:10001/add_file', json=json)
		print(resp)

if __name__ == '__main__':
	fname = sys.argv[1]
	fname = os.path.basename(fname)

	helper = ServerHelper()
	helper.send_file(fname)