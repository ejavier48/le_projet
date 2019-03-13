#from flask import Flask, request, jsonify, redirect, make_response
import flask
import logging
from flask_cors import CORS, cross_origin
from requests import post, get
#from dummy.manager import ManagerSNMP
#from dummy.agent import Agent

url = 'http://localhost:8080'
add = 'add'
limits = 'limits'
getLimits = 'getLimits'
limit = 'limit'

addB = {
	'host' : 'localhost',
	'port' : '161',
	'version' : '2',
	'community' : 'grupo4cm2'
}


manager = None
img_path = './agents/{}_{}.png'
app = flask.Flask(__name__)
app.secret_key = 'hgkyigkj,khbgkgiugkliuhgkuhloiyhliuhlkuhyliu'

#cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['DEBUG'] = True


@app.route('/', methods = ['GET','POST'])
def home():
	r = post('/'.join([url, add]), json = addB)
	print r.json()
	r = get('http://localhost:8080/')
	print r.json()
	return flask.jsonify(r.json())

if __name__ == '__main__':
	app.run(host = '0.0.0.0', port = '8909')