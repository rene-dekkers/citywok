__version__ = 0.01
log = None
from citywok_backend.exception import ApiException
from citywok_backend.prepost import pre_post_actions
import sys
import libvirt

class LibvirtConnection(object):
	"Connection class. Communicate with libvirtd"
	__uri = None
	__conn = None

	def __init__(self, uri = None):
		"Libvirt contructor"
		if uri is None: self.__uri = 'qemu:///system'
		else: self.__uri = uri
		self.__conn = LibvirtConnection.__get_connection(self.__uri)

	@staticmethod
	def __get_connection(uri):
		"Get libvirt connection wrapper (for poll and reload purpose)"
		try:
			return libvirt.open(uri)
		except:
			raise ConnectionError(str(sys.exc_info()[1]), 500)

	def poll(self):
		"Poll method to make sure connection is alive"
		try:
			if self.__conn.isAlive():
				print('poll ok')
		except:
			self.__conn = __get_connection(self.__uri)

	def get_hypervisor(self):
		"Return dict with hypervisor information"
		info = self.__conn.getInfo()
		mem = self.__conn.getMemoryStats(0,0)
		if mem is None:
			mem = {'total':info[1]*1024**2, 'free' : LibvirtConnection.__getfreememory(self.__conn)}
		else:
			mem['total'] = mem['total'] * 1024
			mem['free'] = mem['free'] * 1024

		return {
			'hostname' : self.__conn.getHostname()
		,	'version' : self.__conn.getVersion()
		,	'maxvcpus' : self.__conn.getMaxVcpus(self.__conn.getType())
		,	'type' : self.__conn.getType()
		,	'cpustats' : self.__conn.getCPUStats(0,0)
		,	'arch' : info[0]
		,	'num_cpu' : info[2]
		,	'cpumhz' : info[3]
		,	'num_sockets' : info[5]
		,	'num_cores' : info[6]
		,	'num_threads' : info[7]
		,	'memorystats' : mem
		}

	@staticmethod
	def __getfreememory(connection):
		if connection.getType().lower() == 'xen':
			return ((connection.getFreeMemory()/1024) + (connection.lookupByID(0).info()[2])) * 1024
		else:
			connection.getFreeMemory()

	def __get_virtual(self, virtual):
		"Get libvirt.virDomain objec by virtual name"
		v = [x for x in self.__conn.listAllDomains() if x.name() == virtual]
		if len(v) < 1: raise ApiException("Virtual '%s' was not found" % virtual, 404)
		return v[0]

	def get_virtual(self, virtual):
		"Get dict of information by virtual name"
		v = self.__get_virtual(virtual)
		return self.__virtual_to_dict(v)

	def get_virtuals(self):
		"Get a list with virtuals"
		return [str(x.name()) for x in self.__conn.listAllDomains()]

	def __virtual_to_dict(self, virtual):
		state, maxMem, memory, nrVirtCpu, CpuTime = virtual.info()
		return {
			'hypervisor' : self.__conn.getHostname()
		,	'name' : virtual.name()
		,	'state' : LibvirtConnection.__get_virtual_state(state)
		,	'maxmem' : maxMem*1024
		,	'memory' : memory*1024
		,	'nrvirtcpu' : nrVirtCpu
		,	'cputime' : CpuTime
		,	'isactive' : virtual.isActive()
		}

	@staticmethod
	def __get_virtual_state(state):
		try:
			states = {
				libvirt.VIR_DOMAIN_NOSTATE : 'nostate'
			,       libvirt.VIR_DOMAIN_RUNNING : 'running'
			,       libvirt.VIR_DOMAIN_BLOCKED : 'blocked'
			,       libvirt.VIR_DOMAIN_PAUSED : 'paused'
			,       libvirt.VIR_DOMAIN_SHUTDOWN : 'shutdown'
			,       libvirt.VIR_DOMAIN_SHUTOFF : 'shutoff'
			,       libvirt.VIR_DOMAIN_CRASHED : 'crashed'
			,       libvirt.VIR_DOMAIN_PMSUSPENDED : 'suspended'
			}
			return states[state]
		except:
			return 'nostate'

	def screenshot(self, virtual, screen_id = 0, size = ()):
		"Make screenshot of screen X"
		try:
			try:
				if type(size[0]) != type(int()) or type(size[1]) != type(int()): raise Exception()
				if size[0] < 0 or size[1] < 0: raise Exception()
				if size[0] > 2000 or size[1] > 2000: raise Exception()
			except:
				raise ApiException("Specify screenhost size as (200,100) with a max of 2000")
			from io import BytesIO
			from PIL import Image
			import base64

			virtual = self.__get_virtual(virtual)

			#take screenshot & save to buffer
			stream = self.__conn.newStream(0)
			rawbuf = BytesIO()
			pngbuf = BytesIO()
			virtual.screenshot(stream, screen_id, 0)
			stream.recvAll(LibvirtConnection.__streamwriter, rawbuf)
			stream.finish()
			#pxl to png
			rawbuf.seek(0)
			image = Image.open(rawbuf)
			if 0 in size:
				try:
					if size[0] == 0: image.thumbnail((size[1] * 0.9, size[1]), Image.ANTIALIAS)
					if size[1] == 0: image.thumbnail((size[0], size[0] * 0.9), Image.ANTIALIAS)
				except: pass
			else:
				try: image = image.resize(size, Image.ANTIALIAS)
				except: pass
			image.save(pngbuf, format="png")

			return base64.b64encode(pngbuf.getvalue()).decode()
		except:
			raise
		finally:
			try:
				del(stream)
				del(rawbuf)
				del(image)
			except: pass

	@staticmethod
	def __streamwriter(stream, data, buffer):
		buffer.write(data)

	#TODO pacemaker action required?
	@pre_post_actions
	def create(self, virtual):
		try:
			virtual = self.__get_virtual(virtual)
			if LibvirtConnection.__get_virtual_state(virtual.info()[0]) not in ['shutdown','shutoff']:
				raise ApiException("Virtual '%s' is not powered off" % virtual.name())
			virtual.create()
		except ApiException:
			raise
		except:
			raise ApiException(str(sys.exc_info()[1]))

	def reboot(self, virtual):
		try:
			virtual = self.__get_virtual(virtual)
			if LibvirtConnection.__get_virtual_state(virtual.info()[0]) == 'shutoff':
				raise ApiException("Virtual '%s' is not powered on" % virtual.name())
			virtual.reboot(0)
		except ApiException:
			raise
		except:
			raise ApiException(str(sys.exc_info()[1]))
	@pre_post_actions
	def shutdown(self, virtual):
		try:
			virtual = self.__get_virtual(virtual)
			if LibvirtConnection.__get_virtual_state(virtual.info()[0]) == 'shutoff':
				raise ApiException("Virtual '%s' is not powered on" % virtual.name())
			virtual.shutdown()
		except ApiException:
			raise
		except:
			raise ApiException(str(sys.exc_info()[1]))

	def reset(self, virtual):
		try:
			virtual = self.__get_virtual(virtual)
			if LibvirtConnection.__get_virtual_state(virtual.info()[0]) == 'shutoff':
				raise ApiException("Virtual '%s' is not powered on" % virtual.name())
			virtual.reset(0)
		except ApiException:
			raise
		except:
			raise ApiException(str(sys.exc_info()[1]))

	def destroy(self, virtual):
		try:
			virtual = self.__get_virtual(virtual)
			if LibvirtConnection.__get_virtual_state(virtual.info()[0]) == 'shutoff':
				raise ApiException("Virtual '%s' is not powered on" % virtual.name())
			virtual.destroy()
		except ApiException:
			raise
		except:
			raise ApiException(str(sys.exc_info()[1]))

	def suspend(self, virtual):
		try:
			virtual = self.__get_virtual(virtual)
			if LibvirtConnection.__get_virtual_state(virtual.info()[0]) != 'running':
				raise ApiException("Virtual '%s' is not running" % virtual.name())
			virtual.suspend()
		except ApiException:
			raise
		except:
			raise ApiException(str(sys.exc_info()[1]))

	def resume(self, virtual):
		try:
			virtual = self.__get_virtual(virtual)
			if LibvirtConnection.__get_virtual_state(virtual.info()[0]) != 'paused':
				raise ApiException("Virtual '%s' is not paused" % virtual.name())
			virtual.resume()
		except ApiException:
			raise
		except:
			raise ApiException(str(sys.exc_info()[1]))

	def get_virtual_infobyxmlpath(self, virtual, path):
		from xml.etree import ElementTree as ET
		virtual = self.__get_virtual(virtual)
		state = LibvirtConnection.__get_virtual_state(virtual.info()[0])
		xmlstr = virtual.XMLDesc(0)
		root = ET.fromstring(xmlstr)
		return root.find(path)
