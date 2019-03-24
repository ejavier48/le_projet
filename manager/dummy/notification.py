from time import time

class Notification():

	_STATUS = ['reported', 'in revision', 'diagnosted', 'solved']

	def __init__(self, hostname, resource, label, limit, measure, file):
		self._hostname = hostname
		self._resource = resource
		self._label = label
		self._limit = limit
		self._measure = measure
		self._status = 0
		self._sLabel = self._STATUS[self._status]
		self._comment = []
		self._file = file
		self._times = [time()]

	def addComment(self, comment):
		self._comment.append((comment, time()))

	def nextStatus(self):
		if i < 2:
			self._status += 1
			self._times.append(time())
			self._sLabel = self._STATUS[self._status]

	def getTimeReport(self):
		return self._times[0]

	def getLabel(self):
		return self._label

	def getHostname(self):
		return self._hostname

	def getFile(self):
		return self._file

	def getResource(self):
		return self._resource

	def getReport(self):
		return self.__dict__

	def getHostName(self):
		return self._hostname
