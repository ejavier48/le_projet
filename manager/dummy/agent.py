from time import time
import re

class Agent():

	_rex = 'LINUX|linux|Linux'

	def __init__(self, hostName, version, port, community):
		self._hostName = hostName
		self._version = version
		self._port = port
		self._community = community
		self._status = None
		self._time =  int(time())
		self._numInterFs = 0
		self._interfaces = []
		self._hddUse = 0
		self._hddSize = 0

	def setTime(self):
		self._time = int(time())

	def setHostName(self, hostName):
		self._hostName = hostName

	def setVersion(self, version):
		self._version = version

	def setPort(self, port):
		self._port = port

	def setCommunity(self, community):
		self._community = community

	def setStatus(self, status):
		self._status = status

	def setInfo(self, info):
		self._os = 'linux' if re.search(self._rex, info) else 'win'
		self._info = info

	def setContact(self, contact):
		self._contact = contact

	def setNode(self, node):
		self._node = node

	def setLocalization(self, localization):
		self._localization = localization

	def setNumInterFs(self, numInterFs):
		self._numInterFs = numInterFs

	def setInterfaces(self, interfaces):
		self._interfaces = interfaces

	def setUpTime(self, upTime):
		time = upTime
		ms = time % 100
		time /= 100
		segs = time % 60
		time /= 60
		mins = time % 60
		time /= 60
		hrs = time % 60
		days = hrs/24
		hrs %= 24
		self._upTimeR = upTime
		self._upTimeF = '({}) {} day {}:{}:{}.{}'.format(upTime, days, hrs, mins, segs, ms)

	def setRAMSize(self, ramSize):
		self._ramSize = ramSize

	def setRAMUse(self, ramUse):
		self._ramUse = ramUse

	def setHDDSize(self, hddSize):
		self._hddSize = hddSize

	def setHDDUse(self, hddUse):
		self._hddUse = hddUse

	def setNumCPUs(self, numCPUs):
		self._numCPUs = numCPUs

	def setCPUsUse(self, cpusUse):
		self._cpusUse = cpusUse

	def getTime(self):
		return self._time
		
	def getHostName(self):
		return self._hostName

	def getVersion(self):
		return self._version

	def getPort(self):
		return self._port

	def getCommunity(self):
		return self._community

	def getStatus(self):
		return self._status

	def getUptimeR(self):
		return self._upTimeR

	def getUpTimeF(self):
		return self._upTimeF

	def getInfo(self):
		return self._info#"{} {} {} {}".format(self._type, self._os, self._bits, self._date)

	def getContact(self):
		return self._contact

	def getNode(self):
		return self._node

	def getLocalization(self):
		return self._localization

	def getNumInterFs(self):
		return self._numInterFs

	def getInterfaces(self):
		return self._interfaces

	def getRAMSize(self):
		return self._ramSize

	def getRAMUse(self):
		return self._ramUse

	def getHDDSize(self):
		return self._hddSize

	def getHDDUse(self):
		return self._hddUse

	def getNumCPUs(self):
		return self._numCPUs

	def getCPUsUse(self):
		return self._cpusUse

	def getOS(self):
		return self._os

	def getDict(self):
		self._numInterFs = len(self._interfaces)
		return self.__dict__