__version__ = 1.0
__author__ = "Rene Dekkers"
app = None

import sys
from flask import Blueprint, make_response, render_template, request
import requests
from citywok_frontend.pluginloader import Menu, MenuItem

plugin = Blueprint('jenkins', __name__, template_folder='templates')

menu = Menu('',
	Menu('Jenkins',
		MenuItem(icon = 'th-list', text = 'Job overview', url = 'jenkins.index'),
		MenuItem(icon = 'th-list', text = 'Run Job', url = 'jenkins.generate_form', url_args={'job':'Deploy virtual'}),
	),
	Menu('Jenkins2'),
)

class JobNotFound(Exception): pass

def get_jenkins_url():
	return config['URL']

__crumb = None
def get_jenkins_crumb():
	global __crumb
	if __crumb is None:
		req_url = get_jenkins_url() + '/crumbIssuer/api/json'
		json = requests.get(req_url).json()
		__crumb = {json['crumbRequestField'] : json['crumb']}
	return __crumb

def get_jobconfig_from_jenkins(job):
	try:
		from lxml import etree
		import traceback
		import pprint

		rtrn = {
			'fields': []
		}
		req_url = get_jenkins_url() + "/job/%s/config.xml" % job
		app.logger.debug("GET url: %s" % req_url)

		result = requests.get(req_url)
		if result.status_code == 404:
			raise JobNotFound("%s is not defined as a jenkins job." % job)
		elif result.status_code != 200:
			raise Exception("get status %d" % result.status_code)
		root = etree.fromstring(result.content)

		#parse description
		rtrn['description'] = str(root.xpath('/project/description/text()')[0])

		#parse parameters
		definitions = root.xpath('/project/properties/hudson.model.ParametersDefinitionProperty/parameterDefinitions')
		if len(definitions) < 1:
			raise Exception("could not find project->properties->hudson.model.ParametersDefinitionProperty->parameterDefinitions")
		for parameter in definitions[0].getchildren():
			rtrn['fields'].append(extract_parameter_values(parameter))

		app.logger.debug("Fields extracted from XML:\n%s" % pprint.pformat(rtrn['fields']))
		return rtrn
	except JobNotFound:
		raise
	except:
		app.logger.error("Failed to get form parameters.\n%s\n%s" % (str(sys.exc_info()[1]), traceback.format_exc()))
		raise Exception("Failed to get form parameters. %s" % str(sys.exc_info()[1]))

def extract_parameter_values(parameter):
	"Extract parameter from XML and return a dict ready for our template"
	if parameter.tag == 'hudson.model.StringParameterDefinition':
		return {
			'type' : 'text',
			'name' : str(parameter.xpath('./name/text()')[0]),
			'description' : str(parameter.xpath('./description/text()')[0]),
			'value' : ''.join(parameter.xpath('./defaultValue/text()')),
		}
	if parameter.tag == 'hudson.model.PasswordParameterDefinition':
		return {
			'type' : 'password',
			'name' : str(parameter.xpath('./name/text()')[0]),
			'description' : str(parameter.xpath('./description/text()')[0]),
			'value' : '',
		}
	elif parameter.tag == 'hudson.model.TextParameterDefinition':
		return {
			'type': 'textarea',
			'name' : str(parameter.xpath('./name/text()')[0]),
			'description' : str(parameter.xpath('./description/text()')[0]),
			'value' : ''.join(parameter.xpath('./defaultValue/text()')),
		}
	elif parameter.tag == 'hudson.model.ChoiceParameterDefinition':
		items = parameter.xpath('./choices/a/string')
		return {
			'type': 'select',
			'name' : str(parameter.xpath('./name/text()')[0]),
			'description' : str(parameter.xpath('./description/text()')[0]),
			'value' : ''.join(parameter.xpath('./defaultValue/text()')),
			'items' : [x.text for x in parameter.xpath('./choices/a/string')]
		}
	elif parameter.tag.endswith('.dynamicparameter.ChoiceParameterDefinition'):
		#execute groovy script
		script = str(parameter.xpath('./__script/text()')[0])
		data = {'script':script}
		result = requests.post(get_jenkins_url() + '/scriptText', data = data, headers = get_jenkins_crumb())

		return {
			'type': 'select',
			'name' : str(parameter.xpath('./name/text()')[0]),
			'description' : str(parameter.xpath('./description/text()')[0]),
			'value' : ''.join(parameter.xpath('./defaultValue/text()')),
			'items' : parse_groovy_list(result.text.strip('Result: '))
		}
	else:
		app.logger.error("Parameter type %s not supported" % parameter)

def parse_groovy_list(value):
	return [x.strip() for x in value.strip()[1:-1].split(",")]


def get_last_build():
	try:
		req_url = get_jenkins_url() + "/job/%s/lastBuild/api/json?depth=1" % job
		result = requests.get(req_url)
		
	except:
		app.logger.error("Failed to get last build: %s" % str(sys.exc_info()[1]))
		return False

@plugin.route('/', methods=['GET'])
@plugin.route('/overview', methods=['GET'])
def index():
	return ''

@plugin.route('/generate_form/<string:job>', methods=['GET','POST'])
def generate_form(job):
	try:
		import json, pprint

		#Get job config
		config = get_jobconfig_from_jenkins(job)

		if request.method == 'POST':
			parameters = []
			#Set default values
			for k,v in request.form.items():
				try:
					for f in config['fields']:
						if f['name'] != k: continue
						f['value'] = v
						#parameters.append({"name": k, "value": v})
						break
				except:
					pass
			#Fill parameters list
			for f in config['fields']:
				name = f['name']
				value = request.form[name] if name in request.form else None
				parameters.append({"name": name, "value": value})

			app.logger.debug("Values to post to jenkins:\n%s" % pprint.pformat(parameters))
			data = {'json' : json.dumps({'parameter': parameters})}
			result = requests.post(
				'/'.join([
					get_jenkins_url(),
					'job',
					job,
					'build'
				]),
				data = data,
				headers = get_jenkins_crumb()
			)
			if result.status_code not in [200,201]:
				app.logger.error("Error while posting data to jenkins: %s" % result.text)
				raise Exception("Could not commit job to jenkins (status %d).\nPlease check /var/log/jenkins/jenkins.log." % result.status_code)

			return make_response(render_template(
				'generate_form.html',
				job = job,
				description = config['description'],
				fields = config['fields'],
				message = "Buildjob for project '%s' added to your jenkins environment." % job,
				form_disable = True,
			))
		else:
			return make_response(render_template(
				'generate_form.html',
				job = job,
				description = config['description'],
				fields = config['fields'],
			))
	except JobNotFound:
		return make_response(render_template(
			'generate_form.html',
			job = job + '?',
			error=str(sys.exc_info()[1])
		))
	except:
		return make_response(render_template(
			'generate_form.html',
			job = job,
			description = config['description'],
			fields = config['fields'],
			error = str(sys.exc_info()[1]),
		))
