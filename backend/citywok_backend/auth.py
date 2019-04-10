from flask import request
from functools import wraps
from citywok_backend.exception import ApiException

app = None

def CheckApikey():
	if 'X-Apikey' in request.headers and request.headers['X-Apikey'] in app.config['APIKEY']:
		return True
	else:
		return False

def CheckAuth(decorated = None):
	"Check auth function and decorator"
	if decorated is None:
		return CheckApikey()
	@wraps(decorated)
	def wrapper(*args, **kwargs):
		if CheckApikey() is not True:
			raise ApiException("Apikey not OK", 403)
		return decorated(*args, **kwargs)
	return wrapper
