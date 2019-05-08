# -*- coding: utf-8 -*-
from pylatex import Center, Command, Document, Figure, Itemize, MultiColumn, NewPage, Package, Section, Subsection, Tabular
from pylatex.utils import italic, NoEscape, bold

from threading import Thread
from time import sleep

import os

from http_checker import checkHTTP, checkTFTP
from dummy.manager import ManagerSNMP
from dummy.agent import Agent

MAX = 10000


class Reporter:

	_tyServer = 'Servidor {Server} {location} Status {status}'

	_iBasicInfo = ['Sistema Operativo', 'Tiempo de Actividad', 'Numero de Interfaces']

	_path = 'agents/{}_{}.png'

	def __init__(self):
		self._manager = ManagerSNMP()
		self._threads = {
			'DNS'  : {},
			'SSH'  : {},
			'SMTP' : {},
			'HTTP' : {},
			'TFTP' : {},
		}
		self._servers = {
			'DNS'  : {},
			'SSH'  : {},
			'SMTP' : {},
			'HTTP' : {},
			'TFTP' : {},
		}
		self._report = {
			'DNS'  : {},
			'SSH'  : {},
			'SMTP' : {},
			'HTTP' : {},
			'TFTP' : {},
		}
		self._checkServer = {
			'DNS'  : self._checkDNS,
			'SSH'  : self._checkSSH,
			'SMTP' : self._checkSMTP,
			'HTTP' : self._checkHTTP,
			'TFTP' : self._checkTFTP,
		}

	def addServer(self, info):
		agent = Agent(info['host'], info['version'], int(info['port']), info['community'])

		if self._manager.addAgent(agent):

			self._servers[info['type']][info['host']] = info
			self._report[info['type']][info['host']] = None

			self._servers[info['type']][info['host']]['status'] = True
			
			self._threads[info['type']][info['host']] = Thread(target = self._checkServer[info['type']], args = (info['host'], info['type']))
			self._threads[info['type']][info['host']].daemon = True
			self._threads[info['type']][info['host']].start()
			
			return True

		else:
			return False

	def _checkDNS(self, host, typeS):
		while self._servers[typeS][host]['status']:
			self._report[typeS][host] = checkDNS(self._servers[typeS][host]['url'], )

	def _checkSSH(self, host, typeS):
		while self._servers[typeS][host]['status']:
			self._report[typeS][host] = checkSSH(self._servers[typeS][host]['url'], )

	def _checkSMTP(self, host, typeS):
		while self._servers[typeS][host]['status']:
			self._report[typeS][host] = checkSMTP(self._servers[typeS][host]['url'], )

	def _checkHTTP(self, host, typeS):
		time = {
			'Minimo' : 10e10,
			'Maximo' : -1,
			'Promedio' : 0,
		}
		vel = {
			'Minimo' : 10e10,
			'Maximo' : -1,
			'Promedio' : 0,
		}
		total = {
			'Minimo' : 10e10,
			'Maximo' : -1,
			'Promedio' : 0,
		}

		self._report[typeS][host] = {}

		self._report[typeS][host]['Respuestas'] = {}

		i = 1
		while self._servers[typeS][host]['status']:
			
			aux = checkHTTP(self._servers[typeS][host]['url'])

			if aux['status'] == 'Error':
				if not 'Error' in self._report[typeS][host]['Respuestas']:
					self._report[typeS][host]['Respuestas']['Error'] = 0
				self._report[typeS][host]['Respuestas']['Error'] += 1
				continue

			if not aux['status'] in self._report[typeS][host]['Respuestas']:
				self._report[typeS][host]['Respuestas'][aux['status']] = 0



			self._report[typeS][host]['Respuestas'][aux['status']] += 1

			del aux['status']

			aux['Respuestas'] = self._report[typeS][host]['Respuestas']

			time['Minimo'] = min(time['Minimo'], aux['Tiempo (s)'])
			time['Maximo'] = max(time['Maximo'], aux['Tiempo (s)'])
			time['Promedio'] += (aux['Tiempo (s)']/i - time['Promedio']/i)
			time['Ultima Medicion'] = aux['Tiempo (s)']

			aux['Tiempo (s)'] = time

			vel['Minimo'] = min(vel['Minimo'], aux['Velocidad (bytes/s)'])
			vel['Maximo'] = max(vel['Maximo'], aux['Velocidad (bytes/s)'])
			vel['Promedio'] += (aux['Velocidad (bytes/s)']/i - vel['Promedio']/i)
			vel['Ultima Medicion'] = aux['Velocidad (bytes/s)']

			aux['Velocidad (bytes/s)'] = vel



			total['Minimo'] = min(total['Minimo'], aux['Total Bytes'])
			total['Maximo'] = max(total['Maximo'], aux['Total Bytes'])
			total['Promedio'] += (aux['Total Bytes']/i - total['Promedio']/i)
			total['Ultima Medicion'] = aux['Total Bytes']

			aux['Total Bytes'] = total

			self._report[typeS][host] = aux
			i += 1

	def _checkTFTP(self, host, typeS):
		descarga = {
			'Minimo' : 10e10,
			'Maximo' : -1,
			'Promedio' : 0,
		}
		carga = {
			'Minimo' : 10e10,
			'Maximo' : -1,
			'Promedio' : 0,
		}
		conexion = {
			'Minimo' : 10e10,
			'Maximo' : -1,
			'Promedio' : 0,
		}

		self._report[typeS][host] = {}

		self._report[typeS][host]['Respuestas'] = {'Down' : 0, 'Up' : 0}

		i = 1
		while self._servers[typeS][host]['status']:
			aux = checkTFTP(self._servers[typeS][host]['url'], self._servers[typeS][host]['portS'])

			if aux['status'] == 'Down':
				self._report[typeS][host]['Respuestas'][aux['status']] += 1
				continue

			self._report[typeS][host]['Respuestas'][aux['status']] += 1

			aux['Respuestas'] = self._report[typeS][host]['Respuestas']

			del aux['status']

			descarga['Minimo'] = min(descarga['Minimo'], aux['Tiempo Descarga (s)'])
			descarga['Maximo'] = max(descarga['Maximo'], aux['Tiempo Descarga (s)'])
			descarga['Promedio'] += (aux['Tiempo Descarga (s)']/i - descarga['Promedio']/i)

			aux['Tiempo Descarga (s)'] = descarga

			carga['Minimo'] = min(carga['Minimo'], aux['Tiempo Carga (s)'])
			carga['Maximo'] = max(carga['Maximo'], aux['Tiempo Carga (s)'])
			carga['Promedio'] += (aux['Tiempo Carga (s)']/i - carga['Promedio']/i)

			aux['Tiempo Carga (s)'] = carga

			conexion['Minimo'] = min(conexion['Minimo'], aux['Tiempo Conexion (s)'])
			conexion['Maximo'] = max(conexion['Maximo'], aux['Tiempo Conexion (s)'])
			conexion['Promedio'] += (aux['Tiempo Conexion (s)']/i - conexion['Promedio']/i)

			aux['Tiempo Conexion (s)'] = conexion

			self._report[typeS][host] = aux

	def delAgent(self, host, typeS):
		if host in self._servers[typeS]:
			self._servers[typeS][host]['status'] = False
			
			#self._manager.delAgent(host)

			del self._servers[typeS][host]
			del self._report[typeS][host]

			if self._threads[typeS][host].is_alive():
				self._threads[typeS][host].join()

			del self._threads[typeS][host]

			return True
		else:
			return False

	def generateReport(self):
		doc = Document()

		doc.packages.append(Package('array'))
		doc.preamble.append(Command('title', 'Reporte de Rendimiento'))

		doc.preamble.append(Command('author', 'Equipo 3'))

		doc.preamble.append(Command('date', NoEscape(r'\today')))

		doc.append(NoEscape(r'\maketitle'))

		with doc.create(Section("Integrantes")):
			with doc.create(Itemize()) as itemize:
				itemize.add_item(NoEscape("Caballero Ramirez Michelle"))
				itemize.add_item(NoEscape("Garcia Lomeli Abraham Amos"))
				itemize.add_item(NoEscape("Mu\~noz Ramirez Adriana"))
				itemize.add_item(NoEscape("Rodriguez Mu\~noz Alicia Vanessa"))
				itemize.add_item(NoEscape("Sanchez Gama Erick Javier"))

		for typeS in self._servers:
			
			servers = self._servers[typeS]

			for server in servers:

				doc.append(NewPage())

				info = servers[server]
				status = self._manager.getAgentStatus(server)

				s = self._tyServer.format(Server=info['type'], location=info['url'], status=('UP' if status else 'DOWN'))

				if status == False:
					doc.create(Section(s))

				else:
					agent = self._manager.getAgent(server)

					basic = []
					basic.append(agent.getOS())
					basic.append(agent.getUpTimeF())
					basic.append(agent.getNumInterFs())

					with doc.create(Section(s)):
						with doc.create(Center()) as center:
							with center.create(Tabular('| p{20em}  p{20em}|')) as table:

								table.add_hline()
								table.add_row((MultiColumn(2, align = '|c|', data = bold('Reporte Servidor')),))
								table.add_hline()
								table.add_row((MultiColumn(2, align = '|c|', data = bold('Informacion General')),))
								table.add_hline()

								for info, data in zip(self._iBasicInfo, basic):
										table.add_row((info, data))

								if self._report[typeS][server] is None:
									continue

								table.add_hline()

								table.add_row((MultiColumn(2, align = '|c|', data = bold('Recursos')),))

								table.add_hline()

								headers = self._report[typeS][server]

								print self._report[typeS][server]

								
								for header in headers:

									table.add_row((MultiColumn(2, align = '|c|', data = bold(header)),))

									table.add_hline()

									points = headers[header]

									for point in points:

										table.add_row((italic(point), points[point]))

									table.add_hline()

						with doc.create(Subsection('Uso de Recursos')) as sub:
							with sub.create(Figure(position='h!')) as image:
								aux = self._path.format(server, 'ram')
								path = os.path.join(os.path.dirname(__file__), aux)
								image.add_image(path)
								image.add_caption('Uso de Memoria RAM')
							print agent.getNumCPUs()
							for i in range(agent.getNumCPUs()):
								with sub.create(Figure(position='h!')) as image:
									aux = self._path.format(server, 'cpu'+str(i))
									path = os.path.join(os.path.dirname(__file__), aux)
									image.add_image(path)
									image.add_caption('Uso de CPU ' + str(i+1))

		doc.generate_pdf('rendimiento', clean_tex=False)


