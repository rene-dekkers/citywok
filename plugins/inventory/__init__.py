__version__ = 1.0
__author__ = "Rene Dekkers"
app = None

import sys
from flask import g, Blueprint, make_response, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

plugin = Blueprint('inventory', __name__, template_folder='templates')
plugin.config = {'SQLALCHEMY_DATABASE_URI':'testje'}

db = None

@plugin.teardown_request
def teardown_request(exception):
	if exception:
		db.session.rollback()
		db.session.remove()
	db.session.remove()


def Load():
	global db

	plugin.config = config
	plugin.debug = app.debug

	plugin.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
	plugin.config['SQLALCHEMY_POOL_SIZE'] = 5
	plugin.config['SQLALCHEMY_POOL_TIMEOUT'] = 10
	plugin.config['SQLALCHEMY_POOL_RECYCLE'] = 3600

	db = SQLAlchemy(plugin)
	db.prefix = config.get('DBPREFIX','')

def handle_db_error(template):
	def decorator(func):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except exc.ProgrammingError:
				return make_response(render_template(template, error=str(sys.exc_info()[1])))
		return wrapper
	return decorator

@handle_db_error('hosts.html')
@plugin.route('/host/', methods=['GET'])
@plugin.route('/host/<string:host>', methods=['GET'])
def host(host = None):
	if host is None:
		hosts = db.session.execute("""select
				host_name
			,	host_address
			,	host_vars
			from
				%shosts
			order by
				host_name""" % db.prefix).fetchall()
		return make_response(render_template(
			'hosts.html',
			hosts = hosts
		))
	else:
		host = db.session.execute("""select
				host_name
			,	host_address
			,	host_vars
			from
				%shosts
			where
				host_name = :host""" % db.prefix, {'host': host}).fetchone()
		return make_response(render_template(
			'host.html',
			host = host
		))
