#!/usr/bin/env python3
if __name__ == '__main__':
	import citywok_backend
	try:
		host = citywok_backend.app.config['HOST'] if 'HOST' in citywok_backend.app.config else '127.0.0.1'
		port = int(citywok_backend.app.config['PORT']) if 'PORT' in citywok_backend.app.config else 8080
	except:
		raise Exception("Please define host and port in your settings file (eg '127.0.0.1' and 8080)")
	citywok_backend.app.run(debug = citywok_backend.app.config['DEBUG'], port = port, host = host)

