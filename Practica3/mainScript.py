import sys
import datetime
from time import time

from twisted.internet import task
from twisted.names import client

def reverseNameFromIPAddress(address):
	return '.'.join(reversed(address.split('.'))) + '.in-addr.arpa'

def printResult2(result, inicio, to = None):
	print(result)
	fin = time()
	diff =  fin - inicio[0]
	inicio.append(diff)
	to = []
	to.append(inicio)
	print('Tiempo en resolver {}'.format(diff))
	return to

def printResult(result, inicio, to = None):
	answers, authority, additional = result
	if answers:
		a = answers[0]
		print('{} IN {}'.format(a.name.name, a.payload))
	fin = datetime.datetime.now()
	diff =  fin - inicio
	print('Tiempo en resolver {}'.format(diff))
	return diff

def error(result, inicio):
	print(result)
	fin = datetime.datetime.now()
	diff =  fin - inicio
	print('Tiempo en resolver {}'.format(diff))
	return diff

def readList():
	f  = open("list.txt","r")
	lines = f.readlines()
	hosts = []
	for line in lines:
		hosts.append(line.split(','))
	return hosts


def main(reactor):
	hosts = readList()
   	for host in hosts:
		inicio = datetime.datetime.now()
		if host[1] == 'A\n':
			d = client.getHostByName(host[0])
			l = [time()]
			a = d.addCallback(printResult2, l)
			print l
			print a, type(a)

			b = d.addErrback(error, inicio)
			print b

		else:
			d = client.lookupPointer(name=reverseNameFromIPAddress(address=host[0]))
			d.addCallback(printResult, inicio)
			d.addErrback(error, inicio)
	return d

print 'la'
a = task.react(main)

print 'a', a

