#-*- coding: utf-8 -*-

from server import route

@route
def helloworld(param1, param2):
	return {'helloworld': int(param1) + int(param2)}
