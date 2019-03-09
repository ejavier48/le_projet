from time import time

class Notification():

	_STATUS = ['reported', 'in revision', 'diagnosted', 'solved']

	def __init__(self, hostname, resource, limit, measure):
		self._hostname = hostname
		self._resource = resource
		self._limit = limit
		self._measure = measure
		self._status = 0
		self._label = self._STATUS[self._status]
		self._comment = []
		self._times = [time()]

	def addComment(self, comment):
		self._comment.append((comment, time()))

	def nextStatus(self):
		if i < 2:
			self._status += 1
			self._times.append(time())
			self._label = self._STATUS[self._status]

	def getTimeReport(self):
		return self._times[0]

	def getReport(self):
		return self.__dict__
