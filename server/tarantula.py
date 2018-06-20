#-*- coding: utf-8 -*-
# Copyright 2017 - 2018 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

from __future__ import print_function

__author__ = 'Joungtao'
__version__ = '0.1.1'
__all__ = ['TarantulaHTTPRequestHandler', 'serve']

import re
import os
import imp
import sys
import json
import codecs
import signal
import warnings
import mimetypes
import posixpath
import traceback
import threading

from functools import wraps

if sys.version_info[0] == 3:
	from urllib import parse as urlparse
	from http import server as BaseHTTPServer
	from http.cookies import SimpleCookie
	import socketserver as SocketServer
else:
	import urlparse
	import BaseHTTPServer
	import SocketServer
	from Cookie import SimpleCookie

try:
	import syslog
	def openlog(name): syslog.openlog('Tarantula[%s]' % name, syslog.LOG_PID)
	def log(text): syslog.syslog(text)
except:
	def openlog(name): pass
	def log(text): print(text)

def exec_delegate(code, globals):
	exec(code, globals)

# ooooooooo.                             .
# `888   `Y88.                         .o8
#  888   .d88'  .ooooo.  oooo  oooo  .o888oo  .ooooo.
#  888ooo88P'  d88' `88b `888  `888    888   d88' `88b
#  888`88b.    888   888  888   888    888   888ooo888
#  888  `88b.  888   888  888   888    888 . 888
# o888o  o888o `Y8bod8P'  `V88V"V8P'   "888" `Y8bod8P'
#
TEMPLATE_EXT = '.py.html'

ROUTE_RESPONSE = 0
ROUTE_REDIRECT = 1

def cookie(**args):
	return SimpleCookie(args)

def response(cookie = None, **args):
	return ROUTE_RESPONSE, cookie, args

def redirect(path, cookie = None, **args):
	return ROUTE_REDIRECT, cookie, (path, args)

def route(path):
	if callable(path):
		func = path
		func.____template__ = None
		func.____isRoute__ = True
		return func

	assert path.endswith(TEMPLATE_EXT), 'template "%s" should ends with "%s"!' % (path, TEMPLATE_EXT)

	def _route(func):
		if not path.startswith('/'):
			func.____template__ = '/%s/%s' % (func.__module__.rpartition('.')[-1], path)
		else:
			func.____template__ = path
		func.____isRoute__ = True
		return func

	return _route


#       .o.       oooo
#      .888.      `888
#     .8"888.      888   .oooo.   oooo d8b ooo. .oo.  .oo.
#    .8' `888.     888  `P  )88b  `888""8P `888P"Y88bP"Y88b
#   .88ooo8888.    888   .oP"888   888      888   888   888
#  .8'     `888.   888  d8(  888   888      888   888   888
# o88o     o8888o o888o `Y888""8o d888b    o888o o888o o888o

class Alarm(object):
	def __init__(self, timeout, error):
		self.timeout = timeout
		self.timer = None
		self.error = error
		self.start()

	def start(self):
		if hasattr(signal, 'SIGALRM') and threading.currentThread().getName() == 'MainThread':
			def handler(signum, frame):
				raise RuntimeError(self.error)
			signal.signal(signal.SIGALRM, handler)
			signal.alarm(self.timeout)
		else:
			def handler(frame, event, arg):
				raise RuntimeError(self.error)

			def set_trace_for_frame_and_parents(frame, trace_func):
				# Note: this only really works if there's a tracing function set in this
				# thread (i.e.: sys.settrace or threading.settrace must have set the
				# function before)
				while frame:
					if frame.f_trace is None:
						frame.f_trace = trace_func
					frame = frame.f_back
				del frame

			def interrupt(thread):
				for thread_id, frame in sys._current_frames().items():
					if thread_id == thread.ident:
						set_trace_for_frame_and_parents(frame, handler)

			sys.settrace(lambda frame, event, arg: None)
			self.timer is not None and self.timer.cancel()
			self.timer = threading.Timer(self.timeout, interrupt, (threading.currentThread(), ))
			self.timer.start()

	def cancel(self):
		if hasattr(signal, 'alarm') and threading.currentThread().getName() == 'MainThread':
			signal.alarm(0)
		else:
			self.timer.cancel()
			self.timer = None

