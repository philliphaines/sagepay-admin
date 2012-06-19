import md5
import sys
import httplib
import urllib

class SagePay(object):
	def __init__(self, vendor, username, password):
		super(SagePay, self).__init__()
		self.vendor = vendor
		self.username = username
		self.password = password
		self.host = "live.sagepay.com"

	def addIPAddress(self, ipaddress):
		if not self.__validIP(ipaddress):
			print "Invalid IPADDRESS"
			return False			

		ipaddress = self.__formatIP(ipaddress)


		self.xml = """<command>addValidIPs</command><vendor>%(vendor)s</vendor><user>%(user)s</user><validips><ipaddress><address>%(ip)s</address><mask>255.255.255.255</mask><note>%(note)s</note></ipaddress></validips>""" % { 'vendor' : self.vendor, 'user': self.username, 'ip': ipaddress, 'note': "Added by " + self.username }		
		return self.__post()

	def removeIPAddress(self, ipaddress):
		if not self.__validIP(ipaddress):
			print "Invalid IPADDRESS"
			return False			

		ipaddress = self.__formatIP(ipaddress)

		self.xml = """<command>deleteValidIPs</command><vendor>%(vendor)s</vendor><user>%(user)s</user><validips><ipaddress><address>%(ip)s</address><mask>255.255.255.255</mask></ipaddress></validips>""" % { 'vendor' : self.vendor, 'user': self.username, 'ip': ipaddress }
		return self.__post()

	def testing(self):
		self.host = "test.sagepay.com"

	def __sign(self):
		signature = md5.new(self.xml + """<password>%(password)s</password>""" % { 'password' : self.password })			
		return "<vspaccess>" + self.xml + """<signature>%(signature)s</signature>""" % { 'signature' : signature.hexdigest() } + "</vspaccess>"		    	    

	def __post(self):
		xmlToPost = "XML=" + self.__sign()
		
		headers = {"Content-type": "application/x-www-form-urlencoded", "Content-Length": len(xmlToPost)}
		connection = httplib.HTTPSConnection(self.host)

		connection.request("POST", "/access/access.htm", "", headers)
		connection.send(xmlToPost)	

		response = connection.getresponse()

		payload = response.read()
	
		return "<errorcode>0000</errorcode>" in payload

	def __validIP(self, address):
		parts = address.split(".")
		if len(parts) != 4:
			return False
		for item in parts:
			if not 0 <= int(item) <= 255:
				return False
		
		return True

	# SagePay requires 3 digit padding to each part of the IP address i.e. 1.2.3.4 => 001.002.003.004
	def __formatIP(self, address):
		parts = address.split(".")
		ipString = ""

		for item in parts:
			ipString = ipString + ("000" + item)[-3:] + "."

		# strip the trailing dot
		return ipString[:-1]