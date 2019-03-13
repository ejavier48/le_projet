#from flask import Flask, request, jsonify, redirect, make_response
import flask
import logging
from flask_cors import CORS, cross_origin
from dummy.manager import ManagerSNMP
from dummy.agent import Agent


manager = None
img_path = './agents/{}_{}.png'
app = flask.Flask(__name__)
app.secret_key = 'hgkyigkj,khbgkgiugkliuhgkuhloiyhliuhlkuhyliu'

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['DEBUG'] = True
logging.getLogger('flask_cors').level = logging.DEBUG


@app.route('/', methods = ['GET','POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def home():
	return flask.jsonify(manager.getDict())

@app.route('/add', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def addAgent():

	if flask.request.is_json:

		data = flask.request.get_json()
		agent = Agent(data['host'], data['version'], int(data['port']), data['community'])

		if (manager.addAgent(agent)):
			return flask.redirect('/')
		else:
			return flask.redirect('/error/NoConnected')

	else:
		return flask.redirect('/error/format')

@app.route('/delete', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def deleteAgent():
	if True:
		data = flask.request.get_json()
		manager.delAgent(data['host'])
		return flask.jsonify({'status':True})
	else:
		return flask.redirect('/error/format')

@app.route('/info', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def info():
	data = flask.request.get_json()
	ans = manager.getAgentDict(data['host'])
	return flask.jsonify(ans)


@app.route('/limit', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def limit():
	if flask.request.is_json:

		data = flask.request.get_json()

		if not manager.setLimit(data):
			return flask.redirect('/error/InvalideLimit')

		else:
			return flask.jsonify({'status':True})

	else:
		return flask.redirect('/error/format')

@app.route('/limits', methods = ['POST', 'GET',])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def limits():

	if flask.request.method == 'GET':
		return flask.jsonify(manager.getLimits())

	elif flask.request.is_json:

		data = flask.request.get_json()

		if not manager.setAllLimits(data):
			return flask.redirect('/error/InvalideLimit')

		else:
			return flask.jsonify({'status':True})

	else:
		return flask.redirect('/error/format')

@app.route('/notify', methods = ['POST',])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def notify():
	return flask.jsonify(manager.getNotifications())

@app.route('/images/<host>/<path>')
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def images(host, path):
	
	image = img_path.format(host, path)

	try:

		resp = flask.make_response(open(image).read())
		resp.content_type = 'image/png'
		return resp

	except:
		return flask.redirect('/error/noImageFound')

@app.route('/error/<typeE>', methods = ['GET', 'POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])

def error(typeE):
	data = {}
	data['error'] = typeE
	return flask.jsonify(data)

if __name__ == '__main__':
	manager = ManagerSNMP()
	app.run(host = '0.0.0.0', port = '8080')