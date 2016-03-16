import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify
import limit
from model.model import Base, User, get_db_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import json, datetime, decimal

session = get_db_session()

app = Flask(__name__)

@app.after_request
def inject_headers(response):
	return limit.inject_x_rate_headers(response)

# @app.route('/rate-limited')
# @limit.ratelimit(limit=2, per=10 * 1)
# def index():
#     return jsonify({'response':'This is a rate limited response'})

def get_not_implemented_msg():
	return jsonify({'data': 'endpoint is not implemented'})

#START main

@app.route('/api/v1/<provider>/login', methods=['POST'])
def login(provider):
    return get_not_implemented_msg()

@app.route('/api/v1/<provider>/logout', methods=['POST'])
def logout(provider):
    return get_not_implemented_msg()


@app.route('/api/v1/users', methods=['GET','POST', 'PUT', 'DELETE'])
def process_users():
	if request.method == 'GET':
		users = session.query(User).all()
		return jsonify(users = [u.serialize for u in users])
	elif request.method == 'POST':
		return get_not_implemented_msg()
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		return get_not_implemented_msg()


@app.route('/api/v1/users/<int:id>', methods=['GET'])
def process_user(id):
    return get_not_implemented_msg()


@app.route('/api/v1/requests', methods=['GET','POST'])
def process_requests():
	if request.method == 'GET':
		return get_not_implemented_msg()
	elif request.method == 'POST':
		return get_not_implemented_msg()


@app.route('/api/v1/requests/<int:id>', methods=['GET','PUT','DELETE'])
def process_request():
	if request.method == 'GET':
		return get_not_implemented_msg()
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		return get_not_implemented_msg()

@app.route('/api/v1/proposals', methods=['GET','POST'])
def process_proposals():
	if request.method == 'GET':
		return get_not_implemented_msg()
	elif request.method == 'POST':
		return get_not_implemented_msg()


@app.route('/api/v1/proposals/<int:id>', methods=['GET','PUT','DELETE'])
def process_proposal():
	if request.method == 'GET':
		return get_not_implemented_msg()
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		return get_not_implemented_msg()

@app.route('/api/v1/dates', methods=['GET','POST'])
def process_dates():
	if request.method == 'GET':
		return get_not_implemented_msg()
	elif request.method == 'POST':
		return get_not_implemented_msg()


@app.route('/api/v1/dates/<int:id>', methods=['GET','PUT','DELETE'])
def process_date():
	if request.method == 'GET':
		return get_not_implemented_msg()
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		return get_not_implemented_msg()


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)