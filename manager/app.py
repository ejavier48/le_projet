import flask 

app = flask.Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods = ['GET'])
def home():
	a = {
		'host':'10.100.74.70',
		'version':'2',
		'port':'161',
		'community':'gr_4cm2'
	}
	return flask.jsonify(a)

@app.route('/info/<host>', methods = ['GET', 'POST'])
def info(host):
	print host
	if flask.request.method == 'POST':
		return flask.jsonify(info_post(host))
	else:
		return flask.jsonify(info_get(host))


@app.route('/json_example', methods = ['POST'])
def json_example():
	print(flask.request.is_json)
	req_data = flask.request.get_json()
	print req_data
	a = flask.jsonify(req_data)
	a = {
		'host':'10.100.74.70',
		'version':'2',
		'port':'161',
		'community':'gr_4cm2'
	}
	return a



def info_post(host):
	a = {
		'host':'10.100.74.70',
		'version':'2',
		'port':'161',
		'community':'gr_4cm2'
	}
	a[',method'] = 'POST'
	a['len'] = len(host)
	a['saludos'] = 'Hola mundo'
	return a

def info_get(host):
	a = {
		'host':'10.100.74.70',
		'version':'2',
		'port':'161',
		'community':'gr_4cm2'
	}
	a[',method'] = 'GET'
	a['len'] = len(host)
	a['saludos'] = 'adios'
	return a


if __name__ == '__main__':
	app.run(port = '8080')
