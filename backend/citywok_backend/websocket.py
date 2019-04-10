import sys, os, requests
if 'websockify' not in sys.path:
	sys.path.append(
		os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'websockify'))
	)

import websockify
#from websockify import websockify
from websockify.websocketproxy import *

class Token():
	def __init__(self, backend_url):
		self.__backend_url = backend_url
	
	def lookup(self, token):
		result = requests.get('%s/token/%s' % (self.__backend_url, token))
		if result.status_code == 200:
			data = result.json()
			return [data['host'], data['port']]
		raise Exception('Status code not 200 when looking op token %s. %d' % (token, result.status_code))

class Websockify(object):
	__thread = None
	backend_url = None
	apikey = None


	def __run(self, **kwargs):
		opts = {
			'listen_host': kwargs['host'],
			'verbose': None,
			'token_plugin': kwargs['token_plugin'],
			'target_host': None,
			'ssl_target': None,
			'web': None,
			'listen_port': kwargs['port'],
			'source_is_ipv6': None,
			'target_port': None,
			'auth_plugin': None,
			'run_once': None,
			'idle_timeout': 0,
			'traffic': None,
			'key': None,
			'heartbeat': 0,
			'daemon': False,
			'wrap_mode': 'exit',
			'wrap_cmd': None,
			'record': None,
			'cert': 'self.pem',
			'unix_target': None,
			'timeout': 0,
			'ssl_only': None
		}
		server = WebSocketProxy(**opts)
		logger_init()
		server.start_server()

	def run(self, **kwargs):
		from multiprocessing import Process
		import psutil, signal

		parent = psutil.Process(os.getppid())
		children = parent.children()
		if len(children) > 1:
			#print('  - kill (old) websocket child with PID: %d' % children[0].pid)
			#os.kill(children[0].pid, signal.SIGTERM)
			return False
		print('  - websocket started..')

		kwargs['token_plugin'] = Token(self.backend_url)

		self.__thread = Process(target=self.__run, kwargs=kwargs)
		self.__thread.start()
		#self.__thread.join()