if __name__ == '__main__':
	report = Reporter()
	info = {
		'host' : '192.168.1.86',
		'version' : '2',
		'community' : 'grupo4cm2',
		'port' : '161',
		'type' : 'HTTP',
		'url' : 'http://192.168.1.86'
	}
	report.addServer(info)
	info = {
		'host' : '192.168.1.86',
		'version' : '2',
		'community' : 'grupo4cm2',
		'port' : '161',
		'type' : 'TFTP',
		'url' : '192.168.1.86',
		'portS' : '69',
	}
	report.addServer(info)
	sleep(10)

	report.generateReport()
'''
servers = {
	'Web'	:  'patito.com',
	'TFTP'	:  '192.168.1.86',
	'SSH'	:  '192.168.1.92',
	'DNS'	:  '192.168.1.90',
	'Mail'	:  '@patito.com',
}

report = {
	'Periodo de Prueba':  ['Inicio {val}', 'Final {val}'],
	'Solicitudes'	   :  ['Total {val}', 'Exitosas {val}', 'Fallidas {val}'],
	'Tiempo Respuesta' :  ['Min {val}', 'Max {val}', 'Prom {val}'],
}

BasicInfo = {
	'Sistema Operativo' : None, 
	'Tiempo de Actividad' : None, 
	'Numero de Interfaces' : None, 
	'Graficas' : None, 
	'Supervision Servidor' : report,
}



Servidor = {
	'Sistema Operativo' : 'Linux', 
	'Tiempo de Actividad' : '1 hr', 
	'Numero de Interfaces' : '4', 
	'Graficas': 'Empty', 
	'Supervision Servidor' : 'lalalala',
}
'''