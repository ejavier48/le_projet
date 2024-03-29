# -*- coding: utf-8 -*-
from agent import *

from notification import Notification

from pysnmp.hlapi import *

from glob import glob

from os import remove

from time import sleep, mktime, time, strftime, localtime

from datetime import datetime 

from threading import Thread

from math import ceil

import tempfile

#smtp
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import rrdtool

class ManagerSNMP():
	_querys = {
		'MIB'			: '1.3.6.1.2.1',
		'UCD'			: '1.3.6.1.4.1.2021',
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
		'HDDSize'		: '.9.1.6.2',
		'HDDUse'		: '.9.1.8.2',
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
		self._labels = ['Ready', 'Set', 'Go']
		self._contador = 0
		self._newNotification = []

		self._threads = {}

		self._mailsender = "ejsanchezg96@gmail.com"
		self._mailreceip = ""
		self._mailserver = 'smtp.gmail.com: 587'
		self._password = 'android15'#add self._password
		'''
		self._thread = Thread(target = self._updateRRD, args = ())
		self._thread.daemon = True
		self._thread.start()
		'''

	def _getBasicData(self, hostname):
		if self._agents[hostname].getCommunity() == 'variation/virtualtable':
			self._createRRD(hostname)
			self._agents[hostname].setNumInterFs(3)
			self._getAgentInterFs(hostname)
			print self._agents[hostname].getDict()
			return True

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

	def _sendMail(self, noti):
		try:
			print 'Notification'
			print self._mailreceip
			if not (noti.getLabel() in ['Go', 'Failure Detected', 'Failure Ended']):
				print 'Not Go'
				return
			self._makegraphs(noti.getHostName())

			imgPath = noti.getFile()
			msg = MIMEMultipart()
			msg['Subject'] = ' '.join([ 'Deteccion de falla 4cm2 Equipo 1', noti.getResource(), 'Surpassed Limit'])
			msg['From'] = self._mailsender
			msg['To'] = self._mailreceip
			fp = open( imgPath, 'rb')
			img = MIMEImage(fp.read(), )
			img.add_header('Content-Disposition', 'attachment; filename= %s' % noti.getResource())
			fp.close()
			msg.attach(img)
			msg.attach(MIMEText(str(noti.getReport()), 'plain'))
			mserver = smtplib.SMTP(self._mailserver)
			mserver.starttls()
			# Login Credentials for sending the mail
			mserver.login(self._mailsender, self._password)
			mserver.sendmail(self._mailsender, self._mailreceip, msg.as_string())
			mserver.quit()
		except KeyError:
			print 'Error'

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

						for limit in self._labels:
							valLimit = self._limits['CPU'][limit]
							if valLimit < cpusUse[i]:
								label = limit


						if label is not None:

							noti = Notification(hostname, 'CPU ' + str(i+1), label, self._limits['CPU'][label], cpusUse[i], self._fname[fn].format(hostname, i, 'png'))
							
							if not i in self._notifications[hostname]['CPU']:
								self._notifications[hostname]['CPU'][i] = []
								self._notifications[hostname]['CPU'][i].append(noti)
								self._newNotification.append(noti.getReport())
								self._sendMail(noti)

							else:
								last = self._notifications[hostname]['CPU'][i][-1]
								diff = noti.getTimeReport() - last.getTimeReport()

								if self._limits['Time'] < diff :#or last.getLabel() != noti.getLabel():
									self._notifications[hostname]['CPU'][i].append(noti)
									self._newNotification.append(noti.getReport())	
									self._sendMail(noti)

			self._agents[hostname].setCPUsUse(cpusUse)

		except (KeyError, rrdtool.OperationalError) as e:
			print 'something wrong _getPerCPUs'

	def _getAgentInterFs(self, hostname):
		
		if not hostname in self._agents:
			return
		already = True
		if True:#try:

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
			case = 2

			for i in range(n):
				if i != case:
					print i
					continue

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
							i = 0
							outData = int(a[1]) 
							
							nRRD = s.format(hostname, i, 'rrd')
							rrdtool.tune(nRRD, '--alpha', '0.1')
							rrdtool.tune(nRRD,'--beta', '0.8')
							rrdtool.tune(nRRD,'--gamma', '0.1')
							fn = s.format(hostname, i, 'png')
							value = ':'.join(['N', str(inData)])#, str(outData)])
							
							ret = rrdtool.update(nRRD, value)
							flag = self._checkAberration(nRRD, hostname)
							print 'flag', flag
							if flag == 1:
								noti = Notification(hostname, 'Interface ' + str(i+1), 'Failure Detected', None, None, fn)
								self._sendMail(noti)
								already = False
							elif flag == 2:
								noti = Notification(hostname, 'Interface ' + str(i+1), 'Failure Ended', None, None, fn)
								self._sendMail(noti)
								already = True
						else:
							print 'Error', i

						data += 1

					interfaces.append(interface)

			self._agents[hostname].setInterfaces(interfaces)

		#except (KeyError, rrdtool.OperationalError) as e:
		#	print 'Error, _getAgentInterFs'

	def _getAgentData(self, hostname):

		if not hostname in self._agents:
			return

		if True:#try:

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

						if not self._agents[hostname].getStatus():
							self._agents[hostname].setTime()
							self._getBasicData(hostname)
							print 'Changes Status'

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

						for limit in self._labels:
							
							valLimit = self._agents[hostname].getRAMSize() * self._limits['RAM'][limit]

							if valLimit < self._agents[hostname].getRAMUse():
								label = limit

						if label is not None:
													
							noti = Notification(hostname, 'RAM', label, self._limits['RAM'][label], self._agents[hostname].getRAMUse(), self._fname[fn].format(hostname, 'png'))
							flag = True

							if 0 < len(self._notifications[hostname]['RAM']):

								last = self._notifications[hostname]['RAM'][-1]
								diff = noti.getTimeReport() - last.getTimeReport()

								if  diff < self._limits['Time'] :#and last.getLabel() == noti.getLabel():
									flag = False

							if flag:
								print 'new ram'
								self._notifications[hostname]['RAM'].append(noti)
								self._newNotification.append(noti.getReport())
								self._sendMail(noti)
						
					else:
						print 'error'
					i += 1

				self._agents[hostname].setStatus(True)
				if self._agents[hostname].getOS() == 'linux':
					self._getAgentHDDLin(hostname)
				else:
					None

		#except KeyError:
		#	print 'Exception _getAgentData'

	def _getAgentHDDLin(self, hostname):

		if not hostname in self._agents:
			return

		try:

			eIndi, eStatus, eIndex, vBinds = next(
				getCmd(SnmpEngine(),
					CommunityData(self._agents[hostname].getCommunity()), 
					UdpTransportTarget((hostname, self._agents[hostname].getPort())),
					ContextData(),
					ObjectType(ObjectIdentity(self._querys['UCD'] + self._querys['HDDSize'])),
					ObjectType(ObjectIdentity(self._querys['UCD'] + self._querys['HDDUse'])),)
				)

			if eIndi:
				print eIndi
				#self._agents[hostname].setStatus(False)

			elif eStatus:
				print eIndex, eStatus
				#self._agents[hostname].setStatus(False)

			else:
				i = 0
				for varBind in vBinds:
					a = [x.prettyPrint() for x in varBind]

					if i == 0:
						self._agents[hostname].setHDDSize(int(a[1]))

					elif i == 1:
						self._agents[hostname].setHDDUse(int(a[1]))

						fn = self._names[7]
						nRRD = self._fname[fn].format(hostname, 'rrd')
						value = ':'.join(['N', a[1]])

						try:
							ret = rrdtool.update(nRRD, value) 
						except:
							print 'problem update HDD _getAgentHDDLin'

						if self._limits['HDD'] is None:
							continue

						label = None

						for limit in self._labels:
							
							valLimit = self._agents[hostname].getHDDSize() * self._limits['HDD'][limit]

							if valLimit < self._agents[hostname].getHDDUse():
								label = limit

						if label is not None:
													
							noti = Notification(hostname, 'HDD', label, self._limits['HDD'][label], self._agents[hostname].getHDDUse(), self._fname[fn].format(hostname, 'png'))
							flag = True

							if 0 < len(self._notifications[hostname]['HDD']):

								last = self._notifications[hostname]['HDD'][-1]
								diff = noti.getTimeReport() - last.getTimeReport()

								if  diff < self._limits['Time']:# and last.getLabel() == noti.getLabel():
									flag = False

							if flag:
								self._notifications[hostname]['HDD'].append(noti)
								self._newNotification.append(noti.getReport())
								self._sendMail(noti)

					else:
						print 'error HDD', i
					i += 1

		except:
			print 'Exception _getAgentHDDLin'

	def _createRRD(self, hostname):

		self._step = 5
		self._rrdSize = 500/5
		self._predict = 250/5
		self._season = 125/5

		if True:#try:
			for fname in self._names:

				s = self._fname[fname]

				if fname == self._names[4]:

					if self._agents[hostname].getCommunity() == 'variation/virtualtable':
						continue

					for i in range(self._agents[hostname].getNumInterFs()):

						name = s.format(hostname, i, 'rrd')

						ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', str(self._step),
									'DS:in:COUNTER:600:0:U',
									'RRA:AVERAGE:0.5:1:' + str(self._rrdSize),
									'RRA:HWPREDICT:' + str(self._predict) + ':0.5:0.025:' + str(self._season) + ':3',
									'RRA:SEASONAL:' + str(self._season*2) + ':0.1:2',
									'RRA:DEVSEASONAL:' + str(self._season*2) + ':0.1:2',
									'RRA:DEVPREDICT:' + str(self._predict) + ':4',
									'RRA:FAILURES:' + str(self._season*2) + ':5:5:4',
									'DS:out:COUNTER:600:0:U',
									'RRA:AVERAGE:0.5:1:' + str(self._rrdSize))

						if ret:
							print name, rrdtool.error()

				elif fname == self._names[5]:
					#create ram
					name = s.format(hostname, 'rrd')
					ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', str(self._step),
									'DS:ram:GAUGE:600:0:U',
									'RRA:AVERAGE:0.5:2:' + str(self._rrdSize))
					if ret:
						print name, rrdtool.error()	

				elif fname == self._names[6]:
					#create cpu
					for i in range(self._agents[hostname].getNumCPUs()):

						name = s.format(hostname, i, 'rrd')

						ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', str(self._step),
									'DS:load:GAUGE:600:0:100',
									'RRA:AVERAGE:0.5:2:' + str(self._rrdSize))

						if ret:
							print name, rrdtool.error()

				elif fname == self._names[7]:
					#hdd
					name = s.format(hostname, 'rrd')
					ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', str(self._step),
									'DS:hdd:GAUGE:600:0:U',
									'RRA:AVERAGE:0.5:2:' + str(self._rrdSize))
					if ret:
						print name, rrdtool.error()	
				
				else:
					name = s.format(hostname, 'rrd')

					ret = rrdtool.create(name, 
									'--start', 'N', 
									'--step', str(self._step),
									'DS:in:COUNTER:600:0:U',
									'DS:out:COUNTER:600:0:U',
									'RRA:AVERAGE:0.5:2:' + str(self._rrdSize),
									'RRA:AVERAGE:0.5:2:' + str(self._rrdSize))
					if ret:
						print name, rrdtool.error()	

		else:#except (KeyError, rrdtool.OperationalError) as e:
			print 'Error'

	def _updateRRD(self, hostname):
		
		upImgs = 0
		times = 0
		already = True

		while(1):
				
			if True:#try:

				upImgs+= 1

				if not hostname in self._agents: # check if agent was deleted
					break # if deleted go next

				
				if self._agents[hostname].getCommunity() == 'variation/virtualtable':
					self._getAgentInterFs(hostname)
					if upImgs == 10:
						times += 1
						self._makegraphs(hostname)
						upImgs = 0
						if times == 100:
							self._agents[hostname].sumTime(1)
							times = 0
					continue

				self._getAgentData(hostname) #update time up


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

					if upImgs == self._step:
						times += 1
						self._makegraphs(hostname)
						upImgs = 0
						if times == 100:
							self._agents[hostname].sumTime(int(ceil(self._rrdSize*1)))
							times = 0

			#except (KeyError) as e: #Preventing exception if agent is deleted while working on it
			#	print 'problem update'
			#	continue
			#except rrdtool.OperationalError:
			#	print 'lallaa ' + hostname
			#	continue

			sleep(15)

	def _makegraphs(self, hostname):

		if not hostname in self._agents: # preventing in case of agent deleted
			return

		if True:#try:

			for fname in self._fname:

				if fname == self._names[4]:

					if self._agents[hostname].getCommunity() == 'variation/virtualtable':

						name = self._fname[fname]
						nImg = name.format(hostname, 0, 'png')
						nRRD = name.format(hostname, 0, 'rrd')

						#def gen_image(rrdpath, pngpath, fname, width, height, begdate, enddate):
						"""
						Generates png file from rrd database:
						rrdpath - the path where rrd is located
						pngpath - the path png file should be created in
						fname - rrd file name, png file will have the same name .png extention
						width - chart area width
						height - chart area height
						begdate - unixtime
						enddate - unixtime
						"""
						enddate = rrdtool.last(nRRD)
						begdate = enddate - 30000
						width = '500'
						height = '200'


						title="Deteccion de comportamiento anomalo"
						#fname=nRRD
						pngpath = nImg
						endDate = rrdtool.last(nRRD) #ultimo valor del XML
						begDate = endDate - 600
						DatosAyer=begDate - 86400
						FinAyer=endDate - 86400
						#rrdtool.tune(rrdname, '--alpha', '0.1')
						ret = rrdtool.graph(pngpath,
						                        '--start', str(begDate), '--end', str(endDate), '--title=' + title,
						                        "--vertical-label=Bytes/s",
						                        '--slope-mode',
						                        "DEF:obs=" + nRRD + ":inoctets:AVERAGE",
						                        "DEF:obsAyer=" + nRRD + ":inoctets:AVERAGE:start="+str(DatosAyer)+":end="+str(FinAyer),
						                        "DEF:pred=" + nRRD + ":inoctets:HWPREDICT",
						                        "DEF:dev=" + nRRD + ":inoctets:DEVPREDICT",
						                        "DEF:fail=" + nRRD + ":inoctets:FAILURES",
						                        'SHIFT:obsAyer:86400',
						                    	#"RRA:DEVSEASONAL:1d:0.1:2",
						                    	#"RRA:DEVPREDICT:5d:5",
						                    	#"RRA:FAILURES:1d:7:9:5""
						                        "CDEF:scaledobs=obs,8,*",
						                        "CDEF:scaledobsAyer=obsAyer,8,*",
						                        "CDEF:upper=pred,dev,2,*,+",
						                        "CDEF:lower=pred,dev,2,*,-",
						                        "CDEF:scaledupper=upper,8,*",
						                        "CDEF:scaledlower=lower,8,*",
						                        "CDEF:scaledpred=pred,8,*",
						                    "TICK:fail#FDD017:1.0: Fallas",
						                    "AREA:scaledobsAyer#9C9C9C:Ayer",
						                    "LINE3:scaledobs#00FF00:In traffic",
						                    "LINE1:scaledpred#FF00FF:Prediccion",
						                    #"LINE1:outoctets#0000FF:Out traffic",
						                    "LINE1:scaledupper#ff0000:Upper Bound Average bits in",
						                    "LINE1:scaledlower#0000FF:Lower Bound Average bits in")
						break


					for i in range(self._agents[hostname].getNumInterFs()):

						name = self._fname[fname]
						nImg = name.format(hostname, i, 'png')
						nRRD = name.format(hostname, i, 'rrd')
						graph = [nImg,
									'--start', str(self._agents[hostname].getTime()),
									'--vertical-label=Bytes/s',
									'DEF:in='+nRRD+':in:AVERAGE',
									'DEF:out='+nRRD+':out:AVERAGE',
									'DEF:pred='+nRRD+':in:HWPREDICT',
									'DEF:dev='+nRRD+':in:DEVPREDICT',
									'DEF:fail='+nRRD+':in:FAILURES',
									'CDEF:sin=in,8,*',
									'CDEF:sout=out,8,*',
									'CDEF:upper=pred,dev,2,*,+',
									'CDEF:lower=pred,dev,2,*,-',
									'CDEF:uscale=upper,8,*',
									'CDEF:lscale=lower,8,*',
									'CDEF:spred=pred,8,*',
									'TICK:fail#FDD017:1.0:Failures',
									'LINE3:sin#00FF00:In Traffic',
									'LINE3:spred#FF00FF:Prediction',
									'LINE1:uscale#FF0000:Upper Bound',
									'LINE1:lscale#0000FF:Lower Bound',
									'LINE3:sout#000000:Out Traffic']
						ret = rrdtool.graph(graph)

				elif fname == self._names[5]:
					#ram
					name = self._fname[fname]
					nImg = name.format(hostname, 'png')
					nRRD = name.format(hostname, 'rrd')

					limit = self._limits['RAM']

					rVal = 0					
					sVal = 0					
					gVal = 0

					if limit:
						rVal = int(limit['Ready'] * self._agents[hostname].getRAMSize())
						sVal = int(limit['Set'] * self._agents[hostname].getRAMSize())
						gVal = int(limit['Go'] * self._agents[hostname].getRAMSize())
						rPer = int(limit['Ready'] * 100)
						sPer = int(limit['Set'] * 100)
						gPer = int(limit['Go'] * 100)

					graph = [nImg,
						'--start', str(self._agents[hostname].getTime()),
						'--vertical-label=Megabytes',
						'--title=RAM Use',
						'--color', 'ARROW#009900',
						'--vertical-label', 'RAM Use MB',
						'DEF:ram='+nRRD+':ram:AVERAGE',

						'CDEF:umbral'+str(rPer)+'=ram,'+str(rVal)+',LT,0,ram,IF' if limit else None,
						'CDEF:umbral'+str(sPer)+'=ram,'+str(sVal)+',LT,0,ram,IF' if limit else None,
						'CDEF:umbral'+str(gPer)+'=ram,'+str(gVal)+',LT,0,ram,IF' if limit else None,

						'VDEF:ramMAX=ram,MAXIMUM',
						'VDEF:ramMIN=ram,MINIMUM',
						'VDEF:ramSTDEV=ram,STDEV',
						'VDEF:ramLAST=ram,LAST',
						'AREA:ram#00FF00:RAM Use',

						'AREA:umbral'+str(rPer)+'#FFDF00:RAM Use greater than ' + str(rPer) + '%' if limit else None,
						'AREA:umbral'+str(sPer)+'#DD4E03:RAM Use greater than ' + str(sPer) + '%' if limit else None,
						'AREA:umbral'+str(gPer)+'#730000:RAM Use greater than ' + str(gPer) + '%' if limit else None,

						'HRULE:'+str(rVal)+'#F6D911:Umbral ' + str(1) + ' - ' + str(rPer) + '%' if limit else None,
						'HRULE:'+str(sVal)+'#FF5800:Umbral ' + str(rPer) + ' - ' + str(sPer) + '%' if limit else None,
						'HRULE:'+str(gVal)+'#FF0000:Umbral ' + str(sPer) + ' - ' + str(gPer) + '%' if limit else None,

						'GPRINT:ramMAX:%6.2lf %SMAX',
						'GPRINT:ramMIN:%6.2lf %SMIN',
						'GPRINT:ramSTDEV:%6.2lf %SSTDEV',
						'GPRINT:ramLAST:%6.2lf %SLAST',
						'VDEF:a=ram,LSLSLOPE',
						'VDEF:b=ram,LSLINT',
						'CDEF:avg2=ram,POP,a,COUNT,*,b,+',
						'LINE2:avg2#FFBB00',
						'COMMENT: \\n',
						'CDEF:seg=avg2,40,60,LIMIT',
						'VDEF:minseg=seg,FIRST',
						'VDEF:maxseg=seg,LAST',
						'GPRINT:minseg: Reach 40% @ %c \\n:strftime',
						'GPRINT:maxseg: Reach 60% @ %c \\n:strftime',
					]
					graph = filter(None, graph)

					ret = rrdtool.graph(graph)

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

							'HRULE:'+str(rVal)+'#F6D911:Ready ' + str(1) + ' - ' + str(rVal) + '%' if limit else None,
							'HRULE:'+str(sVal)+'#FF5800:Set ' + str(rVal) + ' - ' + str(sVal) + '%' if limit else None,
							'HRULE:'+str(gVal)+'#FF0000:Go ' + str(sVal) + ' - ' + str(gVal) + '%' if limit else None,

							'GPRINT:loadMAX:%6.2lf %SMAX',
							'GPRINT:loadMIN:%6.2lf %SMIN',
							'GPRINT:loadSTDEV:%6.2lf %SSTDEV',
							'GPRINT:loadLAST:%6.2lf %SLAST',
							'VDEF:a=load,LSLSLOPE',
							'VDEF:b=load,LSLINT',
							'CDEF:avg2=load,POP,a,COUNT,*,b,+',
							'LINE2:avg2#FFBB00',
							'COMMENT: \\n',

							'CDEF:segRS=avg2,' + str(rVal) + ',' + str(sVal) + ',LIMIT' if limit else None,
							'CDEF:segSG=avg2,' + str(gVal) + ',100,LIMIT' if limit else None,
							'VDEF:rseg=segRS,FIRST' if limit else None,
							'VDEF:sseg=segRS,LAST' if limit else None,
							'VDEF:gseg=segSG,FIRST' if limit else None,
							'GPRINT:rseg: Reach Ready '+ str(rVal) +'% @ %c \\n:strftime' if limit else None,
							'GPRINT:sseg: Reach Set '+ str(sVal) +'% @ %c \\n:strftime' if limit else None,
							'GPRINT:gseg: Reach Go'+ str(gVal) +'% @ %c \\n:strftime' if limit else None,
						]
						graph = filter(None, graph)

						ret = rrdtool.graph(graph)

				elif fname == self._names[7]:
					name = self._fname[fname]
					nImg = name.format(hostname, 'png')
					nRRD = name.format(hostname, 'rrd')

					limit = self._limits['HDD']

					rVal = 0					
					sVal = 0					
					gVal = 0

					if limit:
						rVal = int(limit['Ready'] * self._agents[hostname].getHDDSize())
						sVal = int(limit['Set'] * self._agents[hostname].getHDDSize())
						gVal = int(limit['Go'] * self._agents[hostname].getHDDSize())
						rPer = int(limit['Ready'] * 100)
						sPer = int(limit['Set'] * 100)
						gPer = int(limit['Go'] * 100)

					graph = [nImg,
						'--start', str(self._agents[hostname].getTime()),
						'--vertical-label=Megabytes',
						'--title=HDD Use',
						'--color', 'ARROW#009900',
						'--vertical-label', 'HDD Use',
						'DEF:hdd='+nRRD+':hdd:AVERAGE',

						'CDEF:umbral'+str(rPer)+'=hdd,'+str(rVal)+',LT,0,hdd,IF' if limit else None,
						'CDEF:umbral'+str(sPer)+'=hdd,'+str(sVal)+',LT,0,hdd,IF' if limit else None,
						'CDEF:umbral'+str(gPer)+'=hdd,'+str(gVal)+',LT,0,hdd,IF' if limit else None,

						'VDEF:hddMAX=hdd,MAXIMUM',
						'VDEF:hddMIN=hdd,MINIMUM',
						'VDEF:hddSTDEV=hdd,STDEV',
						'VDEF:hddLAST=hdd,LAST',
						'AREA:hdd#00FF00:HDD Use',

						'AREA:umbral'+str(rPer)+'#FFDF00:HDD Use greater than ' + str(rPer) + '%' if limit else None,
						'AREA:umbral'+str(sPer)+'#DD4E03:HDD Use greater than ' + str(sPer) + '%' if limit else None,
						'AREA:umbral'+str(gPer)+'#730000:HDD Use greater than ' + str(gPer) + '%' if limit else None,

						'HRULE:'+str(rVal)+'#F6D911:Umbral ' + str(1) + ' - ' + str(rPer) + '%' if limit else None,
						'HRULE:'+str(sVal)+'#FF5800:Umbral ' + str(rPer) + ' - ' + str(sPer) + '%' if limit else None,
						'HRULE:'+str(gVal)+'#FF0000:Umbral ' + str(sPer) + ' - ' + str(gPer) + '%' if limit else None,

						'GPRINT:hddMAX:%6.2lf %SMAX',
						'GPRINT:hddMIN:%6.2lf %SMIN',
						'GPRINT:hddSTDEV:%6.2lf %SSTDEV',
						'GPRINT:hddLAST:%6.2lf %SLAST',
						'VDEF:a=hdd,LSLSLOPE',
						'VDEF:b=hdd,LSLINT',
						'CDEF:avg2=hdd,POP,a,COUNT,*,b,+',
						'LINE2:avg2#FFBB00',
						'COMMENT: \\n',
						'CDEF:seg=avg2,40,60,LIMIT',
						'VDEF:minseg=seg,FIRST',
						'VDEF:maxseg=seg,LAST',
						'GPRINT:minseg: Reach 40% @ %c \\n:strftime',
						'GPRINT:maxseg: Reach 60% @ %c \\n:strftime',
					]
					graph = filter(None, graph)

					ret = rrdtool.graph(graph)
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

		#except (KeyError) as e: #preventing exception if agent deleted
		#	print "Error", e
		#	print 'problem graphs'
		#	return 

	def _checkAberration(self, fname, hostname):
		""" This will check for begin and end of aberration
			in file. Will return:
			0 if aberration not found.
			1 if aberration begins
			2 if aberration ends
		"""
		
		rrdfilename = fname

		info = rrdtool.info(rrdfilename)

		#for key in info:
		#	print key, '-> ', info[key]
		
		rrdstep = int(info['step'])
		lastupdate = int(info['last_update'])
		previosupdate = lastupdate - rrdstep - 1
		graphtmpfile = tempfile.NamedTemporaryFile()

		if self._agents[hostname].getCommunity() == 'variation/virtualtable1':
			
			ab_status = 0

			values = rrdtool.graph(graphtmpfile.name+'F',
					   'DEF:f0=' + rrdfilename + ':inoctets:FAILURES:start=' + str(previosupdate) + ':end=' + str(lastupdate),
					   'PRINT:f0:MIN:%1.0lf',
					   'PRINT:f0:MAX:%1.0lf',
					   'PRINT:f0:LAST:%1.0lf')
			print (values)
			fmin = (values[2][0])
			fmax = (values[2][1])
			flast = (values[2][2])
			print ("fmin="+fmin+", fmax="+fmax+",flast="+flast)
			# check if failure value had changed.
			if '-nan' in [fmin, fmax, flast]:
				return 0
			
			if (int(fmin) != int(fmax)):
				if (int(flast) == 1):
					ab_status = 1
				
				else:
					ab_status = 2
			return ab_status

		# Ready to get FAILURES  from rrdfile
		# will process failures array values for time of 2 last updates
		try:
			data = rrdtool.fetch(rrdfilename, 'FAILURES', '--start', str(previosupdate), '--end', str(lastupdate))
		except (rrdtool.OperationalError) as e:
			print e
			return 0

		print (data)

		if None in  data[2][0]:
			return 0

		mini = 0
		maxi = 0
		if len(data[2]) == 3:
			mini = min(min(data[2][0]), min(data[2][1]))
			maxi = max(max(data[2][0]), max(data[2][1]))
		else:
			maxi = max(data[2][0])
			mini = min(data[2][0])

		last = data[2][0][0]
		print 'go if'
		if mini != maxi:
			print 'if'
			if last == 1:
				print 'start Failure'
				return 2
			else:
				print 'end Failure'
				return 1
		else:
			print 'Return 0'
			return 0

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

		self._notifications[hostname] = {
			'RAM': [],
			'CPU': {},
			'HDD': [],
		}
		self._agents[hostname] = agent
		self._agents[hostname].setStatus(False)
		flag = self._getBasicData(hostname)

		self._threads[hostname] = Thread(target = self._updateRRD, args = (hostname,))

		self._threads[hostname].daemon = True
		self._threads[hostname].start()

		return flag

	def delAgent(self, hostname):
		try:
			if not hostname in self._agents:
				return True

			self._agents[hostname].setStatus(False)
			del self._agents[hostname]
			del self._notifications[hostname]

			if self._threads[hostname].is_alive():
				self._threads[hostname].join()

			del self._threads[hostname]

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

		#self._newNotification = self._newNotification[n:]

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

	def _graphCheck(self, tQuery):
		try:
			nImg = './agents/rrd_predict.png'
			nRRD = './agents/lineal_cpu0.rrd'

			graph = [nImg,
					'--start', tQuery,
					'--vertical-label=CPU 0 Load',
					'--title=CPU Use',
					'--color','ARROW#009900',
					'--vertical-label','CPU Use(%)',
					'--lower-limit','0',
					'--upper-limit','100',
					'DEF:load='+nRRD+':load:AVERAGE',
					'VDEF:loadMAX=load,MAXIMUM',
					'VDEF:loadMIN=load,MINIMUM',
					'VDEF:loadSTDEV=load,STDEV',
					'VDEF:loadLAST=load,LAST',
					'AREA:load#00FF00:CPU Load', 
					'GPRINT:loadMAX:%6.2lf %SMAX',
					'GPRINT:loadMIN:%6.2lf %SMIN',
					'GPRINT:loadSTDEV:%6.2lf %SSTDEV',
					'GPRINT:loadLAST:%6.2lf %SLAST',
					'VDEF:a=load,LSLSLOPE',
					'VDEF:b=load,LSLINT',
					'CDEF:avg2=load,POP,a,COUNT,*,b,+',
					'LINE2:avg2#FFBB00',
					'COMMENT: \\n',
					'CDEF:seg=avg2,10,30,LIMIT',
					'VDEF:minseg=seg,FIRST',
					'VDEF:maxseg=seg,LAST',
					'GPRINT:minseg: Reach 10% @ %c \\n:strftime',
					'GPRINT:maxseg: Reach 30% @ %c \\n:strftime']
			ret = rrdtool.graph(graph)
			return True

		except KeyError:
			return False

	def rrdFile(self, date):
		try:
			date = date.split(' ')
			date[0] += 'T' 
			date[1] = date[1] + '.00Z'
			date = ''.join(date)
			date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple()
			tQuery = int(mktime(date))
			print tQuery
			return self._graphCheck(str(tQuery))
		except KeyError:
			print 'Error time'
			return False

	def setDataAdmin(self, admin):
		print admin
		self._admin = admin
		self._mailreceip = admin['email']
		print self._mailreceip
		return True
