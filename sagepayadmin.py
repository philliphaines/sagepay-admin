#! /usr/bin/env python

from optparse import OptionParser
from optparse import OptionGroup
import md5, sys, httplib, urllib

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
	
		if "<errorcode>0000</errorcode>" in payload or "<errorcode>9998</errorcode>" in payload:
			return True		
		else:
			print "Error updating SagePay: " + payload

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

usage = "usage: %prog [options] command"
parser = OptionParser(usage)

parser.add_option("-v", "--vendor", dest="vendor", metavar="VENDOR", help="SagePay vendor name [required]")
parser.add_option("-u", "--user", dest="username", metavar="USERNAME", help="SagePay username [required]")
parser.add_option("-p", "--pass", dest="password", metavar="PASSWORD", help="SagePay password [required]")
parser.add_option("-i", "--ip", dest="ipaddress", metavar="IPADDRESS", help="IP address")

debugGroup = OptionGroup(parser, "Debugging Options")
debugGroup.add_option("-t", "--test", dest="test", action="store_true", help="use sagepay test server")
debugGroup.add_option("-l", "--live", dest="live", action="store_true", help="use sagepay live server [default]")
parser.add_option_group(debugGroup)

(options, args) = parser.parse_args()

def exitCode(okay):
	if okay:
		sys.exit(0)
	else:
		sys.exit(-1)

if options.vendor == None or options.username == None or options.password == None:
	print "VENDOR, USERNAME and PASSWORD are required"
	sys.exit(-1)

sagePay = SagePay(options.vendor, options.username, options.password)

if options.test and options.live:
	print "--live and --test are mutually exclusive"
	sys.exit(-1)

if options.test: 
	sagePay.testing()

if not len(args) == 1:
	print "command is required"
	sys.exit(-1)

if args[0].lower() == "addip":
	if options.ipaddress == None:
		print "IPADDRESS required to add IP address to SagePay"
		sys.exit(-1)

	exitCode(sagePay.addIPAddress(options.ipaddress))

elif args[0].lower() == "removeip":
	if options.ipaddress == None:
		print "IPADDRESS required to remove IP address to SagePay"
		sys.exit(-1)	

	exitCode(sagePay.removeIPAddress(options.ipaddress))

else:
	print "command options are addip|removeip"