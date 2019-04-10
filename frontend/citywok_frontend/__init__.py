"""
CityWok HTML GUI / json REST frontend

Goal:
- Communicate with one or more CityWok libvirt backends
- Provide GUI for administrators
- Provide REST interface for advanced administrators
"""
__version__ = 0.01
__author__ = 'Rene Dekkers'
__url__ = 'https://git.better-it-solutions.nl/virtualization/citywok'

import sys
from flask import Flask, g, session, request
from flask_babel import Babel, gettext
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

from pprint import pprint, pformat

app = Flask(__name__)
try:
	from os import environ as env
	if 'HOST' in env and 'PORT' in env:
		app.config.from_pyfile('settings-docker.ini')
		app.logger.info('Config parsed from environment settings file')
	else:
		raise Exception()
except:
	app.config.from_pyfile('settings.ini')
	app.logger.info('Config parsed from settings.ini')

babel = Babel(app)
_ = gettext

import citywok_frontend.backendconnection
connection = backendconnection.BackendConnections(app.config['BACKEND'])

db = SQLAlchemy(app)
app.logger.info('Connected to database: %s' % db)

Session(app)
app.session_interface.db.create_all()

import citywok_frontend.auth
auth.db = db
auth.app = app

import citywok_frontend.filterloader
filterloader.jinja = app.jinja_env
filterloader.Load()

from citywok_frontend import pluginloader
plugins = pluginloader.Load(app)
menu = pluginloader.GetMenulistFromPlugins(plugins)

@app.before_request
def update_globals():
	app.jinja_env.globals['version'] = __version__
	app.jinja_env.globals['pprint'] = pformat
	g.version = __version__
	g.lang = get_locale()
	g.menu = menu

@babel.localeselector
def get_locale():
	# if a user is logged in, use the locale from the user settings
	locale = session.get('locale')
	if locale is not None:
		return locale
	# otherwise try to guess the language from the user accept
	# header the browser transmits.  We support de/fr/en in this
	# example.  The best match wins.
	return request.accept_languages.best_match(app.config['LANGUAGES'])

from citywok_frontend import views
