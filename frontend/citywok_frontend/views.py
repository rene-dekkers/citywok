from flask import request, session, redirect, url_for, jsonify, render_template, make_response

from citywok_frontend import app, auth, connection, _
from citywok_frontend.exception import ApiException


from pprint import pprint, pformat

def __filter_virtuals_by(virtuals, search):
	r = []
	search = search.lower()
	for i in virtuals:
		if search in i['name'].lower(): r.append(i)
	return r

def __group_virtuals_by(virtuals, groupby):
	grouped = {}

	if groupby == _('memory'): keyname = 'memory'
	elif groupby == _('state'): keyname = 'state'
	elif groupby == _('nrvirtcpu'): keyname = 'nrvirtcpu'
	else: keyname = 'hypervisor'
	for v in virtuals:
		if v[keyname] not in grouped:
			grouped[v[keyname]] = []
		grouped[v[keyname]].append(v)
	virtuals = grouped
	#virtuals = list(grouped.values())
	
	return virtuals

def __order_virtuals_by(virtuals, orderby = None):
	if orderby == _('memory'): keyname = 'memory'
	elif orderby == _('nrvirtcpu'): keyname = 'nrvirtcpu'
	else: keyname = 'name'
	import operator
	if keyname != 'name':#first order by name
		virtuals.sort(key = operator.itemgetter('name'))
	virtuals.sort(key = operator.itemgetter(keyname))
	return virtuals

@app.route('/login', methods=['GET','POST'])
def login():
	if auth.CheckAuth():
		return redirect(url_for('index'), code=302)
	if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
		result, message = auth.Authenticate(request.form['login'], request.form['password'])
		if result == auth.AUTH_OK:
			return redirect(url_for('index'), code=302)
		#elif result == auth.AUTH_FAILED:
		else:
			return make_response(render_template('cw/login.html', error = message))
	return make_response(render_template('cw/login.html'))

@app.route('/logout', methods=['GET'])
def logout():
	auth.LogOut()
	return redirect(url_for('login', code=302))

@app.route('/')
@auth.CheckAuth
def index():
	return make_response(render_template('cw/index.html'))


@app.route('/preferences/<string:username>', methods=['GET'])
@auth.CheckAuth
def preferences(username):
	return make_response(render_template('cw/preferences.html'))

@app.route('/hypervisor/', methods=['GET'])
@app.route('/hypervisor/<string:hypervisor>', methods=['GET'])
@auth.CheckAuth
def hypervisor(hypervisor = None):
	return make_response(
		render_template('cw/hypervisor.html',
			virtuals = virtuals,
	))

@app.route('/plain', methods=['GET'])
def plain():
	from collections import OrderedDict
	from datetime import datetime
	_vs = connection.get_all_virtuals()
	_vs = __order_virtuals_by(_vs, 'name')
	_vs = __group_virtuals_by(_vs, 'hypervisor')
	od = OrderedDict(sorted(_vs.items(), key=lambda t: t[0]))
	return make_response(render_template('cw/virtuals_plain.txt', virtuals = od, now = datetime.now()))

@app.route('/virtual/', methods=['GET'])
@app.route('/virtual/<string:virtual>', methods=['GET'])
@app.route('/virtual/<string:virtual>/<string:tab>', methods=['GET'])
@auth.CheckAuth
def virtual(virtual = None, tab = None):
	if virtual is None:
		from collections import OrderedDict
		#save form settings to session
		for i in ['view','groupby','orderby','search']:
			try: session[i] = request.args[i]
			except: pass

		_vs = connection.get_all_virtuals()
		if session.get('search','') is not '':
			app.logger.info("Search virtuals by ->%s<-" % session.get('search'))
			_vs = __filter_virtuals_by(_vs, session.get('search'))
		if session.get('orderby','') is not '':
			app.logger.debug("Order virtuals by ->%s<-" % session.get('orderby'))
			_vs = __order_virtuals_by(_vs, session['orderby'])
		else:
			_vs = __order_virtuals_by(_vs)
		if session.get('groupby','') is not '':
			app.logger.debug("Group virtuals by ->%s<-" % session.get('search'))
			_vs = __group_virtuals_by(_vs, session['groupby'])
		else:
			_vs = {'':_vs}
		od = OrderedDict(sorted(_vs.items(), key=lambda t: t[0]))
		return make_response(
			render_template('cw/virtuals.html',
				virtuals = od,
		))
	else:
		_v = connection.search(virtual).get_virtual(virtual)
		token = connection.search(virtual).create_token(virtual)
		if 'websocket' in token:
			ws_uri = token['websocket'] + '?token=%s' % token['token']
		else:
			ws_uri = app.config['WEBSOCKET_URL_USERLAND'] + '?token=%s' % token['token']
		app.logger.info('Websocket for virtual %s available at %s' % (_v['name'], ws_uri))
		return make_response(
			render_template('cw/virtual.html',
				virtual = _v,
				tab = tab,
				ws_uri = ws_uri,
		))

@app.route('/virtual/<virtual>/screenshot', methods=['GET'])
@auth.CheckAuth
def virtual_screenshot(virtual):
	import base64, os
	try:
		size=tuple(request.args['size'].split('x'))
	except:
		size = ('800','')
	payload = connection.search(virtual).get_virtual_screenshot(virtual, size=size)
	if payload in [None,False]:
		import base64
		black = open('%s/static/img/virtual_nostate.png' % os.path.dirname(os.path.realpath(__file__)), mode='rb').read()
		payload = base64.b64encode(black).decode()

	response = make_response(base64.b64decode(payload))
	response.headers['content-type'] = 'image/png'
	return response

@app.route('/virtual/<virtual>/state', methods=['PUT'])
@auth.CheckAuth
def put_virtual_state(virtual):
	try:
		if request.json is None:
			raise ApiException('Please send data in json format')
		result = connection.search(virtual).request('put', ['virtual',virtual,'state'], json=request.json)
		if result.status_code != 200:
			raise Exception(result.json()['message'])
		return jsonify({})
	except:
		return jsonify({'message':str(sys.exc_info()[1])}), 400

@app.route('/new_virtual', methods=['GET','POST'])
@auth.CheckAuth
def new_virtual():
	if request.method == 'POST':
		print('do iets')
	return make_response(
		render_template('cw/new_virtual.html',
	))

#from flask import Response, stream_with_context
#@app.route('/websocketproxy')
#def websocketproxy():
#	"IN DEVELOPMENT: Proxy http to websocketbackend."
#	#TODO reverse engineer this with a real websocket
#	import requests
#	_headers = {}
#	for h,v in request.headers.items():
#		_headers[h] = v
#	resp = requests.get('http://localhost:8091?token=plop', stream=True, headers = _headers)
#
#	_headers = {}
#	#for h,v in resp.headers.items():
#	#	_headers[h] = v
#	#_headers['Connection'] = 'close' if resp.headers['Upgrade'] == '' else 'upgrade'
#	_headers['Connection'] = resp.headers['Connection']
#	_headers['Sec-WebSocket-Accept'] = resp.headers['Sec-WebSocket-Accept']
#	_headers['Sec-WebSocket-Protocol'] = resp.headers['Sec-WebSocket-Protocol']
#	_headers['Upgrade'] = resp.headers['Upgrade']
#	real_response = Response(
#		stream_with_context(resp.iter_content()),
#		content_type = req.headers['content-type'],
#		headers = _headers,
#		status = resp.status_code,
#	)
#	return real_response
