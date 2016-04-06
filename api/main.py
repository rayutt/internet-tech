import time
from functools import update_wrapper
from flask import Flask, jsonify, make_response, request, g
from map import Maps
from forsq import forsqure
import limit
from model import Base, User, Request, Proposal, MealDate, get_db_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, or_, and_
import json, datetime, decimal
from functools import wraps
from datetime import datetime
from flask.ext.autodoc import Autodoc
import requests
from redis import Redis
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask.ext.httpauth import HTTPBasicAuth
import requests

auth = HTTPBasicAuth()
session = get_db_session()
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
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
		data = User.verify_auth_token(token) if token else None
		print data
		if data:
			g.user = data[0]['id']
			print g.user
			g.token = token
			g.token_expire = data[1]['exp']
			return func(*args, **kwargs)
		else:
			return jsonify({'error': 'Invalid token', 'redirect' : '/' })
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

		#STEP 1 - Parse the auth code
	    auth_code = request.json.get('auth_code')
	    print "Step 1 - Complete, received auth code %s" % auth_code
	    if provider == 'google':
	        #STEP 2 - Exchange for a token
	        try:
	            # Upgrade the authorization code into a credentials object
	            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
	            oauth_flow.redirect_uri = 'postmessage'
	            credentials = oauth_flow.step2_exchange(auth_code)
	        except FlowExchangeError:
	            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
	            response.headers['Content-Type'] = 'application/json'
	            return response
	          
	        # Check that the access token is valid.
	        access_token = credentials.access_token
	        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	        h = httplib2.Http()
	        result = json.loads(h.request(url, 'GET')[1])
	        # If there was an error in the access token info, abort.
	        if result.get('error') is not None:
	            response = make_response(json.dumps(result.get('error')), 500)
	            response.headers['Content-Type'] = 'application/json'
	        print "Step 2 Complete! Access Token : %s " % credentials.access_token

	        #STEP 3 - Find User or make a new one
	        
	        #Get user info
	        h = httplib2.Http()
	        userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
	        params = {'access_token': credentials.access_token, 'alt':'json'}
	        answer = requests.get(userinfo_url, params=params)
	      
	        data = answer.json()

	        name = data['name']
	        picture = data['picture']
	        email = data['email']
        	user = session.query(User).filter_by(email = email).first()
        
	        #see if user exists, if it doesn't make a new one
	        user = session.query(User).filter_by(email=email).first()
	        if not user:
	            user = User(username = name, picture = picture, email = email)
	            session.add(user)
	            session.commit()
	        

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

#token is sent via the header
@app.route('/api/v1/<provider>/logout', methods=['POST'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def logout(provider):
	#redis calls should be move to a singliton design
	redis = Redis()
	token = request.headers.get('Authorization')
	data = User.verify_auth_token(token)
	p = redis.pipeline()
	p.incr(token) # increments key
	p.expireat(token, data[1]['exp']) # expires based on the reset value
	results = p.execute()
	if results[0] >= 1 and results[1] == True:
		return jsonify({'data': 'Successfully logged out'})
	else:
		return jsonify({'error': 'Error logging out'})

#
@app.route('/api/v1/users', methods=['GET','POST'])
@auto.doc()
@limit.ratelimit(limit=1, per=10 * 1)
def process_users():
	if request.method == 'GET':
		users = session.query(User).all()
		return jsonify(users = [u.serialize for u in users])
	elif request.method == 'POST':
		email = request.json['email']
		password = request.json['password']
		#issue uploading picture
		#picture = request.json['picture']
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
	

#
@app.route('/api/v1/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auto.doc()
@limit.ratelimit(limit=2, per=10 * 1)
@require_token
def process_user(id):
	if request.method =='GET':	
		user = session.query(User).filter_by(id = id).first()
		if user:
			return jsonify(user.serialize)
		else:
			return jsonify({'error': 'user does not exist'})
	elif request.method == 'PUT':
			if g.user==request.json['id']:
				user = session.query(User).filter_by(id = g.user).first()
				if user:
					user.email = request.json['email']
					print user.email
					user.picture = request.json['picture']
					session.commit()
					return jsonify({'success': 'update sucessful'})
				else:
					return jsonify({'error': 'update failed'})
			else:
				return jsonify({'error': 'You can not edit another users profile'})

	elif request.method == 'DELETE':
		user = session.query(User).filter_by(id = g.user).first()
		if user:
			session.delete(user)
			session.commit()
			return jsonify({'success': 'dalete sucessful'})
		else:
			return jsonify({'error': 'dalete failed'})
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
		req = session.query(Request).filter_by(id = id).first()
		if req:
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
		else:
			return jsonify({'error': 'update failed'})
	elif request.method == 'DELETE':
		req = session.query(Request).filter_by(id = id, user_id=g.user).first()
		if req:
			session.delete(req)
			session.commit()
			return jsonify({'success': 'delete sucessful'})
		else:
			return jsonify({'error': 'fail sucessful'})
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
		if prop:
			session.delete(prop)
			session.commit()
			return jsonify({'success': 'dalete sucessful'})
		else:
			return jsonify({'error': 'dalete failed'})
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
def process_date(id):
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
		req = session.query(MealDate).filter(and_(MealDate.id == id, (or_(MealDate.user_2==g.user, MealDate.user_2==g.user)) )).first()
		if req:
			session.delete(req)
			session.commit()
			return jsonify({'success': 'delete sucessful'})
		else:
			return jsonify({'error': 'delete failed'})

#creates documentation
@app.route('/documentation')
def documentation():
    return auto.html()

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)