# -*- coding: utf-8 -*-
from agent import *

from pysnmp.hlapi import *

from glob import glob

from os import remove

from time import sleep

from threading import Thread


import rrdtool

class ManagerSNMP():
	_querys = {
		'MIB'		: '1.3.6.1.2.1',
		'Info'		: '.1.1.0',
		#''		: '.1.2.0',
		'UpTime'	: '.1.3.0',
		'Contact'		: '.1.4.0',
		'NodeName'		: '.1.5.0',
		'Localization'	: '.1.6.0',
		'NumInterFs'	: '.2.1.0',
		'NameInterFs'	: '.2.2.1.2',
		'TypeInterFs'	: '.2.2.1.3',
		'PhyAddInterFs'	: '.2.2.1.6',
		'StatusInterFs'	: '.2.2.1.8',
		'InOctInterFs'	: '.2.2.1.10',
		'OutOctInterFs'	: '.2.2.1.16',
		'InIP'			: '.4.3.0',
		'OutIP'			: '.4.10.0',
		'InICMP' 		: '.5.1.0',
		'OutICMP'		: '.5.14.0',
		'InTCP'			: '.6.10.0',
		'OutTCP'		: '.6.11.0',
		'InUDP'			: '.7.1.0',
		'OutUDP'		: '.7.4.0',
	}

	_fname = {
		'infs' : './agents/{}_interface{}.{}',
		'ip' : './agents/{}_ip.{}',
		'icmp' : './agents/{}_icmp.{}',
		'tcp' : './agents/{}_tcp.{}',
		'udp' : './agents/{}_udp.{}',
	}
	_names = [
		'infs',
		'ip',
		'icmp',
		'tcp',
		'udp',
	]

	#_images = 'images/{}'
	
	def __init__(self):
		self._agents = {}
		self._numAgents = 0

		print self._fname.keys()

		self._thread = Thread(target = self._updateRRD, args = ())
		self._thread.daemon = True
		self._thread.start()

	def _getBasicData(self, hostname):
		try:
			eIndi, eStatus, eIndex, vBinds = next(
				getCmd(SnmpEngine(),
					CommunityData(self._agents[hostname].getCommunity()), 
					UdpTransportTarget((hostname, self._agents[hostname].getPort())),
					ContextData(),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['Info'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['Contact'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['NodeName'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['Localization'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['NumInterFs'])))
			)
			if eIndi:
				#print eIndi
				return False
			elif eStatus:
				#print eIndex, eStatus
				return False
			else:
				i = 0
				for varBind in vBinds:
					a = [x.prettyPrint() for x in varBind]
					if i == 0:
						self._agents[hostname].setInfo(a[1])
					elif i == 1:
						self._agents[hostname].setContact(a[1])
					elif i == 2:
						self._agents[hostname].setNode(a[1])
					elif i == 3:
						self._agents[hostname].setLocalization(a[1])
					elif i == 4:
						self._agents[hostname].setNumInterFs(int(a[1]))
					else:
						print 'Error'
					i += 1
				self._createRRD(hostname)
				self._getAgentInterFs(hostname)
				self._agents[hostname].setStatus(True)
				return True
		except:
			return False

	def _getAgentInterFs(self, hostname):
		
		if not hostname in self._agents:
			return 
		
		walk = nextCmd(SnmpEngine(),
			CommunityData(self._agents[hostname].getCommunity()),
			UdpTransportTarget((hostname, self._agents[hostname].getPort())),
			ContextData(), 
			ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['NameInterFs'])),
			ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['StatusInterFs'])),
			ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InOctInterFs'])),
			ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutOctInterFs'])),
		)
		
		n = self._agents[hostname].getNumInterFs()

		interfaces = []
		
		s = self._fname[self._names[0]]

		for i in range(n):
			eIndi, eStatus, eIndex, vBinds = next(walk)
			if eIndi:
				#print eIndi
				self._agents[hostname].setStatus(False)
			elif eStatus:
				#print eIndex, eStatus
				self._agents[hostname].setStatus(False)
			else:
				data = 0
				interface = {}

				for varBind in vBinds:
					
					a = [x.prettyPrint() for x in varBind]

					if data == 0:
						try:
							interface['name'] = a[1].decode('hex')
						except:
							interface['name'] = a[1]
						data += 1

					elif data == 1:
						interface['status'] = 'Up' if a[1] == '1' else 'Down'
						data += 1

					elif data == 2:
						inData = a[1]
						data += 1

					elif data == 3:
						outData = a[1]
						nRRD = s.format(hostname, i, 'rdd')
						value = ':'.join(['N', str(inData), str(outData)])
						print nRRD, value
						try:
							ret = rrdtool.update(nRRD, value) 
						except:
							break
						# update RRD
					else:
						print 'Error'
				interfaces.append(interface)
		
		self._agents[hostname].setInterfaces(interfaces)

	def _getAgentData(self, hostname):

		if not hostname in self._agents:
			return

		eIndi, eStatus, eIndex, vBinds = next(
			getCmd(SnmpEngine(),
				CommunityData(self._agents[hostname].getCommunity()), 
				UdpTransportTarget((hostname, self._agents[hostname].getPort())),
				ContextData(),
				ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['UpTime'])))
		)
		
		if eIndi:
			print eIndi
			self._agents[hostname].setStatus(False)
		elif eStatus:
			print eIndex, eStatus
			self._agents[hostname].setStatus(False)
		else:
			i = 0
			
			for varBind in vBinds:
				a = [x.prettyPrint() for x in varBind]
				self._agents[hostname].setUpTime(int(a[1]))
			
			self._getAgentInterFs(hostname)
		
		return

	def _createRRD(self, hostname):
		for fname in self._fname:
			s = self._fname[fname]
			
			if fname != self._names[0]:
				
				name = s.format(hostname, 'rrd')
				
				ret = rrdtool.create(name, 
								'--start', 'N', 
								'--step', '60',
								'DS:in:COUNTER:600:U:U',
								'DS:out:COUNTER:600:U:U',
								'RRA:MAX:0.5:5:50',
								'RRA:MAX:0.5:1:75')
				if ret:
					print name, rrdtool.error()

			else:
				for i in range(self._agents[hostname].getNumInterFs()):

					name = s.format(hostname, i, 'rrd')

					ret = rrdtool.create(name, 
								'--start', 'N', 
								'--step', '60',
								'DS:in:COUNTER:600:U:U',
								'DS:out:COUNTER:600:U:U',
								'RRA:MAX:0.5:5:50',
								'RRA:MAX:0.5:1:75')

					if ret:
						print name, rrdtool.error()

	def _updateRRD(self):
		while(1):
			hosts = self._agents.keys()
			for host in hosts:#get agent data
				try:

					if not host in self._agents: # check if agent was deleted
						continue # if deleted go next

					self._getAgentData(host) #update time up

					if not self._agents[host].getStatus(): #if agent is not active, go to next
						continue

					eIndi, eStatus, eIndex, vBinds = next(
						getCmd(SnmpEngine(),
							CommunityData(self._agents[host].getCommunity()), 
							UdpTransportTarget((host, self._agents[host].getPort())),
							ContextData(),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InIP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutIP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InUDP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutUDP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InICMP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutICMP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InTCP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutTCP'])))
					)

					if eIndi:
						print eIndi

					elif eStatus:
						print eIndex, eStatus

					else:
						i = 0
						inData = ''
						outData = ''
						for varBind in vBinds:
							a = [x.prettyPrint() for x in varBind]
							if not i&1:
								inData = str(a[1])
							else:

								outData = str(a[1])
								value = ':'.join(['N', inData, outData])

								fn = self._names[(i/2) + 1]
								nRRD = self._fname[fn].format(host, 'rrd')
								
								print nRRD, value

								try:
									ret = rrdtool.update(nRRD, value) 
								except:
									break
							i += 1
				except: #Preventing exception if agent is deleted while working on it
					continue
			sleep(.5)

	def _makegraphs(self, hostname):

		for fname in self._fname:

			if fname == self._names[0]:

				for i in range(self._agents[hostname].getNumInterFs()):

					name = self._fname[fname]
					nImg = name.format(hostname, i, 'png')
					nRRD = name.format(hostname, i, 'rrd')

					ret = rrdtool.graph(nImg,
								'--start', str(self._agents[hostname].getTime()),
								'--vertical-label=Bytes/s',
								'DEF:in='+nRRD+':in:MAX',
								'DEF:out='+nRRD+':out:MAX',
								'LINE1:in#0F0F0F:In Traffic',
								'LINE2:out#000FFF:Out Traffic')
			else:

				name = self._fname[fname]
				nImg = name.format(hostname, 'png')
				nRRD = name.format(hostname, 'rrd')

				ret = rrdtool.graph(nImg,
									'--start', str(self._agents[hostname].getTime()),
									'--vertical-label=Bytes/s',
									'DEF:in='+nRRD+':in:MAX',
									'DEF:out='+nRRD+':out:MAX',
									'LINE1:in#0F0F0F:In Traffic',
									'LINE2:out#000FFF:Out Traffic')

	def _getAgentsData(self):
		devices = []
		for host in self._agents:
			devices.append(self._agents[host].getDict())
		return devices

	def addAgent(self, agent):
		host = agent.getHostName()
		if host in self._agents:
			return True
		self._numAgents += 1
		self._agents[host] = agent
		return self._getBasicData(host)

	def delAgent(self, hostname):
		try:
			self._agents[hostname].setStatus(False)
			del self._agents[hostname]
			sleep(.25)
			self._numAgents -= 1
			path = './agents/' + hostname + '*'
			files = glob(path)
			for file in files:
				remove(file)
			return True
		except:
			return False

	def getDict(self):
		data = {}
		data['num_device'] = self._numAgents
		data['devices'] = self._getAgentsData()
		return data

	def getAgentDict(self, hostname):
		if not hostname in self._agents:
			return {}
		self._makegraphs(hostname)
		return self._agents[hostname].getDict()