# ooooooooooooo                                              .               oooo
# 8'   888   `8                                            .o8               `888
#      888       .oooo.   oooo d8b  .oooo.   ooo. .oo.   .o888oo oooo  oooo   888   .oooo.
#      888      `P  )88b  `888""8P `P  )88b  `888P"Y88b    888   `888  `888   888  `P  )88b
#      888       .oP"888   888      .oP"888   888   888    888    888   888   888   .oP"888
#      888      d8(  888   888     d8(  888   888   888    888 .  888   888   888  d8(  888
#     o888o     `Y888""8o d888b    `Y888""8o o888o o888o   "888"  `V88V"V8P' o888o `Y888""8o
#
def TarantulaHTTPRequestHandler(debug, app_route, file_path, index_route, app_timeout, request_timeout, extra_types):
	class _TarantulaHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
		cache = {}
		modules = {}
		protocol_version = "HTTP/1.0"
		server_version = "TarantulaHTTP/" + __version__

		#       .o8                   .oooooo.    oooooooooooo ooooooooooooo
		#      "888                  d8P'  `Y8b   `888'     `8 8'   888   `8
		#  .oooo888   .ooooo.       888            888              888
		# d88' `888  d88' `88b      888            888oooo8         888
		# 888   888  888   888      888     ooooo  888    "         888
		# 888   888  888   888      `88.    .88'   888       o      888
		# `Y8bod88P" `Y8bod8P'       `Y8bood8P'   o888ooooood8     o888o
		#
		def do_GET(self):
			"""Serve a GET request."""
			_, _, path, query, _ = urlparse.urlsplit(self.path)
			if self.send_file(path, None):
				return
			elif self.handle_route(path, {k: v if len(v) > 1 else v[0]
				for k, v in urlparse.parse_qs(query).items()},
				SimpleCookie(self.headers.get('Cookie')), None):
				return
			log('[Handler] GET Error: %s' % self.path)

		#       .o8                 ooooooooo.     .oooooo.    .oooooo..o ooooooooooooo
		#      "888                 `888   `Y88.  d8P'  `Y8b  d8P'    `Y8 8'   888   `8
		#  .oooo888   .ooooo.        888   .d88' 888      888 Y88bo.           888
		# d88' `888  d88' `88b       888ooo88P'  888      888  `"Y8888o.       888
		# 888   888  888   888       888         888      888      `"Y88b      888
		# 888   888  888   888       888         `88b    d88' oo     .d8P      888
		# `Y8bod88P" `Y8bod8P'      o888o         `Y8bood8P'  8""88888P'      o888o
		#
		def do_POST(self):
			"""Serve a POST request."""
			# ignore parameters form URL
			_, _, path, _, _ = urlparse.urlsplit(self.path)
			if self.send_file(path, None):
				return

			try:
				# Get arguments by reading body of request.
				# We read this in chunks to avoid straining
				# socket.read(); around the 10 or 15Mb mark, some platforms
				# begin to have problems (bug #792570).
				max_chunk_size = 10*1024*1024
				size_remaining = int(self.headers['content-length'])
				L = []
				while size_remaining:
					chunk_size = min(size_remaining, max_chunk_size)
					chunk = self.rfile.read(chunk_size)
					if not chunk:
						break
					L.append(chunk)
					size_remaining -= len(L[-1])
				data = b''.join(L)

			except Exception as e: # This should only happen if the module is buggy
				self.print_trace(e)
				return

			try:
				params = json.loads(data)
			except ValueError:
				params = {k: v if len(v) > 1 else v[0]
					for k, v in urlparse.parse_qs(data.decode()).items()}
			if self.handle_route(path, params,
				SimpleCookie(self.headers.get('Cookie')), None):
				return
			log('[Handler] POST Error: %s %s' % (self.path, data))

		# ooooooooooooo ooooooooo.         .o.         .oooooo.   oooooooooooo
		# 8'   888   `8 `888   `Y88.      .888.       d8P'  `Y8b  `888'     `8
		#      888       888   .d88'     .8"888.     888           888
		#      888       888ooo88P'     .8' `888.    888           888oooo8
		#      888       888`88b.      .88ooo8888.   888           888    "
		#      888       888  `88b.   .8'     `888.  `88b    ooo   888       o
		#     o888o     o888o  o888o o88o     o8888o  `Y8bood8P'  o888ooooood8
		#
		def print_trace(self, e):
			# internal error, report as HTTP server error
			self.send_response(500)

			# Send information about the exception if requested
			if self.debug:
				self.send_header('X-exception', str(e))
				self.send_header('X-traceback', traceback.format_exc())

			self.send_header('Content-length', "0")
			self.end_headers()

			log(traceback.format_exc())

		# ooooooooo.     .oooooo.   ooooo     ooo ooooooooooooo oooooooooooo
		# `888   `Y88.  d8P'  `Y8b  `888'     `8' 8'   888   `8 `888'     `8
		#  888   .d88' 888      888  888       8       888       888
		#  888ooo88P'  888      888  888       8       888       888oooo8
		#  888`88b.    888      888  888       8       888       888    "
		#  888  `88b.  `88b    d88'  `88.    .8'       888       888       o
		# o888o  o888o  `Y8bood8P'     `YbodP'        o888o     o888ooooood8
		#
		def handle_route(self, path, params, cookies, set_cookie):
			"""Common code for GET and POST commands to handle route and send json result."""
			names = list(filter(None, path.split('/')))[:2]
			if len(names) == 0 and self.index_route:
				moduleName, routeName = self.index_route, 'index'
			elif len(names) == 1:
				moduleName, routeName = names[0], 'index'
			else:
				moduleName, routeName = names

			# load module
			if moduleName not in self.modules:
				try:
					path = os.path.join(self.app_route, moduleName + '.py')
					mod = imp.load_source(moduleName, path)
					self.modules[moduleName] = {k: getattr(mod, k) for k in dir(mod)
						if getattr(getattr(mod, k), '____isRoute__', False)}
				except IOError:
					self.send_error(404, 'Route module "%s" not found' % moduleName)
					return True
				except Exception as e:
					self.print_trace(e)
					return True

			module = self.modules[moduleName]
			if routeName not in module:
				self.send_error(404, 'Route "%s" not found' % routeName)
				return True
			route = module[routeName]

			try:
				alarm = Alarm(self.app_timeout, 'Route "%s" timeout(%s)' % (routeName, self.app_timeout))

				t, cookie, result = route(cookies, **params)
				cookie is not None and cookies.load(cookie)
				if set_cookie:
					if cookie is None:
						cookie = SimpleCookie(set_cookie)
					else:
						cookie.load(set_cookie)
				if t == ROUTE_REDIRECT:
					if self.send_file(result[0], cookie):
						return True
					elif self.handle_route(result.path, result.params, cookies, cookie):
						return True
					raise RuntimeError('Redirect "%s" error with params: %s' % (result.path, result.params))

				if route.____template__ is None:
					content_type = 'text/json'
					result = json.dumps(result)
				else:
					content_type = 'text/html'
					result = self.template(route.____template__, result)
				result = result.encode()

			except Exception as e:
				self.print_trace(e)
			else:
				self.send_response(200)
				self.send_header('Content-type', content_type)
				self.send_header('Content-length', str(len(result)))
				if cookie is not None:
					if hasattr(self, 'flush_headers'): self.flush_headers()
					self.wfile.write(cookie.output().encode())
					self.wfile.write(b'\r\n')
				self.end_headers()
				self.wfile.write(result)
			finally:
				alarm.cancel()

			return True

		# oooooooooooo ooooo ooooo        oooooooooooo
		# `888'     `8 `888' `888'        `888'     `8
		#  888          888   888          888
		#  888oooo8     888   888          888oooo8
		#  888    "     888   888          888    "
		#  888          888   888       o  888       o
		# o888o        o888o o888ooooood8 o888ooooood8
		#
		def send_file(self, path, cookie):
			"""Common code for GET and POST commands to send the response code, MIME headers and file contents."""
			path = os.path.join(self.file_path, path.lstrip('/'))
			if not os.path.isfile(path):
				if not os.path.isdir(path):
					_, ext = posixpath.splitext(path)
					if ext in self.extensions_map:
						self.send_error(404, 'File "%s" not found' % (path))
						return True
					return False
				index = os.path.join(path, 'index.html')
				if not os.path.isfile(index):
					index = os.path.join(path, 'index.htm')
					if not os.path.isfile(index):
						return False
				path = index

			filename, ext = posixpath.splitext(path)
			if path.endswith(TEMPLATE_EXT):
				log('[Handler] Request file with template extensions: "%s"' % path)
				return False
			elif ext not in self.extensions_map:
				ext = ext.lower()
				if ext not in self.extensions_map:
					return False

			if not self.debug and path in self.cache:
				content, length, mtime = self.cache[path]
			else:
				try:
					# Always read in binary mode. Opening files in text mode may cause
					# newline translations, making the actual size of the content
					# transmitted *less* than the content-length!
					with open(path, 'rb') as f:
						fs = os.fstat(f.fileno())
						content = f.read()
						length = str(fs[6])
						mtime = self.date_time_string(fs.st_mtime)
					self.cache[path] = content, length, mtime
				except IOError:
					self.send_error(404, 'File "%s" not found' % path)
					return True
				except Exception as e:
					self.print_trace(e)
					return True

			self.send_response(200)
			self.send_header('Content-type', self.extensions_map[ext])
			self.send_header('Content-Length', length)
			self.send_header('Last-Modified', mtime)
			if cookie is not None:
				if hasattr(self, 'flush_headers'): self.flush_headers()
				self.wfile.write(cookie.output().encode())
				self.wfile.write(b'\r\n')
			self.end_headers()
			self.wfile.write(content)

			return True

		# ooooooooooooo oooooooooooo ooo        ooooo ooooooooo.   ooooo              .o.       ooooooooooooo oooooooooooo
		# 8'   888   `8 `888'     `8 `88.       .888' `888   `Y88. `888'             .888.      8'   888   `8 `888'     `8
		#      888       888          888b     d'888   888   .d88'  888             .8"888.          888       888
		#      888       888oooo8     8 Y88. .P  888   888ooo88P'   888            .8' `888.         888       888oooo8
		#      888       888    "     8  `888'   888   888          888           .88ooo8888.        888       888    "
		#      888       888       o  8    Y     888   888          888       o  .8'     `888.       888       888       o
		#     o888o     o888ooooood8 o8o        o888o o888o        o888ooooood8 o88o     o8888o     o888o     o888ooooood8
		#
		TEMPLATE_SEGMENT = re.compile(r'\s*<\?python[^\?]+\?>', re.I)

		class TemplateOutput(object):
			def __init__(self):
				self.content = ''

			def __getitem__(self, content):
				self.content += content

			def __getattr__(self, key):
				def dump(data):
					self.content += '<script type="text/javascript">var %s = %s;</script>' % (key, json.dumps(data) or "null")
				return dump

		def template(self, path, data):
			path = os.path.join(self.file_path, path.lstrip('/'))
			if not self.debug and path in self.cache:
				content, template = self.cache[path]
			else:
				with codecs.open(path, 'r', 'utf-8') as f:
					content = f.read()

				text_segs = self.TEMPLATE_SEGMENT.split(content)
				code_segs = self.TEMPLATE_SEGMENT.findall(content)

				template = ['_["""%s"""]' % text_segs[0].replace('"', '\\"')]
				for i , code_seg in enumerate(code_segs):
					prefix, code_seg = code_seg[:-2].split('<?python')
					prefix = prefix.lstrip('\n')
					codes = code_seg.split('\n')
					for code in codes:
						if not code.strip(): continue
						assert code.startswith(prefix), (prefix, code)
						code = code[len(prefix):].rstrip()
						indent = code[:-len(code.lstrip())]
						template.append(code)
						if code.endswith(':'):
							indent += '\t'

					text = text_segs[i + 1]
					template.append('%s_["""%s"""]' % (indent, text.replace('"', '\\"')))
				template = compile('\n'.join(template), path, 'exec')
				self.cache[path] = content, template

			output = self.TemplateOutput()
			globals = {'_': output}
			globals.update(data)
			exec_delegate(template, globals)
			return output.content

		def log_message(self, format, *args):
			log('%s - - [%s] %s' % (self.address_string(),
				self.log_date_time_string(), format % args))

		if not mimetypes.inited:
			mimetypes.init() # try to read system mime.types
		extensions_map = mimetypes.types_map.copy()

	_TarantulaHTTPRequestHandler.app_route = app_route
	_TarantulaHTTPRequestHandler.file_path = file_path
	_TarantulaHTTPRequestHandler.index_route = index_route
	_TarantulaHTTPRequestHandler.app_timeout = app_timeout
	_TarantulaHTTPRequestHandler.timeout = request_timeout
	_TarantulaHTTPRequestHandler.debug = debug

	for t in (extra_types or ()):
		k, v = t.split(':')
		_TarantulaHTTPRequestHandler.extensions_map[k.strip()] = v.strip()


	return _TarantulaHTTPRequestHandler

