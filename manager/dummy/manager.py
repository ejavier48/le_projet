# -*- coding: utf-8 -*-
from agent import *

from notification import Notification

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

	"""
	_limits = {
		'RAM' : {
			'Ready' : .25,
			'Set' ; .35,
			'Go' : .30,
		},
		'CPU' : {
			'Ready' : 25,
			'Set' ; 50,
			'Go' : 80,
		},
		'HDD' : {
			'Ready' : .05,
			'Set' ; .10,
			'Go' : .35,
		},
	}
	"""
	"""
	_limit = {
		'label' : RAM', 
		'vals' : {
			'Ready' : .25,
			'Set' ; .35,
			'Go' : .30,
		},
	}
	"""

	_notifications = {}
	
	def __init__(self):

		self._numAgents = 0
		self._agents = {}
		self._limits = {'RAM': None, 'CPU': None, 'HDD': None, 'Time':300}

		self._new = []
		self._newNotification = []

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

				self._createRRD(hostname)

				self._getCPUsUse(hostname)

				self._getAgentInterFs(hostname)

				self._agents[hostname].setStatus(True)

				self._new.remove(hostname)

				return True

		except KeyError:
			print 'error _getBasicData'
			return False

	def _getNumCPUs(self, hostname):
		if True:#if True:#try:
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
		
		try:
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
						
						if True:#try:
							ret = rrdtool.update(nRRD, value) 
						else:#except:
							print 'problem update cpu _getCPUsUse'

						if self._limits['CPU'] is None:
							continue

						label = None

						for limit in self._limits['CPU']:
							valLimit = self._limits['CPU'][limit]
							if valLimit < cpusUse[i]:
								label = limit


						if label is not None:

							noti = Notification(hostname, 'CPU ' + str(i+1), label, self._limits['CPU'][label], cpusUse[i])
							
							if not i in self._notifications[hostname]['CPU']:
								self._notifications[hostname]['CPU'][i] = []
								self._notifications[hostname]['CPU'][i].append(noti)
								self._newNotification.append(noti.getReport())

							else:
								last = self._notifications[hostname]['CPU'][i][-1]
								diff = noti.getTimeReport() - last.getTimeReport()

								if self._limits['Time'] < diff or last.getLabel() != noti.getLabel():
									self._notifications[hostname]['CPU'][i].append(noti)
									self._newNotification.append(noti.getReport())	

			self._agents[hostname].setCPUsUse(cpusUse)

		except (KeyError, rrdtool.OperationalError) as e:
			print 'something wrong _getPerCPUs'

	def _getAgentInterFs(self, hostname):
		
		if not hostname in self._agents:
			return
		try:

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

		except (KeyError, rrdtool.OperationalError) as e:
			print 'Error, _getAgentInterFs'

	def _getAgentData(self, hostname):

		if not hostname in self._agents:
			return

		try:

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

						if self._limits['RAM'] is None:
							continue

						label = None

						for limit in self._limits['RAM']:
							
							valLimit = self._agents[hostname].getRAMSize() * self._limits['RAM'][limit]

							if valLimit < self._agents[hostname].getRAMUse():
								label = limit

						if label is not None:
													
							noti = Notification(hostname, 'RAM', label, self._limits['RAM'][label], self._agents[hostname].getRAMUse())
							flag = True

							if 0 < len(self._notifications[hostname]['RAM']):

								last = self._notifications[hostname]['RAM'][-1]
								diff = noti.getTimeReport() - last.getTimeReport()

								if  diff < self._limits['Time'] and last.getLabel() == noti.getLabel():
									flag = False

							if flag:
								self._notifications[hostname]['RAM'].append(noti)
								self._newNotification.append(noti.getReport())


						
					else:
						print 'error'
					i += 1

				self._agents[hostname].setStatus(True)

		except KeyError:
			print 'Exception _getAgentData'

	def _createRRD(self, hostname):

		try:
			for fname in self._names:

				s = self._fname[fname]

				if fname == self._names[4]:

					for i in range(self._agents[hostname].getNumInterFs()):

						name = s.format(hostname, i, 'rrd')

						ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', '10',
									'DS:in:COUNTER:600:0:U',
									'DS:out:COUNTER:600:0:U',
									'RRA:AVERAGE:0.5:2:80',
									'RRA:AVERAGE:0.5:1:100')

						if ret:
							print name, rrdtool.error()

				elif fname == self._names[5]:
					#create ram
					name = s.format(hostname, 'rrd')
					ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', '10',
									'DS:ram:GAUGE:600:0:U',
									'RRA:AVERAGE:0.5:2:100')
					if ret:
						print name, rrdtool.error()	

				elif fname == self._names[6]:
					#create cpu
					for i in range(self._agents[hostname].getNumCPUs()):

						name = s.format(hostname, i, 'rrd')

						ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', '10',
									'DS:load:GAUGE:600:0:100',
									'RRA:AVERAGE:0.5:2:100')

						if ret:
							print name, rrdtool.error()

				elif fname == self._names[7]:
					#hdd
					name = s.format(hostname, 'rrd')
					ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', '10',
									'DS:use:GAUGE:600:0:U',
									'RRA:AVERAGE:0.5:2:100')
					if ret:
						print name, rrdtool.error()	
				
				else:
					name = s.format(hostname, 'rrd')

					ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', '10',
									'DS:in:COUNTER:600:0:U',
									'DS:out:COUNTER:600:0:U',
									'RRA:AVERAGE:0.5:2:80',
									'RRA:AVERAGE:0.5:2:100')
					if ret:
						print name, rrdtool.error()	

		except (KeyError, rrdtool.OperationalError) as e:
			print 'Error'

	def _updateRRD(self):
		
		upImgs = 0

		while(1):
			
			upImgs+= 1

			hosts = self._agents.keys()
			
			for hostname in hosts:#get agent data
				
				try:

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
								if True:#try:
									ret = rrdtool.update(nRRD, value) 

								else:#except:
									print 'problem update for in out'
									break
							i += 1

						if upImgs == 4:
							self._makegraphs(hostname)



				except (KeyError) as e: #Preventing exception if agent is deleted while working on it
					print 'problem update'
					continue

				except rrdtool.OperationalError:
					print 'lallaa'
					continue

			if upImgs == 4:
				upImgs = 0

			sleep(1)

	def _makegraphs(self, hostname):

		if not hostname in self._agents: # preventing in case of agent deleted
			return

		try:

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
						'COMMENT:	Now		Min		Avg		Max//n',
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
					limit = self._limits['CPU']

					rVal = 0					
					sVal = 0					
					gVal = 0

					if limit:
						rVal = int(limit['Ready'])
						sVal = int(limit['Set'])
						gVal = int(limit['Go'])

					for i in range(self._agents[hostname].getNumCPUs()):

						name = self._fname[fname]
						nImg = name.format(hostname, i, 'png')
						nRRD = name.format(hostname, i, 'rrd')

						graph = [nImg,
							'--start', str(self._agents[hostname].getTime()),
							'--vertical-label=CPU ' + str(i) + ' Load',
							'--title=CPU Use',
							'--color', 'ARROW#009900',
							'--vertical-label', 'CPU Use(%)',
							'--lower-limit', '0',
							'--upper-limit', '100',					
							'DEF:load='+nRRD+':load:AVERAGE',

							'CDEF:umbral'+str(rVal)+'=load,'+str(rVal)+',LT,0,load,IF' if limit else None,
							'CDEF:umbral'+str(sVal)+'=load,'+str(sVal)+',LT,0,load,IF' if limit else None,
							'CDEF:umbral'+str(gVal)+'=load,'+str(gVal)+',LT,0,load,IF' if limit else None,

							'VDEF:loadMAX=load,MAXIMUM',
							'VDEF:loadMIN=load,MINIMUM',
							'VDEF:loadSTDEV=load,STDEV',
							'VDEF:loadLAST=load,LAST',
							'AREA:load#00FF00:CPU Load',

							'AREA:umbral'+str(rVal)+'#FFDF00:CPU Load greater than ' + str(rVal) + '%' if limit else None,
							'AREA:umbral'+str(sVal)+'#DD4E03:CPU Load greater than ' + str(sVal) + '%' if limit else None,
							'AREA:umbral'+str(gVal)+'#730000:CPU Load greater than ' + str(gVal) + '%' if limit else None,

							'HRULE:'+str(rVal)+'#F6D911:Umbral ' + str(1) + ' - ' + str(rVal) + '%' if limit else None,
							'HRULE:'+str(sVal)+'#FF5800:Umbral ' + str(rVal) + ' - ' + str(sVal) + '%' if limit else None,
							'HRULE:'+str(gVal)+'#FF0000:Umbral ' + str(sVal) + ' - ' + str(gVal) + '%' if limit else None,

							'GPRINT:loadMAX:%6.2lf %SMAX',
							'GPRINT:loadMIN:%6.2lf %SMIN',
							'GPRINT:loadSTDEV:%6.2lf %SSTDEV',
							'GPRINT:loadLAST:%6.2lf %SLAST'
						]

						graph = filter(None, graph)

						ret = rrdtool.graph(graph)

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

		except (KeyError, rrdtool.OperationalError) as e: #preventing exception if agent deleted
			print e
			print 'problem graphs'
			return 

	def _getAgentsData(self):
		try:
			devices = []
			for hostname in self._agents:
				devices.append(self._agents[hostname].getDict())
			return devices
		except (KeyError) as e:
			return self._getAgentsData()

	def addAgent(self, agent):

		hostname = agent.getHostName()
		if hostname in self._agents:
			return True
		self._numAgents += 1
		self._new.append(hostname)
		self._notifications[hostname] = {
			'RAM': [],
			'CPU': {},
			'HDD': [],
		}
		self._agents[hostname] = agent
		self._agents[hostname].setStatus(False)
		return self._getBasicData(hostname)

	def delAgent(self, hostname):
		try:

			if not hostname in self._agents:
				return True

			self._agents[hostname].setStatus(False)
			del self._agents[hostname]
			del self._notifications[hostname]
			self._numAgents -= 1
			path = './agents/' + hostname + '*'
			files = glob(path)
			for file in files:
				remove(file)
			return True

		except KeyError:
			return False

	def getDict(self):
		data = {}
		data['num_device'] = self._numAgents
		data['devices'] = self._getAgentsData()
		return data

	def getNotifications(self):
		n = len(self._newNotification)
		noti = self._newNotification[:n]

		self._newNotification = self._newNotification[n:]

		return noti

	def getAgentDict(self, hostname):

		if not hostname in self._agents:
			return {}

		return self._agents[hostname].getDict()

	def _checkLimType(self, label):
		return label in self._limits

	def setAllLimits(self, limits):

		for label in limits:
			if self._checkLimType(label):
				
				self._limits[label] = {}
				aux = limits[label]

				for val in aux:
					self._limits[label][val] = float(aux[val])

			else:
				return False

		return True

	def getLimits(self):
		return self._limits

	def setLimit(self, limit):

		if self._checkLimType(limit['label']):

			label = limit['label']
			self._limits[label] = {}

			aux = limit['vals']

			for lim in aux:
				self._limits[label][lim] = float(aux[lim])

			return True

		else:
			return False
