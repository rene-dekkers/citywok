"""
Hypervisor / REST service libvirt communicater

Goals:
- Communicate with libvirt daemon
- Provide information about a single hypervisor
- Provide information about all registered virtuals
- Ability to update/delete hypervisor / virtual configuration
- Restrict access by an apikey authentication
"""
__version__ = 0.01
__author__ = 'Rene Dekkers'
__url__ = 'https://git.better-it-solutions.nl/virtualization/citywok'

import sys
from flask import Flask, jsonify, make_response, request, g
from citywok_backend.exception import ApiException
from citywok_backend.exception import ConnectionError

app = Flask(__name__)
app.config.from_pyfile('settings.ini')

from citywok_backend.websocket import Websockify
websocket = websocket.Websockify()
websocket.backend_url = 'http://%s:%d' % (app.config['HOST'], app.config['PORT'])
websocket.run(host = app.config['WEBSOCKET_HOST'], port = app.config['WEBSOCKET_PORT'])

import citywok_backend.libvirtconnection
libvirtconnection.log = app.logger
conn = libvirtconnection.LibvirtConnection()

import citywok_backend.auth
auth.app = app

#websockify token
tokens = {}

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(ApiException)
def handle_error(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response

@app.route('/hypervisor', methods=['GET'])
def get_hypervisor():
	try:
		return jsonify(conn.get_hypervisor())
	except:
		raise ApiException(str(sys.exc_info()[1]), 500)

@app.route('/virtual', methods=['GET'])
@app.route('/virtual/<virtual>', methods=['GET'])
@auth.CheckAuth
def get_virtual(virtual=None):
	try:
		if virtual is not None:
			return jsonify({'virtual':conn.get_virtual(virtual)})
		else:
			return jsonify({'virtuals':conn.get_virtuals()})
	except ApiException:
		raise
	except:
		raise ApiException(str(sys.exc_info()[1]), 500)

@app.route('/virtual/<virtual>/screenshot', methods=['GET'])
def get_virtual_screenshot(virtual):
	try:
		if conn.get_virtual(virtual)['state'] != 'running':
			raise ApiException('Machine state != running', 500)
		try:
			size = request.args['size'].split('x')
			if size[0] == '': size[0] = 0
			if size[1] == '': size[1] = 0
			size = tuple([int(size[0]), int(size[1])])
		except:
			size = ()
		return conn.screenshot(virtual, size=size)
	except:
		raise ApiException(str(sys.exc_info()[1]), 500)

@app.route('/virtual/<virtual>/state', methods=['PUT'])
def put_virtual_state(virtual):
	try:
		if 'state' not in request.json:
			raise ApiException('Please post data as json')
		_state = request.json['state'].lower()
		if _state == 'running':
			conn.create(virtual)
		elif _state == 'reboot':
			conn.reboot(virtual)
		elif _state == 'shutdown':
			conn.shutdown(virtual)
		elif _state == 'reset':
			conn.reset(virtual)
		elif _state == 'destroy':
			conn.destroy(virtual)
		elif _state == 'suspended':
			conn.suspend(virtual)
		elif _state == 'resume':
			conn.resume(virtual)
		else:
			raise ApiException("State '%s' is not supported" % _state)
		return jsonify({'state':_state,'result':True})
	except ApiException:
		raise
	except:
		raise ApiException(str(sys.exc_info()[1]), 500)

@app.route('/token/<virtual>', methods=['POST'])
def create_token(virtual):
	"Generate a new token to connect to the websockify service"
	try:
		import uuid
		virtual = conn.get_virtual(virtual)['name']
		token = uuid.uuid4().hex
		tokens[virtual] = token
		r = {'token':token}
		if 'WEBSOCKET_URL_USERLAND' in app.config:
			r['websocket'] = app.config['WEBSOCKET_URL_USERLAND']
		return jsonify(r)
	except ApiException:
		raise
	except:
		raise ApiException(str(sys.exc_info()[1]), 500)

@app.route('/token/<token>', methods=['GET'])
#TODO alleen voor websockify token class!
def get_token(token):
	"""
	- Verify token en get the right virtual
	- Find out which spice or vnc port libvirt is hosting
	- Return this information so websockify knows what to do
	"""

	try:
		try:
			virtual = [v for v,t in tokens.items() if t == token][0]
		except:
			import time
			time.sleep(2)
			raise ApiException('Token %s was not found' % token, 404)
		graphics = conn.get_virtual_infobyxmlpath(virtual, './devices/graphics')
		gtype = graphics.get('type')
		listen = graphics.get('listen')
		port = graphics.get('port')

		if gtype is None or listen is None or port is None:
			raise ApiException("Unable to load graphic connection info", 400)
		
		return jsonify({
			'type' : gtype,
			'host' : listen,
			'port' : port,
		})
	except ApiException:
		raise
	except:
		raise ApiException(str(sys.exc_info()[1]), 500)
