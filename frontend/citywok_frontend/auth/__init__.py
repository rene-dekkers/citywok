import time
from flask import Flask, request, session, redirect, url_for
from functools import wraps

app = None
db = None

AUTH_OK = 0x0
AUTH_FAILED = 0x1
AUHT_USER_UNKNOWN = 0x2
AUTH_USER_DISABLED = 0x3

def CheckSession():
	"Check session worker"
	if 'session' in session:
		return True
	else:
		return False

def LogOut():
	"Clear all session data"
	session.clear()

def CheckAuth(decorated = None):
	"Check auth function and decorator"
	if decorated is None:
		return CheckSession()
	@wraps(decorated)
	def wrapper(*args, **kwargs):
		if CheckSession() is not True:
			return redirect(url_for('login'), code=302)
		return decorated(*args, **kwargs)
	return wrapper

def __gen_session():
	"Generate session string"
	import uuid
	return uuid.uuid4().hex

def Authenticate(username, password):
	"Lookup username and auth method. Do also internal or plugin auth"
	user = db.session.execute("select \
		user_id \
	,	username \
	,	password \
	,	user_enabled \
	,	auth_externally \
	,	auth_by_url \
	from \
		cw_users \
	where \
		username = :username", {'username':username}).fetchone()
	if user is None:
		time.sleep(2) #TODO more denial friendly
		return AUHT_USER_UNKNOWN, 'User %s was not found' % username

	if user['auth_externally'] and len(user['auth_by_url']) > 0:
		app.logger.debug('%s has auth externally enabled: %s' % (user['username'], user['auth_by_url']))
		return __auth_by_url(user['auth_by_url'], user['username'], password)
	else:
		app.logger.debug('%s has auth internal enabled: %s' % (user['username'], user['auth_by_url']))
		return __auth_internal(dbpassword_string, username, password)

def __auth_by_url(url, username, password):
	"Authenticate by url, username and password when auth_by_url is true"
	from urllib.parse import urlparse
	import importlib, re

	o = urlparse(url)
	pluginname = re.sub('[^0-9a-zA-Z]+', '', o.scheme)
	plugin = importlib.import_module('citywok_frontend.auth.%s' % pluginname)
	plugin.url = o
	plugin.debug = None
	result, message = plugin.Authenticate(username, password)

	#auth ok
	if result == AUTH_OK:
		session['session'] = __gen_session()
		session['username'] = username
	else:
		time.sleep(2) #TODO more denial friendly

	try:
		if plugin.debug is not None: app.logger.debug(plugin.debug)
	except:
		pass
	return result, message

def __auth_internal(hashed_password, username, password):
	"Internal authentication {method}hash"
	try:
		import re,hashlib
		match = re.match('^\{([a-z0-9]*)\}(.*)', hashed_password, re.I)
		if match is None:
			raise AuthError('password string is not valid')
		method = match.group(1).lower()
		dbpassword = match.group(2)
		m = getattr(hashlib, method)()
		m.update(bytes(password.encode()))
		if m.hexdigest() == dbpassword:
			return AUTH_OK, "user %s logged in" % username
		raise Exception('password failed')
	except:
		return AUTH_FAILED, str(sys.exc_info()[1])

