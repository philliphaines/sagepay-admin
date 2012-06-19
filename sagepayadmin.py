#! /usr/bin/env python

from sagepay import SagePay
import sys
from optparse import OptionParser
from optparse import OptionGroup

usage = "usage: %prog [options] command"
parser = OptionParser(usage)

parser.add_option("-v", "--vendor", dest="vendor", metavar="VENDOR", help="SagePay vendor name [required]")
parser.add_option("-u", "--user", dest="username", metavar="USERNAME", help="SagePay username [required]")
parser.add_option("-p", "--pass", dest="password", metavar="PASSWORD", help="SagePay password [required]")
parser.add_option("-i", "--ip", dest="ipaddress", metavar="IPADDRESS", help="IP address")

debugGroup = OptionGroup(parser, "Debugging Options")
debugGroup.add_option("-t", "--test", dest="test", action="store_true", help="use sagepay test server")
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