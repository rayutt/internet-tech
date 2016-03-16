#imported libs
from sqlalchemy import Column,Integer,String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'id': self.id })

    @staticmethod
    def verify_auth_token(token):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['id']
    	return user_id


class Request(Base):
 	__tablename__ = 'requests'
 	rid = Column(Integer, primary_key=True)
 	user_id = Column(Integer, ForeignKey('user.id'))
 	meal_type = Column(String(50))
 	location_string = Column(String(100))
 	latitude = Column(String(200))
 	longitude = Column(String(200))
 	meal_time = Column(String)
 	filled = Column(String)
 	user = relationship("Request", backref ="requests")

class Proposal(Base):
    __tablename__ = 'proposals'
    pid = Column(Integer, primary_key=True)
    user_proposed_to = Column(Integer)
    user_proposed_from = Column(Integer)
    request_id = Column(Integer, ForeignKey('requests.rid'))
    filled = Column(String(10))
    request = relationship("Proposal", backref ="proposals")

class MealDate(Base):
    __tablename__= 'mealDates'
    rid = Column(Integer, primary_key=True)
    user_1 = Column(Integer)
    user_2= Column(Integer)
    restaurant_name = Column(String(100))
    restaurant_address = Column(String)
    restauramt_picture = Column(String)
    meal_time = Column(String)
    
#creates the database

engine = create_engine('sqlite:///project.db')

Base.metadata.create_all(engine)