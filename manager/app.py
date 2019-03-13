from flask import Flask, request, jsonify, redirect, make_response
#import flask
import logging
from flask_cors import CORS, cross_origin
from dummy.manager import ManagerSNMP
from dummy.agent import Agent


manager = None
img_path = './agents/{}_{}.png'
app = Flask(__name__)
app.secret_key = 'hgkyigkj,khbgkgiugkliuhgkuhloiyhliuhlkuhyliu'

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['DEBUG'] = True
logging.getLogger('flask_cors').level = logging.DEBUG


@app.route('/', methods = ['GET','POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def home():

	return jsonify(manager.getDict())

@app.route('/add', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def addAgent():

	if request.is_json:

		data = request.get_json()
		agent = Agent(data['host'], data['version'], int(data['port']), data['community'])

		if (manager.addAgent(agent)):
			return redirect('/')
		else:
			return redirect('/error/NoConnected')

	else:
		return redirect('/error/format')

@app.route('/delete', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def deleteAgent():
	if True:
		data = request.get_json()
		manager.delAgent(data['host'])
		return jsonify({'status':True})
	else:
		return redirect('/error/format')

@app.route('/info', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def info():
	data = request.get_json()
	ans = manager.getAgentDict(data['host'])
	return jsonify(ans)

@app.route('/limit', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def limit():
	if request.is_json:

		data = request.get_json()

		if not manager.setLimit(data):
			return redirect('/error/InvalideLimit')

		else:
			return jsonify({'status':True})

	else:
		return redirect('/error/format')

@app.route('/limits', methods = ['POST', 'GET',])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def limits():

	if request.method == 'GET':
		return jsonify(manager.getLimits())

	elif request.is_json:

		data = request.get_json()

		if not manager.setAllLimits(data):
			return redirect('/error/InvalideLimit')

		else:
			return jsonify({'status':True})

	else:
		return redirect('/error/format')

@app.route('/notify', methods = ['POST',])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def notify():
	return jsonify(manager.getNotifications())

@app.route('/images/<host>/<path>')
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def images(host, path):
	
	image = img_path.format(host, path)

	try:

		resp = make_response(open(image).read())
		resp.content_type = 'image/png'
		return resp

	except:
		return redirect('/error/noImageFound')

@app.route('/error/<typeE>', methods = ['GET', 'POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def error(typeE):
	data = {}
	data['error'] = typeE
	return jsonify(data)

@app.route('/date', methods = ['POST'])
@cross_origin(origin='*', headers=['Content-Type','Authorization'])
def date():
	if request.is_json:
		data = request.get_json()

		if not manager.rrdFile(data['date']):
			return redirect('/error/InvalideDate')
		else:
			return jsonify({'status':True})

	else:
		return redirect('/error/format')

if __name__ == '__main__':
	manager = ManagerSNMP()
	app.run(host = '0.0.0.0', port = '8080')