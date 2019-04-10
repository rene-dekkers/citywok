#!/usr/bin/python3
if __name__ == '__main__':
	import citywok_frontend
	try:
		host = citywok_frontend.app.config['HOST'] if 'HOST' in citywok_frontend.app.config else '127.0.0.1'
		port = int(citywok_frontend.app.config['PORT']) if 'PORT' in citywok_frontend.app.config else 8080
	except:
		raise Exception("Please define host and port in your settings file (eg '127.0.0.1' and 8080)")

	debug = citywok_frontend.app.config['DEBUG']
	threaded = citywok_frontend.app.config['THREADED']

	citywok_frontend.app.logger.info("Start citywok on %s:%d. [ debug = %s, threaded = %s ]" % (host, port, debug, threaded)) 

	citywok_frontend.app.run(
		host = host,
		port = port,
		debug = debug,
		threaded = threaded,
	)
