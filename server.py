import requests
import os
import sys
from PIL import Image
import numpy as np

class ServerHelper:
	def __init__(self):
		self.TEXT_EXTENSIONS = ['.txt', '.py', '.c', '.cpp']
		self.IMG_EXTENSIONS = ['.jpg', '.png', '.jpeg']
		self.map = {}
		self.nodes = ['http://192.168.43.220:10001']

	def select_node(self):
		'''
			Select a node for sending the file.
		'''

		nodes = self._get_nodes()
		max_size = -1
		max_node = None
		for node in self.nodes:
			# Step-1 : Get remaining storage from all nodes
			resp = self.send_request(reqtype='get', node=node, route='remaining_space')
			size = resp.json()['storage']
			if size > max_size:
				max_size = size
				max_node = node
		print("Node {} has maximum storage - {}".format(node, max_size))
		return max_node

	def send_file(self, fname):
		print("Sending {} ...".format(fname))
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

		# node = 'http://192.168.43.220:10001'
		node = self.select_node()
		resp = self.send_request(reqtype='post', node=node, route='add_file', json=json)
		if resp.status_code == 200:
			self.map[fname] = node

	def send_request(self, reqtype, node, route, json=None):
		if reqtype == 'post':
			# resp = requests.post('http://127.0.0.1:5000/add_file', json=json)
			resp = requests.post('{}/{}'.format(node, route), json=json)
		elif reqtype == 'get':
			resp = requests.get('{}/{}'.format(node, route))
		return resp

	def _get_nodes(self):
		'''
			Return all nodes which are known to server.
		'''
		nodes = []
		for k in self.map:
			nodes.append(self.map[k])
		return nodes

if __name__ == '__main__':
	fname = sys.argv[1]
	fname = os.path.basename(fname)

	helper = ServerHelper()
	helper.send_file(fname)