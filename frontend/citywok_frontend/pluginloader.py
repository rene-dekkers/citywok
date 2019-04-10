class MenuItem():
	"Plugin provided menu item"
	__supported_attributes = ['icon','text','url','url_args']

	def __init__(self, **kwargs):
		for k,v in kwargs.items():
			if k not in self.__supported_attributes:
				raise ValueError("Attribute %s is not supported (%s)" % (k, ','.join(self.__supported_attributes)))
			setattr(self, k, v)

	def __repr__(self):
		return "%s(%s)" % (self.__class__, self.text)


class Menu(object):
	"Collection of menuitems"
	__name = None
	__items = []
	def __init__(self, name, *items):
		self.__name = name
		for i in items:
			self.AddItem(i)

	def __repr__(self):
		return "%s(%s)" % (self.__class__, self.name)

	def AddItem(self, item):
		if isinstance(item , Menu) is not True and isinstance(item, MenuItem) is not True:
			raise TypeError("Item %s is not a Menu or MenuItem object" % type(item))
		self.__items.append(item)
		return self

	@property
	def name(self):
		return self.__name

	@property
	def items(self):
		return self.__items

	def Show(self):
		r = []
		r.append("Lvl #1: " + self.name)
		for i in self.items:
			if isinstance(i, Menu):
				r.append("  Menu: " + i.name)
			else:
				r.append("    Item: " + i.text)
		return '\n'.join(r)


def GetPluginConfig(plugin, config):
	"Load all PLUGIN_xx config options into plugin.config variable. Strip PLUGIN_ from options, so PLUGIN_apikey=xx will be apikey=xx inside plugin"
	return {x[len(plugin) + 1:] : y for x,y in config.items() if x.startswith(plugin.upper() + '_')}

def Load(app):
	"Import all files in /plugins and set default variables (app, config)"
	import os
	from flask.blueprints import Blueprint

	plugins = IncludePluginDirectory(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'plugins'))
	for name, attributes in plugins.items():
		attributes['source'].app = app
		attributes['source'].config = GetPluginConfig(name, app.config)
		for blueprnt in [name for name, value in attributes['source'].__dict__.items() if isinstance(value, Blueprint)]:
			app.register_blueprint(
				getattr(attributes['source'], blueprnt),
				url_prefix = '/plugins/%s' % name
			)
			app.logger.debug("Registered %s.%s as blueprint" % (name, blueprnt))
		if hasattr(attributes['source'], 'Load') and callable(attributes['source'].Load):
			attributes['source'].Load()


#		try:
#			attributes['menu'] = [value for name, value in attributes['source'].__dict__.items() if isinstance(value, Menu)][0]
#			for mnu in [value for name, value in attributes['source'].__dict__.items() if isinstance(value, Menu)]:
#				print(mnu)
#		except:
#			raise
	return plugins

#from pprint import pprint
def GetMenulistFromPlugins(plugins):
	"Return a list of menu's from plugins dict"
	r = Menu('container')
	try:
		for menu in [plugin['menu'] for name, plugin in plugins.items() if isinstance(plugin['menu'], Menu)]:
			r.AddItem(menu)
	except:
		pass
	return r

def IncludePluginDirectory(directory):
	"Load __init__.py from all directories. Return a list with dicts."
	import imp, sys, os, traceback
	r = {}
	if os.path.exists(directory) is True:
		plugins = [
			os.path.join(directory, f) for f in os.listdir(directory)
			if os.path.isdir(os.path.join(directory, f))
			and f.startswith('_') is not True
			and f.endswith('~') is not True
		]
		for i in plugins:
			try:
				name = os.path.basename(i)
				initpy = os.path.join(i, '__init__.py')
				r[name] = {'source':imp.load_source(name, initpy)}
			except:
				raise
	import collections
	return collections.OrderedDict(sorted(r.items()))
