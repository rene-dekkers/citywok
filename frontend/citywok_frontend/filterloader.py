jinja = None
def FilterModule():
	"Mark a function as a jinja filter by this decorator"
	def decorator(decorated):
		__add_to_jinja(decorated.__name__, decorated)
	return decorator

def Load():
	"Load all py files from filters directory"
	import os
	IncludeFilterDirectory(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'filters'))

def IncludeFilterDirectory(directory):
	"Load all py files from a directory"
	import imp
	import os
	for i in [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.startswith('.') is not True and f.endswith('.py')]:
		imp.load_source('', i)

def __add_to_jinja(name, payload):
	"Add filter to jinja"
	global jinja
	jinja.filters.update({name:payload})
