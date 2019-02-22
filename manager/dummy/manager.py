# -*- coding: utf-8 -*-
from agent import *
from pysnmp.hlapi import *

#from threading import Thread

class Manager():

	def __init__(self):
		self._numAgents = 0
		self._agents = {}

	def addAgent(self, agent):
		self._numAgents += 1
		self._agents[agent.getHostName()] = agent

	def delAgent(self, hostname):
		try:
			del self._agents[hostname]
			self._numAgents -= 1
			print 'delete'
			return True
		except:
			return False

	def showAgents(self):
		i = 1
		for host in self._agents:
			agent = self._agents[host]
			print 'Agent Nº: ' + str(i)
			print 'Hostname: ' + str(agent.getHostName())
			print 'SNMP version: ' +  str(agent.getVersion())
			print 'Port: ' + str(agent.getPort())
			print 'Community: ' + str(agent.getCommunity())
			flag = agent.getStatus()
			print 'Status: ' + 'Up' if flag else 'Down'
			if flag:
				print 'Information: ' + agent.getInfo()
				print 'Localization: ' + str(agent.getLocalization())
				print 'Node Name: ' + str(agent.getNode())
				print 'Contact: ' + str(agent.getContact())
				numInterFs = agent.getNumInterFs()
				print 'Interfaces: ' + str(numInterFs)
				interfaces =  agent.getInterfaces()
				i = 1
				for interface in interfaces:
					print '\tInterface Nº ' + str(i)
					print '\tName: ' + interface['name']
					print '\tStatus: ' + interface['status']
					i += 1
				print 'UpTime: ' + agent.getUpTimeF()

			i += 1

class ManagerSNMP(Manager):
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
		'OutOctInterFs'	: '.2.2.1.16'
	}
	
	def __init__(self):
		Manager.__init__(self)

	def getBasicData(self, hostname):
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
				self._agents[hostname].setStatus(False)
				print eIndi
				return False
			elif eStatus:
				print eIndex, eStatus
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
				return True
		except:
			return False

	def _getAgentInterFs(self, hostname):
		flag = True
		try:
			walk = nextCmd(SnmpEngine(),
				CommunityData(self._agents[hostname].getCommunity()),
				UdpTransportTarget((hostname, self._agents[hostname].getPort())),
				ContextData(), 
				ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['NameInterFs'])),
				ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['StatusInterFs'])),
				)
			n = self._agents[hostname].getNumInterFs()
			interfaces = []
			for i in range(n):
				eIndi, eStatus, eIndex, vBinds = next(walk)
				if eIndi:
					print eIndi
					flag = False
				elif eStatus:
					print eIndex, eStatus
					flag = False
				else:
					data = 0
					interface = {}
					for varBind in vBinds:
						a = [x.prettyPrint() for x in varBind]
						if data == 0:
							interface['name'] = a[1]
							data += 1
						elif data == 1:
							interface['status'] = 'Up' if a[1] == '1' else 'Down'
							data += 1
						else:
							print 'Error'
					interfaces.append(interface)
			self._agents[hostname].setInterfaces(interfaces)
		except:
			flag = False
		return flag

	def getAgentData(self, hostname):
		self._agents[hostname].setStatus(False)
		try:
			eIndi, eStatus, eIndex, vBinds = next(
				getCmd(SnmpEngine(),
					CommunityData(self._agents[hostname].getCommunity()), 
					UdpTransportTarget((hostname, self._agents[hostname].getPort())),
					ContextData(),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['UpTime'])))
			)
			if eIndi:
				print eIndi
				return
			elif eStatus:
				print eIndex, eStatus
				return
			else:
				i = 0
				for varBind in vBinds:
					a = [x.prettyPrint() for x in varBind]
					self._agents[hostname].setUpTime(int(a[1]))
					#if i == 0:
					#	self._agents[hostname].setUpTime(int(a[1]))
					#	i += 1
					#elif i == 1:
					#	self._agents[hostname].setNumInterFs(int(a[1]))
					#	i += 1
					#else:
					#	print "Error"
				self._agents[hostname].setStatus(self._getAgentInterFs(hostname))
		except:
			print "Error in data"

	def getAgentsData(self):
		for host in self._agents:
			self.getAgentData(host)

	def getDict(self):
		self.getAgentsData()
		data = {}
		data['num_device'] = self._numAgents
		data['devices'] = []
		for host in self._agents:
			agent = self._agents[host]
			data['devices'].append(agent.getDict())
		return data

def main():
	hosts = []
	manager = ManagerSNMP()
	host = raw_input()
	hosts.append(host)
	version = raw_input()
	port = int(raw_input())
	community = raw_input()
	manager.addAgent(Agent(host, version, port, community))
	manager.getBasicData(host)
	i = 0
	while(i<10):
		manager.getAgentsData()
		manager.showAgents()
		i += 1
	return



if __name__ == '__main__':
	main()