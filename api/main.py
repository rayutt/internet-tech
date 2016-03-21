import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify
import limit
from model import Base, User, Request, Proposal, MealDate, get_db_session
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

#generic method to return a message indicating that the user has entered invalid data
def get_invalid_input_msg(fields):
	return jsonify({'error': 'Invalid input in one or more of fields: '+fields})

#authenciates a user
def require_token(func):
 def validate(*args, **kwargs):
  token = request.headers.get('Authorization')
  id = User.verify_auth_token(token) if token else None
  if id:
   g.user = id
   return func(*args, **kwargs)
  else:
   return jsonify({'error': 'Invalid token'})
 return validate
	
#creates a user if the oauth is successful
def create_user(answer):
	answer.json()
	name = data['name']
	picture = data['picture']
	email = data['email']
	user = session.query(User).filter_by(email=email).first()
	if not user:
		user = User(username = name, picture = picture, email = email)
		session.add(user)
		session.commit()

#START main
# @limit.ratelimit(limit=2, per=10 * 1)
@app.route('/api/v1/<provider>/login', methods=['POST'])
def login(provider):
	if provider == 'gmail':
		return get_not_implemented_msg()
	elif provider == 'facebook':
		return get_not_implemented_msg()
	elif provider == 'app':
		email = request.form['email']
		password = request.form['password']
		user = session.query(User).filter_by(email = email).first()

		if user and User.verify_password(password, user.password_hash):
			return jsonify({'token': User.generate_auth_token(user.id)})
		else:
			#keep error message generic to avoid leaking info to attacker
			return jsonify({'error': 'Invalid username and/or password'})

# @limit.ratelimit(limit=2, per=10 * 1)
@app.route('/api/v1/<provider>/logout', methods=['POST'])
def logout(provider):
    return get_not_implemented_msg()

@require_token
# @limit.ratelimit(limit=2, per=10 * 1)
@app.route('/api/v1/users', methods=['GET','POST', 'PUT', 'DELETE'])
def process_users():
	if request.method == 'GET':
		users = session.query(User).all()
		return jsonify(users = [u.serialize for u in users])
	elif request.method == 'POST':
		email = request.form['email']
		password = request.form['password']

		if(email and password and len(email) > 3 and len(password) > 3):
			if(session.query(User).filter_by(email = email).first()):
				#username already exists, return error message
				return jsonify({'error': 'the email provided already exists.'})
			else:
				newUser = User(email = email, password_hash = User.hash_password(password))
				session.add(newUser)
				session.commit()
				return jsonify(newUser.serialize)
		else:
			return get_invalid_input_msg("email, password")
	elif request.method == 'PUT':
		#user = User.query(id)
		#user.name = 'username'
		#session.commit()
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		user = session.query(User).filter_by(id = id)
		session.delete(user)
		session.commit()
		

# @limit.ratelimit(limit=2, per=10 * 1)
@require_token
@app.route('/api/v1/users/<int:id>', methods=['GET'])
def process_user(id):
	#TODO include his requests/dates/proposals etc
	user = session.query(User).filter_by(id = id).first()
	if user:
		return jsonify(user.serialize)
	else:
		return jsonify({'error': 'user does not exist'})

# @limit.ratelimit(limit=2, per=10 * 1)
@require_token
@app.route('/api/v1/requests', methods=['GET','POST'])
def process_requests():
	if request.method == 'GET':
		requests = session.query(Request).all()
		return jsonify(requests = [r.serialize for r in requests])
	elif request.method == 'POST':
		#TODO user id should not come from post form data (testing purposes) // meal_time from user instead of static
		user_id = request.form['id']
		meal_type = request.form['meal_type']
		location_string = request.form['location_string']
		latitude = request.form['latitude']
		longitude = request.form['longitude']
		meal_time = datetime.datetime.utcnow()

		if(user_id, meal_type, location_string, latitude, longitude, meal_time):
			newRequest = Request(user_id = user_id, meal_type = meal_type, location_string=location_string,
							  latitude=latitude,longitude=longitude, meal_time=meal_time)
			session.add(newRequest)
			session.commit()
			return jsonify(newRequest.serialize)
		else:
			return get_invalid_input_msg("meal_type, location_string, latitude, longitude, meal_time")

# @limit.ratelimit(limit=2, per=10 * 1)
@require_token
@app.route('/api/v1/requests/<int:id>', methods=['GET','PUT','DELETE'])
def process_request():
	if request.method == 'GET':
		req = session.query(Request).filter_by(rid = id).first()
		if req:
			return jsonify(req.serialize)
		else:
			return jsonify({'error': 'request does not exist'})
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		req = session.query(Request).filter_by(rid = id)
		session.delete(req)
		session.commit()

# @limit.ratelimit(limit=2, per=10 * 1)
@require_token
@app.route('/api/v1/proposals', methods=['GET','POST'])
def process_proposals():
	if request.method == 'GET':
		req = session.query(Proposal).filter_by(pid = id).first()
		if req:
			return jsonify(req.serialize)
		else:
			return jsonify({'error': 'request does not exist'})
	elif request.method =='POST':
		return get_not_implemented_msg()

# @limit.ratelimit(limit=2, per=10 * 1)	
@require_token
@app.route('/api/v1/proposals/<int:id>', methods=['GET','PUT','DELETE'])
def process_proposal():
	if request.method == 'GET':
		req = session.query(Proposal).filter_by(pid = id).first()
		if req:
			return jsonify(req.serialize)
		else:
			return jsonify({'error': 'request does not exist'})
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		req = session.query(Proposal).filter_by(pid = id)
		session.delete(req)
		session.commit()

# @limit.ratelimit(limit=2, per=10 * 1)
@require_token
@app.route('/api/v1/dates', methods=['GET','POST'])
def process_dates():
	if request.method == 'GET':
		return get_not_implemented_msg()
	elif request.method == 'POST':
		return get_not_implemented_msg()

# @limit.ratelimit(limit=2, per=10 * 1)
@require_token
@app.route('/api/v1/dates/<int:id>', methods=['GET','PUT','DELETE'])
def process_date():
	if request.method == 'GET':
		if request.method == 'GET':
			req = session.query(MealDate).filter_by(id = id).first()
			if req:
				return jsonify(req.serialize)
			else:
				return jsonify({'error': 'request does not exist'})
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		req = session.query(Proposal).filter_by(id = id)
		session.delete(req)
		session.commit()


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)