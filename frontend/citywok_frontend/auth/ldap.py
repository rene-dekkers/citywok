#ParseResult(scheme='ldap', netloc='ldap.qdata.nl', path='/ou=Users,dc=qdata,dc=local', params='', query='', fragment='')
import sys
from citywok_frontend import auth
from ldap3.core.exceptions import LDAPInvalidCredentialsResult
from ldap3 import Server, Connection, SIMPLE
url = None

def Authenticate(username, password):
	global url
	global debug
	try:
		s = Server(host=url.netloc)
		dn = 'uid=%s,%s' % (username, url.path[1:])
		c = Connection(s, authentication=SIMPLE, user=dn, password=password, raise_exceptions=True)
		c.open()
		c.bind()
		return auth.AUTH_OK, "User %s logged in" % username
	except LDAPInvalidCredentialsResult:
		debug = 'password failed'
		return auth.AUTH_FAILED, 'password failed'
	except:
		return auth.AUTH_FAILED, str(sys.exc_info()[1])
	finally:
		try: c.unbind()
		except: pass
	
