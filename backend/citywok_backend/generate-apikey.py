#!/usr/bin/python3
import os, re, uuid

def main():
	settings = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.ini')
	with open(settings, "r+") as file:
		for line in file:
			if re.search(r'^APIKEY\=.*$',line) is not None:
				print('Key already found!')
				break
		else:
			file.write("""APIKEY=['%s']""" % uuid.uuid4().hex)

if __name__ == '__main__':
	main()

