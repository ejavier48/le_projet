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
		'MIB'			: '1.3.6.1.2.1',
		'Info'			: '.1.1.0',
		'UpTime'		: '.25.1.1.0',
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
		'RAMInfo'		: '.25.2.2.0',
		'RAMUse'		: '.25.2.3.1.6.1',
		'CPUNum'		: '.25.3.3.1.1',
		'CPUUse'		: '.25.3.3.1.2',
	}

	_fname = {
		'ip'	: './agents/{}_ip.{}',
		'icmp'	: './agents/{}_icmp.{}',
		'tcp'	: './agents/{}_tcp.{}',
		'udp'	: './agents/{}_udp.{}',
		'infs'	: './agents/{}_interface{}.{}',
		'ram'	: './agents/{}_ram.{}',
		'cpu'	: './agents/{}_cpu{}.{}',
		'hdd'	: './agents/{}_hdd.{}',

	}

	_names = [
		'ip',
		'icmp',
		'tcp',
		'udp',
		'infs',
		'ram',
		'cpu',
		'hdd',
	]
	
	def __init__(self):
		self._agents = {}
		self._new = []
		self._numAgents = 0
		self._thread = Thread(target = self._updateRRD, args = ())
		self._thread.daemon = True
		self._thread.start()

	def _getBasicData(self, hostname):
		if True:#try:
			eIndi, eStatus, eIndex, vBinds = next(
				getCmd(SnmpEngine(),
					CommunityData(self._agents[hostname].getCommunity()), 
					UdpTransportTarget((hostname, self._agents[hostname].getPort())),
					ContextData(),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['Info'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['Contact'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['NodeName'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['Localization'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['NumInterFs'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['RAMInfo'])),
					ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['RAMUse'])),)
			)
			if eIndi:
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
					elif i == 5:
						self._agents[hostname].setRAMSize(int(a[1]))
					elif i == 6:
						self._agents[hostname].setRAMUse(int(a[1]))
					else:
						print 'Error'
					i += 1

				self._getNumCPUs(hostname)
				print 'num cpus'

				self._createRRD(hostname)
				print 'create'

				self._getCPUsUse(hostname)
				print 'cpu use'

				self._getAgentInterFs(hostname)
				print 'interFs'

				self._agents[hostname].setStatus(True)
				print 'status'

				self._new.remove(hostname)
				print 'finish _getBasicData'

				return True
		else:#except:
			print 'error _getBasicData'
			return False

	def _getNumCPUs(self, hostname):
		if True:#try:
			walk = nextCmd(SnmpEngine(),
				CommunityData(self._agents[hostname].getCommunity()),
				UdpTransportTarget((hostname, self._agents[hostname].getPort())),
				ContextData(), 
				ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['CPUNum'])),
			)

			flag = True
			countCPUs = 0

			while(flag):
				
				eIndi, eStatus, eIndex, vBinds = next(walk)

				if eIndi:
					print eIndi, i
					continue

				elif eStatus:
					print eIndex, eStatus, i
					continue

				else:

					for varBind in vBinds:
						a = [x.prettyPrint() for x in varBind]
						if a[1] != '0.0':
							flag = False
							break
						countCPUs += 1

			self._agents[hostname].setNumCPUs(countCPUs)
		else:#xcept:
			print 'error getNumCPUs'

	def _getCPUsUse(self, hostname):

		if not hostname in self._agents:
			return

		if True:#try:
			walk = nextCmd(SnmpEngine(),
				CommunityData(self._agents[hostname].getCommunity()),
				UdpTransportTarget((hostname, self._agents[hostname].getPort())),
				ContextData(), 
				ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['CPUUse'])),
			)

			
			cpus = self._agents[hostname].getNumCPUs()
			cpusUse = [0] * cpus

			for i in range(cpus):
				
				eIndi, eStatus, eIndex, vBinds = next(walk)

				if eIndi:
					print eIndi, i
					continue

				elif eStatus:
					print eIndex, eStatus, i
					continue

				else:

					for varBind in vBinds:
						a = [x.prettyPrint() for x in varBind]
						cpusUse[i] = int(a[1])

						fn = self._names[6]
						nRRD = self._fname[fn].format(hostname, i, 'rrd')
						value = ':'.join(['N', a[1]])
						
						try:
							ret = rrdtool.update(nRRD, value) 
						except:
							print 'problem update cpu _getCPUsUse'

			self._agents[hostname].setCPUsUse(cpusUse)

		else:#except:
			print 'something wrong _getPerCPUs'

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
			ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutOctInterFs']))
		)
		
		n = self._agents[hostname].getNumInterFs()

		interfaces = []
		
		s = self._fname[self._names[4]]

		for i in range(n):

			eIndi, eStatus, eIndex, vBinds = next(walk)

			if eIndi:
				print eIndi, i
				continue

			elif eStatus:
				print eIndex, eStatus, i
				continue

			else:

				data = 0
				interface = {}

				for varBind in vBinds:
					
					a = [x.prettyPrint() for x in varBind]
					#print a

					if data == 0:
						if a[1].find('0x') == 0:
							a[1] = a[1][2:]
							interface['name'] = bytearray.fromhex(a[1]).decode()
						else:
							interface['name'] = a[1]
					elif data == 1:
						interface['status'] = 'Up' if a[1] == '1' else 'Down'

					elif data == 2:
						inData = int(a[1])

					elif data == 3:
						
						outData = int(a[1])
						
						nRRD = s.format(hostname, i, 'rrd')
						value = ':'.join(['N', str(inData), str(outData)])
						
						ret = rrdtool.update(nRRD, value)

					else:
						print 'Error', i

					data += 1

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
				ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['UpTime'])),
				ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['RAMUse'])),)
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
				if i == 0:
					self._agents[hostname].setUpTime(int(a[1]))
				elif i == 1:
					self._agents[hostname].setRAMUse(int(a[1]))
					fn = self._names[5]
					nRRD = self._fname[fn].format(hostname, 'rrd')
					value = ':'.join(['N', a[1]])
					if True:#try:
						ret = rrdtool.update(nRRD, value) 
					else:#except:
						print 'problem update ram _getAgentData'
				else:
					print 'error'
				i += 1

			self._agents[hostname].setStatus(True)
		
		return

	def _createRRD(self, hostname):

		for fname in self._names:

			s = self._fname[fname]
			print len(self._names)
			
			if fname == self._names[4]:

				print fname

				for i in range(self._agents[hostname].getNumInterFs()):

					name = s.format(hostname, i, 'rrd')

					ret = rrdtool.create(name, 
								'--start', 'N', 
								'--step', '10',
								'DS:in:COUNTER:600:U:U',
								'DS:out:COUNTER:600:U:U',
								'RRA:AVERAGE:0.5:5:80',
								'RRA:AVERAGE:0.5:1:100')

					if ret:
						print name, rrdtool.error()

			elif fname == self._names[5]:
				print fname
				#create ram
				name = s.format(hostname, 'rrd')
				ret = rrdtool.create(name, 
								'--start', 'N', 
								'--step', '10',
								'DS:ram:GAUGE:600:U:U',
								'RRA:AVERAGE:0.5:5:100')
				if ret:
					print name, rrdtool.error()	

			elif fname == self._names[6]:
				print fname
				#create cpu
				for i in range(self._agents[hostname].getNumCPUs()):

					name = s.format(hostname, i, 'rrd')

					ret = rrdtool.create(name, 
								'--start', 'N', 
								'--step', '10',
								'DS:load:GAUGE:600:U:100',
								'RRA:AVERAGE:0.5:5:100')

					if ret:
						print name, rrdtool.error()

			elif fname == self._names[7]:
				print fname
				#hdd
				name = s.format(hostname, 'rrd')
				ret = rrdtool.create(name, 
								'--start', 'N', 
								'--step', '10',
								'DS:use:GAUGE:600:U:U',
								'RRA:AVERAGE:0.5:5:100')
				if ret:
					print name, rrdtool.error()	
			
			else:
				print fname
				name = s.format(hostname, 'rrd')

				ret = rrdtool.create(name, 
								'--start', 'N', 
								'--step', '10',
								'DS:in:COUNTER:600:U:U',
								'DS:out:COUNTER:600:U:U',
								'RRA:AVERAGE:0.5:5:80',
								'RRA:AVERAGE:0.5:1:100')
				if ret:
					print name, rrdtool.error()	

	def _updateRRD(self):
		upImgs = 0
		while(1):
			upImgs+= 1

			hosts = self._agents.keys()
			for hostname in hosts:#get agent data
				if True:

					if not hostname in self._agents: # check if agent was deleted
						continue # if deleted go next

					if hostname in self._new:
						continue

					self._getAgentData(hostname) #update time up

					#print 'status update', self._agents[hostname].getStatus()

					if not self._agents[hostname].getStatus(): #if agent is not active, go to next
						continue

					self._getCPUsUse(hostname)

					self._getAgentInterFs(hostname)

					eIndi, eStatus, eIndex, vBinds = next(
						getCmd(SnmpEngine(),
							CommunityData(self._agents[hostname].getCommunity()), 
							UdpTransportTarget((hostname, self._agents[hostname].getPort())),
							ContextData(),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InIP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutIP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InICMP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutICMP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InTCP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutTCP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['InUDP'])),
							ObjectType(ObjectIdentity(self._querys['MIB'] + self._querys['OutUDP'])))
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

								fn = self._names[(i/2)]
								nRRD = self._fname[fn].format(hostname, 'rrd')

								#Prevent exception if agents and files were deleted
								try:
									ret = rrdtool.update(nRRD, value) 

								except:
									print 'problem update for in out'
									break
							i += 1

						if upImgs == 9:
							self._makegraphs(hostname)



				else: #Preventing exception if agent is deleted while working on it
					print 'problem update'
					continue

			if upImgs == 9:
				upImgs = 0

			sleep(.5)

	def _makegraphs(self, hostname):
		if not hostname in self._agents: # preventing in case of agent deleted
			return 

		if True:#try:
			for fname in self._fname:

				if fname == self._names[4]:

					for i in range(self._agents[hostname].getNumInterFs()):

						name = self._fname[fname]
						nImg = name.format(hostname, i, 'png')
						nRRD = name.format(hostname, i, 'rrd')

						ret = rrdtool.graph(nImg,
									'--start', str(self._agents[hostname].getTime()),
									'--vertical-label=Bytes/s',
									'DEF:in='+nRRD+':in:AVERAGE',
									'DEF:out='+nRRD+':out:AVERAGE',
									'LINE1:in#0F0F0F:In Traffic',
									'LINE2:out#000FFF:Out Traffic')

				elif fname == self._names[5]:
					#ram
					name = self._fname[fname]
					nImg = name.format(hostname, 'png')
					nRRD = name.format(hostname, 'rrd')

					ret = rrdtool.graph(nImg,
						'--start', str(self._agents[hostname].getTime()),
						'--vertical-label=Megabytes',
						'--title=RAM Use',
						'--color', 'ARROW#009900',
						'--vertical-label', 'RAM Use MB',
						'DEF:ram='+nRRD+':ram:AVERAGE',
						'AREA:ram#00FF00:RAM Use',
						'LINE1:30',
						'AREA:5#ff000022:stack',
						'VDEF:RAMlast=ram,LAST',
						'VDEF:RAMmin=ram,MINIMUM',
						'VDEF:RAMavg=ram,AVERAGE',
						'VDEF:RAMmax=ram,MAXIMUM',
						'COMMENT:		Now		Min		Avg		Max//n',
						'GPRINT:RAMlast:%12.0lf%s',
						'GPRINT:RAMmin:%10.0lf%s',
						'GPRINT:RAMavg:%13.0lf%s',
						'GPRINT:RAMmax:%13.0lf%s',
						'VDEF:a=ram,LSLSLOPE',
						'VDEF:b=ram,LSLINT',
						'CDEF:avg2=ram,POP,a,COUNT,*,b,+',
						'LINE2:avg2#FFBB00')

				elif fname == self._names[6]:
					#cpu
					for i in range(self._agents[hostname].getNumCPUs()):

						name = self._fname[fname]
						nImg = name.format(hostname, i, 'png')
						nRRD = name.format(hostname, i, 'rrd')

						ret = rrdtool.graph(nImg,
									'--start', str(self._agents[hostname].getTime()),
									'--vertical-label=CPU Load',
									'--title=CPU Use',
									'--color', 'ARROW#009900',
									'--vertical-label', 'CPU Use(%)',
									'--lower-limit', '0',
									'--upper-limit', '100',
									'DEF:load='+nRRD+':load:AVERAGE',
									'AREA:load#00FF00:CPU Load',
									'LINE1:30',
									'AREA:5#ff000022:stack',
									'VDEF:CPUlast=load,LAST',
									'VDEF:CPUmin=load,MINIMUM',
									'VDEF:CPUavg=load,AVERAGE',
									'VDEF:CPUmax=load,MAXIMUM',
									'COMMENT:		Now		Min		Avg		Max//n',
									'GPRINT:CPUlast:%12.0lf%s',
									'GPRINT:CPUmin:%10.0lf%s',
									'GPRINT:CPUavg:%13.0lf%s',
									'GPRINT:CPUmax:%13.0lf%s',
									'VDEF:a=load,LSLSLOPE',
									'VDEF:b=load,LSLINT',
									'CDEF:avg2=load,POP,a,COUNT,*,b,+',
									'LINE2:avg2#FFBB00' )
				elif fname == self._names[7]:
					None
					#hdd
				else:

					name = self._fname[fname]
					nImg = name.format(hostname, 'png')
					nRRD = name.format(hostname, 'rrd')

					ret = rrdtool.graph(nImg,
										'--start', str(self._agents[hostname].getTime()),
										'--vertical-label=Bytes/s',
										'DEF:in='+nRRD+':in:AVERAGE',
										'DEF:out='+nRRD+':out:AVERAGE',
										'LINE1:in#0F0F0F:In Traffic',
										'LINE2:out#000FFF:Out Traffic')

		else:#except: #preventing exception if agent deleted
			print 'problem graphs'
			return 

	def _getAgentsData(self):
		devices = []
		for hostname in self._agents:
			devices.append(self._agents[hostname].getDict())
		return devices

	def addAgent(self, agent):
		hostname = agent.getHostName()
		if hostname in self._agents:
			return True
		self._numAgents += 1
		self._new.append(hostname)
		self._agents[hostname] = agent
		self._agents[hostname].setStatus(False)
		return self._getBasicData(hostname)

	def delAgent(self, hostname):
		try:
			self._agents[hostname].setStatus(False)
			del self._agents[hostname]
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
		return self._agents[hostname].getDict()
