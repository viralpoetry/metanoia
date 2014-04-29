
import json
import base64
import socket

def run(target, initialHash):
	# connect to mining server (replace with some real server ip, port)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('127.0.0.1', 7040))
	
	data = {'method':'do_pow'}
	data['target'] = target
	data['initialHash'] = base64.b64encode(initialHash)
	try:
		s.send(json.dumps(data, ensure_ascii = False))	
	except Exception as e:
		raise
	result = json.loads(s.recv(1024))
	s.close()
	if result['status'] == 200:
		return [ result['trialValue'], result['nonce'] ]
	else:
		# we should compute pow here..
		print "POW Error"

