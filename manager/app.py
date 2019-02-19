import flask 

app = flask.Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods = ['GET'])
def home():
	a = {'token':'token123'}
	return flask.jsonify(a)


if __name__ == '__main__':
	app.run(port = '8080')
