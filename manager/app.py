import flask
from flask_cors import CORS
from dummy.manager import ManagerSNMP
from dummy.agent import Agent


manager = None
img_path = './agents/{}_{}.png'
app = flask.Flask(__name__)
app.secret_key = '1335555577777789'

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
		if (manager.addAgent(agent)):
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

@app.route('/info', methods = ['POST'])
def info():
	data = flask.request.get_json()
	ans = manager.getAgentDict(data['host'])
	return flask.jsonify(ans)
	#except:
	#	return flask.redirect('/error/format')



@app.route('/images/<host>/<path>')
def images(host, path):
	image = img_path.format(host, path)
	print image
	try:
		resp = flask.make_response(open(image).read())
		resp.content_type = 'image/png'
		return resp
	except:
		return flask.redirect('/error/noImageFound')

@app.route('/error/<typeE>', methods = ['GET', 'POST'])
def error(typeE):
	data = {}
	data['error'] = typeE
	return flask.jsonify(data)

if __name__ == '__main__':
	manager = ManagerSNMP()
	app.run(host = '0.0.0.0', port = '8080')