#!/usr/bin/env python
#coding: utf8

import json
import base64
import logging
import threading
from SocketServer import BaseRequestHandler, ThreadingTCPServer

import workqueue
from settings import SERVER_SETTINGS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# pass queue object to Threading TCP server
class customTCPServer(ThreadingTCPServer):
	#allow_reuse_address = True
	def __init__(self, server_address, RequestHandlerClass, queue):
		ThreadingTCPServer.__init__(self, 
									server_address, 
									RequestHandlerClass)
		self.queue = queue


class BitmessageHandler:
	""" Base class defining core Bitmessage mining server methods."""
		
	def do_pow(self):
		"""Add work to queue, and wait for the result from miners."""
		# add work to queue
		self.server.queue.enqueue(self.json_data['target'], base64.b64decode(self.json_data['initialHash']))
		logger.debug('DO_POW: %s\n' % self.json_data)
		# get result
		trialValue, nonce = self.server.queue.get_result( self.json_data['initialHash'] )
		result_data = self._to_JSON({'status': 200, 'trialValue': trialValue, 'nonce': nonce})
		logger.debug('GET_RESULT: %s\n' % result_data)
		return result_data

	def get_work(self):
		"""Get work from a queue. If there is no work to be done, wait few seconds using the long polling technique."""
		# get work from queue
		work = self.server.queue.get_work()
		if work is None:
			# ping message
			result_data = self._to_JSON({'status':'NO_DATA'})
		else:
			target, initialHash = work
			result_data = self._to_JSON({'status': 200, 'target': target, 'initialHash': base64.b64encode(initialHash)})
			logger.debug('GET_WORK: %s\n' % result_data)
		return result_data

	def push_result(self):
		"""Push result to the queue."""
		logger.debug('PUSH_RESULT: %s\n' % self.json_data)
		self.server.queue.push_result(self.json_data['initialHash'], self.json_data['trialValue'], self.json_data['nonce'])
		result_data = self._to_JSON({'status': 200})
		return result_data

	def _from_JSON(self, recv_data):
		"""Translate from JSON format."""
		try:
			json_data = json.loads(recv_data)
		except ValueError as e:
			json_data = None
			pass
		return json_data

	def _to_JSON(self, send_data):
		"""Translate to JSON format."""
		try:
			json_data = json.dumps(send_data)
		except ValueError as e:
			json_data = None
			pass
		return json_data	


class ClientTcpHandler(BaseRequestHandler, BitmessageHandler):
	"""Derived TCP handler class which contains default BaseRequestHandler and methods from BitmessageHandler. """
	
	def handle(self):
		"""TCP connection handler."""
		# while the client is connected, hold connection open
		while True:
			try:
				recv_data = self.request.recv(1024).strip()
				if not recv_data:
					# the client probably disconnected
					break
				self.json_data = self._from_JSON(recv_data)
				if not self.json_data:
					break
				# the request is valid JSON
				self._call_mining_method()
			except Exception as e:
				print "Exception while receiving message: ", e
				break

	def _call_mining_method(self):
		"""Call appropriate mining server method. Send return value to open TCP connection."""
		if 'method' in self.json_data:
			if self.json_data['method'] == 'do_pow':
				ret = self.do_pow()
				self.request.sendall(ret)
			elif self.json_data['method'] == 'get_work':
				ret = self.get_work()
				self.request.sendall(ret)
			elif self.json_data['method'] == 'push_result':
				ret = self.push_result()
			else:
				logger.debug('Unsupported json method!\n')


class bitmessageMiningServer( object ):
	def __init__(self, workQueue ):
		self.queue = workQueue
		
	def run(self):
		"""Run mining server."""
		logger.info('Starting Metanoia mining service...')
		self.server = customTCPServer((SERVER_SETTINGS['address'], SERVER_SETTINGS['port']), ClientTcpHandler, self.queue)
		
		try:
			logger.info('Server started...\n')
			self.server.serve_forever()
		except Exception as e:
			self.server.shutdown()
			raise Exception(e)

	def stop(self):
		self.server.shutdown()


# blocking service
def start(object):
	"""Start mining threaded mining server."""
	server_process = bitmessageMiningServer(object)
	server_process.daemon = True
	server_process.run()


# start Bitmessage mining server
if __name__ == "__main__":
	# initialize Queue
	work_queue = workqueue.WorkQueue()
	
	try:
		client_server = start(work_queue)
	except KeyboardInterrupt:
		raise
	
	
	
