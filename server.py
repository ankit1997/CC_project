import os
import sys
import json
import requests
import traceback
import numpy as np
from PIL import Image

NODES_FILE = ".node-list"
MAP_FILE = ".mapping"

def INIT_SERVER(cmd_args, mode='w'):
	if len(cmd_args) == 0:
		print("No arguments found. Give IP addresses of the nodes.")
		return

	with open(NODES_FILE, mode) as file:
		file.write('\n'.join(cmd_args))
	print("Done.")

class ServerHelper:
	def __init__(self):
		self.TEXT_EXTENSIONS = ['.txt', '.py', '.c', '.cpp']
		self.IMG_EXTENSIONS = ['.jpg', '.png', '.jpeg']
		
		# Load mappings
		if os.path.isfile(MAP_FILE):
			with open(MAP_FILE) as f:
				self.map = json.load(f)
		else:
			self.map = {}

		# Load nodes
		if os.path.isfile(NODES_FILE):
			self.nodes = open(NODES_FILE).read().split('\n')
			self.nodes = list(filter(lambda x: len(x.strip())>0, self.nodes))
			print(self.nodes)
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
			size = resp.json()['storage']
			print('{}: {}'.format(node, size))
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

		node = self.select_node()
		resp = self.send_request(reqtype='post', node=node, route='add_file', json=json)
		if resp.status_code == 200:
			self.map[fname] = node
		self._save_map() # save the new map

		print("Done.")

	def get_file(self, fname):
		fname = os.path.basename(fname)
		extension = os.path.splitext(fname)[1]
		try:
			node = self.map[fname]
		except:
			print("No track of {}".format(fname))
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

		if reqtype == 'post':
			resp = requests.post('{}/{}'.format(node, route), json=json)
		elif reqtype == 'get':
			resp = requests.get('{}/{}'.format(node, route))
		return resp

	def _save_map(self):
		'''
			Save the map file.
		'''
		with open(MAP_FILE, 'w') as f:
			json.dump(self.map, f)

	def _save_text_file(self, fname, data):
		with open(fname, 'w') as file:
			file.write(data)

	def _save_img_file(self, fname, data):
		try:
			img = Image.fromarray(np.asarray(data, dtype=np.uint8))
			img.save(fname)
		except:
			print(traceback.format_exc())

if __name__ == '__main__':

	if sys.argv[1] == 'init':
		INIT_SERVER(sys.argv[2:])

	elif sys.argv[1] == 'add-node':
		INIT_SERVER(sys.argv[2:], mode='a')

	elif sys.argv[1] == 'list-nodes':
		print(open(NODES_FILE).read())

	elif sys.argv[1] == 'store':
		fname = sys.argv[2]
		assert os.path.isfile(fname), "{} is not a valid file.".format(fname)
		fname = os.path.basename(fname)

		helper = ServerHelper()
		helper.send_file(fname) # Send the file to a client.

	elif sys.argv[1] == 'get':
		fname = sys.argv[2]

		helper = ServerHelper()
		helper.get_file(fname) # Get file from the appropriate client.

	elif sys.argv[1] == '-h' or sys.argv[1] == 'help':
		print("Some work to do here...") #TODO

	else:
		print("Invalid command line arg. Use -h for help.")
		exit()