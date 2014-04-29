#!/usr/bin/env python
#coding: utf8

from threading import Thread
import socket
import json

import base64
import hashlib
from struct import unpack, pack
import sys

def _doSafePoW(target, initialHash):
	nonce = 0
	trialValue = float('inf')
	while trialValue > target:
		nonce += 1
		# big endian unsigned long long
		trialValue, = unpack('>Q',hashlib.sha512(hashlib.sha512(pack('>Q',nonce) + initialHash).digest()).digest()[0:8])
	return [trialValue, nonce]


class Miner(object):
	def __init__( self, server ):
		self.server = server

	def poll_for_updates( self ):
		while True:
			get_work = {'method':'get_work'}
			self.server.send(json.dumps(get_work))
			
			response = self.server.recv(1024)
			response = json.loads(response)
			
			if response['status'] != 'NO_DATA':
				print "DO_WORK: %s" % response 
				ret = _doSafePoW(response['target'], base64.b64decode(response['initialHash']))
				result_data = json.dumps({'method':'push_result', 'trialValue':ret[0], 'nonce':ret[1], 'initialHash': response['initialHash'] })
				print "PUSH_RESULT: %s" % result_data 
				self.server.send(result_data)
			else:
				print "PING: ", response
				
				
def run():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# replace with some real server ip, port
	server.connect(('127.0.0.1', 7040))
	
	miner = Miner( server )
	miner.poll_for_updates()
	
# start
if __name__ == "__main__":
	run()