#!/usr/bin/env python
#coding: utf8

import threading
from settings import QUEUE_SETTINGS

class WorkQueue( ):
	"""Distributes work to miners using queue mechanism."""
	def __init__( self ):
		self.lock = threading.Condition()
		self.result_lock = threading.Condition()
		# Pending work
		self.jobQueue = []
		# Pending results
		self.resultsDict = {}

	def get_result(self, initialHash):
		"""Get result from queue."""
		result = None
		self.result_lock.acquire()
		
		while True:
			if initialHash in self.resultsDict:
				# There is a result for our key.
				result = self.resultsDict[initialHash]
				del self.resultsDict[initialHash]
				break
			else:
				# No result in the queue, wait for work
				self.result_lock.wait()
				
		self.result_lock.release()
		return result	
	
	def get_work( self ):
		"""Returns work which needs to be done or None if timeout is reached."""
		exit = False	
		result = None
		self.lock.acquire()
		
		while True:
			if len( self.jobQueue ) > 0:
				# Dequeue work
				result = self.jobQueue[0]
				del self.jobQueue[0]
				break
			elif not exit:
				# wait with timeout, recheck jobQueue and exit
				self.lock.wait(QUEUE_SETTINGS['TIMEOUT'])
				exit = True
			else:
				break
		
		self.lock.release()
		return result

	def push_result( self, initialHash, trialValue, nonce):
		"""Push result to the dictionary."""
		self.result_lock.acquire()
		self.resultsDict[initialHash] = (trialValue, nonce)
		# Notify all that results are available
		self.result_lock.notifyAll()
		self.result_lock.release()

	def enqueue( self, target, initialHash ):
		"""Add a new work item to the queue."""
		work = (target, initialHash)
		self.lock.acquire()
		# enqueue the work item
		self.jobQueue.append(work)
		self.lock.notifyAll()
		self.lock.release()
