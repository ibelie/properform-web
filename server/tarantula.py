#-*- coding: utf-8 -*-
# Copyright 2017 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

__author__ = 'Joungtao'
__version__ = '0.0.1'
__all__ = ["TarantulaHTTPRequestHandler", "serve"]

import os
import imp
import sys
import json
import shutil
import urlparse
import mimetypes
import posixpath
import BaseHTTPServer
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO


def route(func):
	func.____isRoute__ = True
	return func


def TarantulaHTTPRequestHandler(app_route, file_path):
	class _TarantulaHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
		modules = {}
		app_route = app_route
		file_path = file_path
		protocol_version = "HTTP/1.0"
		server_version = "TarantulaHTTP/" + __version__

		def do_GET(self):
			"""Serve a GET request."""
			_, _, path, query, _ = urlparse.urlsplit(self.path)
			if self.send_file(path):
				return
			elif self.handle_route(path, urlparse.parse_qs(query)):
				return
			print '[Tarantula] GET Error:', self.path

		def do_POST(self):
			"""Serve a POST request."""
			# ignore parameters form URL
			_, _, path, _, _ = urlparse.urlsplit(self.path)
			if self.send_file(path):
				return

			try:
				# Get arguments by reading body of request.
				# We read this in chunks to avoid straining
				# socket.read(); around the 10 or 15Mb mark, some platforms
				# begin to have problems (bug #792570).
				max_chunk_size = 10*1024*1024
				size_remaining = int(self.headers["content-length"])
				L = []
				while size_remaining:
					chunk_size = min(size_remaining, max_chunk_size)
					chunk = self.rfile.read(chunk_size)
					if not chunk:
						break
					L.append(chunk)
					size_remaining -= len(L[-1])
				data = ''.join(L)

			except Exception, e: # This should only happen if the module is buggy
				self.print_trace(e)
				return

			print 'do_POST data: %s' % repr(data)

		def print_trace(self, e):
			# internal error, report as HTTP server error
			self.send_response(500)

			# Send information about the exception if requested
			if hasattr(self.server, '_send_traceback_header') and self.server._send_traceback_header:
				self.send_header("X-exception", str(e))
				self.send_header("X-traceback", traceback.format_exc())

			self.send_header("Content-length", "0")
			self.end_headers()

		def handle_route(self, path, params):
			"""Common code for GET and POST commands to handle route and send json result."""
			names = filter(None, path.split('/'))[:2]
			if len(names) < 2:
				return False
			moduleName, routeName = names

			# load module
			if moduleName not in self.modules:
				try:
					path = os.path.join(self.app_route, moduleName + '.py')
					f = open(path, 'rb')
				except IOError:
					self.send_error(404, "Route module not found")
					return True
				try:
					mod = imp.new_module(moduleName)
					exec f.read() in mod.__dict__
					self.modules[moduleName] = {k: getattr(mod, k) for k in dir(mod)
						if getattr(getattr(mod, k), '____isRoute__', False)}
				except Exception, e:
					self.print_trace(e)
					return True
				finally:
					f.close()

			module = self.modules[moduleName]
			if routeName not in module:
				self.send_error(404, "Route not found")
				return True
			route = module[routeName]

			try:
				params = {k: v if len(v) > 1 else v[0] for k, v in params.iteritems()}
				result = json.dumps(route(**params))
			except Exception, e:
				self.print_trace(e)
				return True
			else:
				self.send_response(200)
				self.send_header("Content-type", "text/json")
				self.send_header("Content-length", str(len(result)))
				self.end_headers()
				self.wfile.write(result)

		def send_file(self, path):
			"""Common code for GET and POST commands to send the response code, MIME headers and file contents."""
			path = os.path.join(self.file_path, path.lstrip('/'))
			if not os.path.isfile(path):
				if not os.path.isdir(path):
					_, ext = posixpath.splitext(path)
					if ext in self.extensions_map:
						self.send_error(404, "File not found")
						return True
					return False
				index = os.path.join(path, 'index.html')
				if not os.path.isfile(index):
					index = os.path.join(path, 'index.htm')
					if not os.path.isfile(index):
						return False
				path = index

			_, ext = posixpath.splitext(path)
			if ext not in self.extensions_map:
				ext = ext.lower()
				if ext not in self.extensions_map:
					return False
			try:
				# Always read in binary mode. Opening files in text mode may cause
				# newline translations, making the actual size of the content
				# transmitted *less* than the content-length!
				f = open(path, 'rb')
			except IOError:
				self.send_error(404, "File not found")
				return True
			try:
				self.send_response(200)
				self.send_header("Content-type", self.extensions_map[ext])
				fs = os.fstat(f.fileno())
				self.send_header("Content-Length", str(fs[6]))
				self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
				self.end_headers()
				shutil.copyfileobj(f, self.wfile)
			finally:
				f.close()
			return True

		if not mimetypes.inited:
			mimetypes.init() # try to read system mime.types
		extensions_map = mimetypes.types_map.copy()

	return _TarantulaHTTPRequestHandler


def serve(port, app_route, file_path):
	httpd = BaseHTTPServer.HTTPServer(('', port),
		TarantulaHTTPRequestHandler(app_route, file_path))
	sa = httpd.socket.getsockname()
	print "[Tarantula] Serving HTTP on", sa[0], "port", sa[1], "..."
	httpd.serve_forever()


if __name__ == '__main__':
	if sys.argv[1:]:
		app_route = str(sys.argv[1])
	else:
		app_route = ''
	if sys.argv[2:]:
		file_path = str(sys.argv[2])
	else:
		file_path = ''
	if sys.argv[3:]:
		port = int(sys.argv[3])
	else:
		port = 80
	serve(port, app_route, file_path)
