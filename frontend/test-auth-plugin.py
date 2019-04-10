#!/usr/bin/python3
def test(pluginname, username, password, url):
	from urllib.parse import urlparse
	import importlib
	try:
		plugin = importlib.import_module('citywok_frontend.auth.%s' % pluginname)
	except:
		raise Exception('Unknown plugin %s. Please add file citywok_frontend/auth/%s.py' % (pluginname, pluginname))
	plugin.url = urlparse(url)
	result, message = plugin.Authenticate(username, password)
	from citywok_frontend import auth
	if auth.AUTH_OK == result:
		print("AUTH_OK")
	elif auth.AUTH_FAILED == result:
		print("AUTH_FAILED")
	print("Message: ->%s<-" % message)

if __name__ == '__main__':
	import sys, getpass, importlib
	try:
		pluginname = sys.argv[1]
		username = sys.argv[2]
		url = sys.argv[3]
	except:
		print('Usage: %s <plugin> <username> <url>' % sys.argv[0])
		sys.exit(2)

	password = getpass.getpass(prompt = 'Password: ')
	test(pluginname, username, password, url)
