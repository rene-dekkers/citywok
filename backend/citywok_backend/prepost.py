import os, re, subprocess
def __prepost_directory(script_type):
	path = os.path.join('/etc','citywok',script_type) 
	if os.path.exists(path):
		return path
	else:
		return False

def __get_scripts(script_type, action):
	path = __prepost_directory(script_type)
	if path is False: return
	scripts = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and re.sub(r'[0-9]{1,}\-([a-z]*)','\\1', f) == action]
	if len(scripts) < 1: return

def __run_scripts(script_type, action, *args, **kwargs):
#TODO rechten check!
	files = __get_scripts(script_type, action)
	if files is None: return
	#push args and kwargs to environment vars
	env = {}
	for i in range(1, len(args[1:])+1):
		env['ARG_%d' % i] = args[i]
	for k,v in kwargs:
		env['KWARG_%s' % k] = v
	for script in files:
		print('Run script %s' % script)
		p = subprocess.Popen(script, env = env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output = p.communicate()
		if p.returncode != 0:
			print(output[1].decode())
			raise Exception(output[1].decode())

def pre_post_actions(func):
	def wrapper(*args, **kwargs):
		__run_scripts('pre.d', func.__name__, *args, **kwargs)
		if __get_scripts('instead.d', func.__name__) is not None:
			__run_scripts('instead.d', func.__name__, *args, **kwargs)
		else:
			func(*args, **kwargs)
		__run_scripts('post.d', func.__name__, *args, **kwargs)
	return wrapper

