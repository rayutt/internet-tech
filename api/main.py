import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify
from map import Maps
from forsq import forsqure
import limit
from model import Base, User, Request, Proposal, MealDate, get_db_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, or_
import json, datetime, decimal
from functools import wraps
from datetime import datetime
from flask.ext.autodoc import Autodoc


session = get_db_session()

app = Flask(__name__, static_url_path = "")
auto = Autodoc(app)

@app.after_request
def inject_headers(response):
	return limit.inject_x_rate_headers(response)

#test code
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
	@wraps(func)
	def validate(*args, **kwargs):
		print 'before token call'
		token = request.headers.get('Authorization')
		print token
		id = User.verify_auth_token(token) if token else None
		if id:
			g.user = id
			return func(*args, **kwargs)
		else:
			return jsonify({'error': 'Invalid token'})
	return validate
	
#START main

#directs to the home page

@app.route('/')
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
def root():
  return app.send_static_file("index.html")


@app.route('/api/v1/<provider>/login', methods=['POST'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
def login(provider):
	if provider == 'gmail':
		return get_not_implemented_msg()
	elif provider == 'facebook':
		return get_not_implemented_msg()
	elif provider == 'app':
		email = request.json['email']
		password = request.json['password']
		user = session.query(User).filter_by(email = email).first()

		if user and User.verify_password(password, user.password_hash):
			return jsonify({'token': User.generate_auth_token(user.id)})
		else:
			#keep error message generic to avoid leaking info to attacker
			return jsonify({'error': 'Invalid username and/or password'})
#
@app.route('/api/v1/<provider>/logout', methods=['POST'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
def logout(provider):
    return get_not_implemented_msg()

#
@app.route('/api/v1/users', methods=['GET','POST', 'PUT', 'DELETE'])
@auto.doc()
@limit.ratelimit(limit=1, per=10 * 1)
@require_token
def process_users():
	if request.method == 'GET':
		users = session.query(User).all()
		return jsonify(users = [u.serialize for u in users])
	elif request.method == 'POST':
		email = request.json['email']
		password = request.json['password']

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
		user = User.query(id)
		user.password_hash = request.json['password_hash']
		user.picture = request.json['picture']
		session.commit()
		return jsonify({'success': 'update sucessful'})
		
	elif request.method == 'DELETE':
		user = session.query(User).filter_by(id = g.user).first()
		session.delete(user)
		session.commit()
		return jsonify({'success': 'dalete sucessful'})

#
@app.route('/api/v1/users/<int:id>', methods=['GET'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_user(id):
	#TODO include his requests/dates/proposals etc
	user = session.query(User).filter_by(id = id).first()
	if user:
		return jsonify(user.serialize)
	else:
		return jsonify({'error': 'user does not exist'})

#
@app.route('/api/v1/requests', methods=['GET','POST'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_requests():
	if request.method == 'GET':
		requests = session.query(Request).all()
		return jsonify(requests = [r.serialize for r in requests])
	elif request.method == 'POST':
		user_id = g.user
		meal_type = request.json['meal_type']
		location_string = request.json['location_string']
		geoloc = Maps.getGeocodeLocation(location_string)
		#output example from maps api
		#{u'lat': 10.5168387, u'lng': -61.4114482}
		latitude = geoloc['lat']
		longitude = geoloc['lng']
		#converts the json date into python date
		meal_time = datetime.strptime(request.json['meal_time'], '%Y-%m-%d %H:%M:%S')
		#creates a new request
		if(user_id, meal_type, location_string, latitude, longitude, meal_time):
			newRequest = Request(user_id = user_id, meal_type = meal_type, location_string=location_string,
							  latitude=latitude,longitude=longitude, meal_time=meal_time)
			session.add(newRequest)
			session.commit()
			return jsonify(newRequest.serialize)
		else:
			return get_invalid_input_msg("meal_type, location_string, latitude, longitude, meal_time")

#
@app.route('/api/v1/requests/<int:id>', methods=['GET','PUT','DELETE'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_request(id):
	if request.method == 'GET':
		req = session.query(Request).filter_by(id = id).first()
		if req:
			return jsonify(req.serialize)
		else:
			return jsonify({'error': 'request does not exist'})
	elif request.method == 'PUT':
		req = session.query(Request).filter_by(id = id, user_id=g.user).first()
		req.meal_type = request.json['meal_type']
		req.location_string = request.json['location_string']
		geoloc = Maps.getGeocodeLocation(req.location_string)
		#output example from maps api
		#{u'lat': 10.5168387, u'lng': -61.4114482}
		req.latitude = geoloc['lat']
		req.longitude = geoloc['lng']
		#converts the json date into python date
		req.meal_time = datetime.strptime(request.json['meal_time'], '%Y-%m-%d %H:%M:%S')
		session.commit()
		return jsonify({'success': 'update sucessful'})
	elif request.method == 'DELETE':
		req = session.query(Request).filter_by(id = id, user_id=g.user).first()
		session.delete(req)
		session.commit()
		return jsonify({'success': 'dalete sucessful'})
#
@app.route('/api/v1/proposals', methods=['GET','POST'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_proposals():
	if request.method == 'GET':
		proposals = session.query(Proposal).all()
		return jsonify(proposals = [p.serialize for p in proposals])
		
	elif request.method =='POST':
		user_proposed_from = g.user
		request_id = request.json['request_id']
		user_proposed_to = request.json['user_proposed_to']
		if(user_proposed_from, request_id, user_proposed_to):
			newProposal = Proposal(user_proposed_from = user_proposed_from, user_proposed_to=user_proposed_to, request_id=request_id)
			session.add(newProposal)
			session.commit()
			return jsonify(newProposal.serialize)
		else:
			return get_invalid_input_msg("user_proposed_from, request_id, user_proposed_to")

#	
@app.route('/api/v1/proposals/<int:id>', methods=['GET','PUT','DELETE'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_proposal(id):
	if request.method == 'GET':
		req = session.query(Proposal).filter_by(id = id).first()
		if req:
			return jsonify(req.serialize)
		else:
			return jsonify({'error': 'proposal does not exist'})
	elif request.method == 'PUT':
		req = session.query(Proposal).filter_by(pid = id, user_proposed_to=g.user).first()
		req.filled = request.json['filled']
		session.commit()
		return jsonify({'success': 'update sucessful'})
	elif request.method == 'DELETE':
		#and or require for sql
		prop = session.query(Proposal).filter_by(id = id).first()
		session.delete(prop)
		session.commit()
		return jsonify({'success': 'dalete sucessful'})

#
@app.route('/api/v1/dates', methods=['GET','POST'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_dates():
	if request.method == 'GET':
		dates = session.query(MealDate).filter(or_(MealDate.user_2==g.user, MealDate.user_2==g.user))
		return jsonify(dates = [d.serialize for d in dates])
		
	elif request.method == 'POST':
		user_2 = g.user
		request_id = request.json['request_id']
		user_1 = request.json['user_1']
		meal_time = request.json['meal_time']
		req = session.query(Request).filter_by(id = request_id).first()
		meal_type=req.meal_type
		restaurant=forsqure.findAResturant(req.meal_type, req.location_string)
		restaurant_name = restaurant['name']
		restaurant_address = restaurant['address']
		restaurant_picture = restaurant['image']
		if(user_2,user_1,meal_time,restaurant_name,restaurant_address,restaurant_picture):
			newMealDate = MealDate(user_2 = user_2, user_1=user_1, restaurant_name=restaurant_name, restaurant_address=restaurant_address, restaurant_picture=restaurant_picture)
			session.add(newMealDate)
			session.commit()
			return jsonify(newMealDate.serialize)
		else:
			return get_invalid_input_msg("user_2,user_1,meal_time,restaurant_name,restaurant_address,restaurant_picture")
#
@app.route('/api/v1/dates/<int:id>', methods=['GET','PUT','DELETE'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_date():
	if request.method == 'GET':
		if request.method == 'GET':
			req = session.query(MealDate).filter_by(id = id).first()
			if req:
				return jsonify(req.serialize)
			else:
				return jsonify({'error': 'date does not exist'})
	elif request.method == 'PUT':
		return get_not_implemented_msg()
	elif request.method == 'DELETE':
		req = session.query(MealDate).filter_by(id = id).first()
		session.delete(req)
		session.commit()
		return jsonify({'success': 'dalete sucessful'})

#creates documentation
@app.route('/documentation')
def documentation():
    return auto.html()

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)