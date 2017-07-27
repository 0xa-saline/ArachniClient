#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

POST_HINT_CONTENT_TYPES = {
    "JSON": "application/json",
    "MULTIPART": "multipart/form-data",
    "SOAP": "application/soap+xml",
    "XML": "application/xml",
    "normal": "application/x-www-form-urlencoded; charset=utf-8",
}

class Http_Info(object):
	"""docstring for ClassName"""
	def __init__(self, url,method,type,data=''):
		super(Http_Info, self).__init__()
		self.url = url
		self.method = method
		self.type = type
		self.data = data


	def to_param_dict(self,params):
	    """a=1&b=2 to {'a':1,'b':2}"""
	    param_dict = {}
	    if not params:
	        return param_dict
	    try:
	        split_params = params.split('&')
	        for element in split_params:
	            elem = element.split("=")
	            if len(elem) >= 2:
	                parameter = elem[0].replace(" ", "")
	                value = "=".join(elem[1:])
	                param_dict[parameter] = value
	    except:
	        pass

	    return param_dict
		

	def _check(self,method,url,data):
	   import urlparse
	   import os
	   furl = urlparse.urlparse(url)
	   fileext = os.path.splitext(furl.path)[-1]

	   EXCLUDE_EXTENSIONS = [".css", ".js", ".3ds", ".ttf", ".3g2", ".3gp", ".7z", ".DS_Store", ".a", ".aac", ".adp", ".ai", ".aif", ".aiff", ".apk", ".ar", ".asf", ".au", ".avi", ".bak", ".bin", ".bk", ".bmp", ".btif", ".bz2", ".cab", ".caf", ".cgm", ".cmx", ".cpio", ".cr2", ".dat", ".deb", ".djvu", ".dll", ".dmg", ".dmp", ".dng", ".doc", ".docx", ".dot", ".dotx", ".dra", ".dsk", ".dts", ".dtshd", ".dvb", ".dwg", ".dxf", ".ear", ".ecelp4800", ".ecelp7470", ".ecelp9600", ".egg", ".eol", ".eot", ".epub", ".exe", ".f4v", ".fbs", ".fh", ".fla", ".flac", ".fli", ".flv", ".fpx", ".fst", ".fvt", ".g3", ".gif", ".gz", ".h261", ".h263", ".h264", ".ico", ".ief", ".image", ".img", ".ipa", ".iso", ".jar", ".jpeg", ".jpg", ".jpgv", ".jpm", ".jxr", ".ktx", ".lvp", ".lz", ".lzma", ".lzo", ".m3u", ".m4a", ".m4v", ".mar", ".mdi", ".mid", ".mj2",
	      ".ttf",".ico",".mka", ".mkv", ".mmr", ".mng", ".mov", ".movie", ".mp3", ".mp4", ".mp4a", ".mpeg", ".mpg", ".mpga", ".mxu", ".nef", ".npx", ".o", ".oga", ".ogg", ".ogv", ".otf", ".pbm", ".pcx", ".pdf", ".pea", ".pgm", ".pic", ".png", ".pnm", ".ppm", ".pps", ".ppt", ".pptx", ".ps", ".psd", ".pya", ".pyc", ".pyo", ".pyv", ".qt", ".rar", ".ras", ".raw", ".rgb", ".rip", ".rlc", ".rz", ".s3m", ".s7z", ".scm", ".scpt", ".sgi", ".shar", ".sil", ".smv", ".so", ".sub", ".swf", ".tar", ".tbz2", ".tga", ".tgz", ".tif", ".tiff", ".tlz", ".ts", ".ttf", ".uvh", ".uvi", ".uvm", ".uvp", ".uvs", ".uvu", ".viv", ".vob", ".war", ".wav", ".wax", ".wbmp", ".wdp", ".weba", ".webm", ".webp", ".whl", ".wm", ".wma", ".wmv", ".wmx", ".woff", ".woff2", ".wvx", ".xbm", ".xif", ".xls", ".xlsx", ".xlt", ".xm", ".xpi", ".xpm", ".xwd", ".xz", ".z", ".zip", ".zipx",".axd"]
	   if fileext in EXCLUDE_EXTENSIONS:
	      return False

	   if method == 'GET':
	      if furl.path[-1] == '/':
	         return False
	      elif "?" not in url:
	         return False
	      else:
	         return True

	   elif method == 'POST' or method == 'post':
	      #如果url没有？同时data也没有数据
	      if "?" not in url and (data == '' or len(data)==0):
	         return False
	      else:
	         return True

	def _match_content(self,data):
	   type_get = ''
	   types = {
	      "SOAP":"<soap:Envelope([\s\S]*?)</soap:Envelope>",
	      "XML": "<xml>.*?</xml>",
	      "JSON":"({\'\w*\':.*?})|({\"\w*\":.*?})",
	      "MULTIPART" : "-+\w[-\w.+]*([\s\S].*)Content-Disposition"
	   }
	   for types,value in types.iteritems():
	      #print types,value
	      if re.search(value,data):
	         type_get = types
	   
	   if type_get == '':
	      type_get = 'normal'

	   return POST_HINT_CONTENT_TYPES.get(type_get)

	def param_data(self):
		headers = {"referer":self.url}
		if self._check(self.method, self.url, self.data):
			if self.method == "POST":
				headers["Content-Type"] = self._match_content(self.data)

			if self.data:
				param = {'type':self.type,'method':self.method,'action':self.url,'inputs':[self.to_param_dict(self.data)]}
			else:
				param = {'type':self.type,'method':self.method,'action':self.url}

			return headers,param
