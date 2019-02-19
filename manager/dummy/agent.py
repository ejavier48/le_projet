class Agent():

	def __init__(self, hostName, version, port, community):
		self._hostName = hostName
		self._version = version
		self._port = port
		self._community = community
		self._status = None

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
		info = info.split(' ')
		self._type = info[0]
		self._os = info[5]
		self._date = info[7]
		self._bits = info[8]

	def getInfo(self):
		return "{} {} {} {}".format(self._type, self._os, self._bits, self._date)

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