#  .oooooo..o
# d8P'    `Y8
# Y88bo.       .ooooo.  oooo d8b oooo    ooo  .ooooo.
#  `"Y8888o.  d88' `88b `888""8P  `88.  .8'  d88' `88b
#      `"Y88b 888ooo888  888       `88..8'   888ooo888
# oo     .d8P 888        888        `888'    888
# 8""88888P'  `Y8bod8P' d888b        `8'     `Y8bod8P'
#
def serve(port, log_tag, debug, *args):
	if debug:
		class TarantulaHTTPServer(BaseHTTPServer.HTTPServer): pass
	elif hasattr(os, "fork"):
		class TarantulaHTTPServer(SocketServer.ForkingMixIn, BaseHTTPServer.HTTPServer): pass
	else:
		class TarantulaHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): pass

	httpd = TarantulaHTTPServer(('', port), TarantulaHTTPRequestHandler(debug, *args))
	sa = httpd.socket.getsockname()
	openlog(log_tag)
	log('[Server] Serving HTTP on %s port %s ...' % (sa[0], sa[1]))
	httpd.serve_forever()

if __name__ == '__main__':
	# Parse command line arguments
	import argparse

	parser = argparse.ArgumentParser(description = 'tarantula')

	parser.add_argument('-a', dest = 'app_route', type = str, default = '', help = 'application route path')
	parser.add_argument('-f', dest = 'file_path', type = str, default = '', help = 'static file path')
	parser.add_argument('-i', dest = 'index_route', type = str, help = 'default route module name')
	parser.add_argument('-t', dest = 'app_timeout', type = int, default = 5, help = 'application route timeout')
	parser.add_argument('-r', dest = 'request_timeout', type = int, default = 30, help = 'request connection timeout')
	parser.add_argument('-p', dest = 'port', type = int, default = 80, help = 'listen listen port')
	parser.add_argument('-l', dest = 'log_tag', type = str, default = 'log', help = 'log name')
	parser.add_argument('-d', dest = 'debug', type = bool, default = False, help = 'debug mode')
	parser.add_argument('-m', dest = 'mimetypes', type = str, action='append', help = 'extra mimetypes')

	args = parser.parse_args()

	serve(args.port, args.log_tag, args.debug, args.app_route, args.file_path, args.index_route, args.app_timeout, args.request_timeout, args.mimetypes)
