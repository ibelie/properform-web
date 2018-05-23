#-*- coding: utf-8 -*-

from tarantula import route, response

@route
def helloworld(cookies, param1, param2):
	return response(helloworld = int(param1) + int(param2))
