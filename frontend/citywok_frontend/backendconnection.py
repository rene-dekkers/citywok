__version__ = 0.01
import requests
from citywok_frontend.exception import ConnectionError

class BackendConnections(object):
	def __init__(self, backends):
		if type(backends) != type(list()):
			raise Exception('Please specify all backends as a list')
		self.__backends = [BackendConnection(x) for x in backends]

	def get_all_virtuals(self):
		r = []
		for b in self.__backends:
			try:
				r = r + b.get_virtuals()
			except:
				pass
		return r

	def search(self, virtual):
		for b in self.__backends:
			if b.in_index(virtual):
				return b
		raise Exception("Virtual '%s' was not found" % virtual)

#	def __getattr__(self, name):
#TODO security check
#		"Wrap all (unknown) methods to the right backend connection. The first argument *has* to be a virtual name!"
#		def method(*args, **kwargs):
#			for b in self.__backends:
#				if b.in_index(args[0]):
#					print('return connection %s.%s for virtual %s' % (b, name, args[0]))
#					return getattr(b, name)(*args, **kwargs)
#		return method

#TODO reload, sync time etc
class BackendConnection(object):
	__url = None
	__params = {}
	__apikey = None
	__hypervisor = None

	__index = False

	def __init__(self, url):
		"Cached list with virtuals"
		from urllib.parse import urlparse, parse_qsl
		urlobj = urlparse(url)
		params = dict(parse_qsl(urlobj.params))
		
		if urlobj.scheme == '' or urlobj.netloc == '':
			raise ConnectionError("Url %s is not correct!" % url)

		self.__url = '%s://%s' % (urlobj.scheme.rstrip('/'), urlobj.netloc)
		self.__params = dict(parse_qsl(urlobj.params))
		try:
			self.__apikey = self.__params['apikey']
		except:
			raise ConnectionError("Please provide a ;apikey= in your backend url!")

	def __build_url(self, url):
#TODO build args!
		"Join backend with string or list items"
		if type(url) != type(list()):
			return '/'.join([self.__url] + [url])
		else:
			return '/'.join([self.__url] + url)

	def request(self, req, url, *args, **kwargs):
		"requests Wrapper to provide a simple software abstraction"
		method = getattr(requests, req)
		if 'headers' not in kwargs: kwargs['headers'] = {}
		kwargs['headers']['X-Apikey'] = self.__apikey
		url = self.__build_url(url)
		return method(url, *args, **kwargs)

	@property
	def url(self):
		"Read-only url property"
		return self.__url

	def get_hypervisor(self):
		"Load hypervisor data into var and get return"
		self.__hypervisor = self.request('get', '%s/hypervisor' % self.__url).json()
		return self.__hypervisor

	def load_index(self, force=False):
		"Reload index of virtuals"
		if force or self.__index is False:
			self.__index = self.request('get', 'virtual').json()['virtuals']

	def in_index(self, virtual):
		"Is virtual in index ?"
		try:
			if self.__index is False: self.load_index()
			return virtual in self.__index
		except:
			return False

	def get_virtual(self, virtual):
		"Get details of a virtual"
		self.load_index()
		if self.in_index(virtual) is not True: return None
		return self.request('get', ['virtual',virtual]).json()['virtual']

	def get_virtuals(self):
		"Method to get all details of all virtuals"
		r = []
		self.load_index(True)
		for v in self.__index:
			r.append(self.request('get', ['virtual',v]).json()['virtual'])
		return r

	def get_virtual_screenshot(self, virtual, **kwargs):
#TODO running?
#TODO build args
		self.load_index()
		if self.in_index(virtual) is not True: return None

		if 'size' in kwargs: cmd='screenshot?size=' + 'x'.join(kwargs['size'])
		else: cmd='screenshot'

		response = self.request('get', ['virtual',virtual,cmd])
		if response.status_code != 200:
			return False
		else:
			return response.content.decode()

	def create_token(self, virtual):
		self.load_index()
		if self.in_index(virtual) is not True: return None

		response = self.request('post', ['token',virtual])
		if response.status_code == 200:
			return response.json()
		else:
			return False
