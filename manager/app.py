from flask import Flask, request, jsonify, redirect, make_response
from flask_cors import CORS
from dummy.manager import ManagerSNMP
from dummy.agent import Agent


manager = None
img_path = './agents/{}_{}.png'
app = Flask(__name__)
app.secret_key = '1335555577777789'

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['DEBUG'] = True

@app.route('/', methods = ['GET','POST'])
def home():
	return jsonify(manager.getDict())

@app.route('/add', methods = ['POST'])
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
def deleteAgent():
	try:
		data = request.get_json()
		manager.delAgent(data['host'])
		return jsonify({'status':True})
	except:
		return redirect('/error/format')

@app.route('/info', methods = ['POST'])
def info():
	data = request.get_json()
	ans = manager.getAgentDict(data['host'])
	return jsonify(ans)


@app.route('/limit', methods = ['POST'])
def limit():
	if request.is_json:
		data = request.get_json()
		print data
		if not manager.setLimit(data):
			return redirect('/error/InvalideLimit')
		else:
			return jsonify({'status':True})
	else:
		return redirect('/error/format')

@app.route('/limits', methods = ['POST', 'GET',])
def limits():
	if request.method == 'GET':
		return jsonify(manager.getLimits())

	elif request.is_json:
		data = request.get_json()
		print data

		if not manager.setAllLimits(data):
			return redirect('/error/InvalideLimit')
		else:
			return jsonify({'status':True})

	else:
		return redirect('/error/format')

@app.route('/notify', methods = ['POST',])
def notify():
	return jsonify(manager.getNotifications())

@app.route('/images/<host>/<path>')
def images(host, path):
	image = img_path.format(host, path)
	print image
	if True:#try:
		resp = make_response(open(image).read())
		resp.content_type = 'image/png'
		return resp

	else:#except:
		return redirect('/error/noImageFound')

@app.route('/error/<typeE>', methods = ['GET', 'POST'])
def error(typeE):
	data = {}
	data['error'] = typeE
	return jsonify(data)

if __name__ == '__main__':
	manager = ManagerSNMP()
	app.run(host = '0.0.0.0', port = '8080')