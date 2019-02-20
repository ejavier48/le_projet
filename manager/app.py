import flask
from flask_cors import CORS
from dummy.manager import ManagerSNMP
from dummy.agent import Agent

manager = None

app = flask.Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['DEBUG'] = True

@app.route('/', methods = ['GET','POST'])
def home():
	return flask.jsonify(manager.getDict())

@app.route('/add', methods = ['POST'])
def addAgent():
	try:
		data = flask.request.get_json()
		agent = Agent(data['host'], data['version'], int(data['port']), data['community'])
		manager.addAgent(agent)
		if (manager.getBasicData(data['host'])):
			return flask.redirect('/')
		else:
			return flask.redirect('/error/NoConnected')
	except:
		return flask.redirect('/error/format')

@app.route('/delete', methods = ['POST'])
def deleteAgent():
	try:
		data = flask.request.get_json()
		manager.delAgent(data['host'])
		return flask.jsonify({'status':True})
	except:
		return flask.redirect('/error/format')


@app.route('/error/<typeE>', methods = ['GET', 'POST'])
def error(typeE):
	data = {}
	data['error'] = typeE
	return flask.jsonify(data)


if __name__ == '__main__':
	manager = ManagerSNMP()
	app.run(host = '0.0.0.0', port = '8080')