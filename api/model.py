#imported libs
import os
from sqlalchemy import Column,Integer,String, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as JSONWebSignatureSerializer, BadSignature, SignatureExpired)
from redis import Redis
Base = declarative_base()


db_filename = os.path.dirname(os.path.dirname(__file__))+'/project.db'
engine = create_engine('sqlite:///'+db_filename)

secret_key = "fish"

class User(Base):
    __tablename__ = 'user'
    sqlite_autoincrement=True
    id = Column(Integer, primary_key=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'picture' : self.picture,
            'email' : self.email
        }

    @staticmethod
    def hash_password(password):
        return  pwd_context.encrypt(password)

    @staticmethod
    def verify_password(password, hashed_password):
        return pwd_context.verify(password, hashed_password)

    @staticmethod
    def generate_auth_token(id, expiration=1000):
        s = JSONWebSignatureSerializer(secret_key, expires_in = expiration)
        #convert to string
        return s.dumps({'id': id }).decode("utf-8")

    @staticmethod
    def verify_auth_token(token):
        s = JSONWebSignatureSerializer(secret_key)
        try:
            #verify data is okay or throw exception
            data = s.loads(token, None, True)
            print data
            #check that this token is still valid, should return None to indicate not found in invalid store
            redis = Redis()

            if redis.get(token) is not None:
                print redis.get(token)
                raise Exception('Invalid token')
        except SignatureExpired:
            #Valid Token, but expired

            return None
        except BadSignature:
            #Invalid Token
            return None
        except Exception:
            #token is found in invalid token list
            print 'exception'
            return None
        #user_id = data[0]['id']
        #({'id': 2}, {'alg': 'HS256', 'exp': 1559820061, 'iat': 1459814061})
        return data


class Request(Base):
    __tablename__ = 'request'
    sqlite_autoincrement=True
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    meal_type = Column(String(50))
    location_string = Column(String(100))
    latitude = Column(String(200))
    longitude = Column(String(200))
    meal_time = Column(DateTime)
    filled = Column(Boolean, default=False)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'user_id' : self.user_id,
            'meal_type' : self.meal_type,
            'location_string' : self.location_string,
            'latitude' : self.latitude,
            'longitude' : self.longitude,
            'meal_time' : self.meal_time,
            'filled' : self.filled
        }

class Proposal(Base):
    __tablename__ = 'proposal'
    sqlite_autoincrement=True
    id = Column(Integer, primary_key=True)
    user_proposed_to = Column(Integer, ForeignKey('user.id'))
    user_proposed_from = Column(Integer, ForeignKey('user.id'))
    request_id = Column(Integer, ForeignKey('request.id'))
    filled = Column(Boolean, default=False)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'user_proposed_to' : self.user_proposed_to,
            'user_proposed_from' : self.user_proposed_from,
            'request_id' : self.request_id,
            'filled' : self.filled
        }

class MealDate(Base):
    __tablename__= 'meal_date'
    sqlite_autoincrement=True
    id = Column(Integer, primary_key=True)
    user_1 = Column(Integer, ForeignKey('user.id'))
    user_2 = Column(Integer, ForeignKey('user.id'))
    
    restaurant_name = Column(String(100))
    restaurant_address = Column(String)
    restaurant_picture = Column(String)
    meal_time = Column(DateTime)

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'user_1' : self.user_1,
            'user_2' : self.user_2,
            'restaurant_name' : self.restaurant_name,
            'restaurant_address' : self.restaurant_address,
            'restaurant_picture' : self.restaurant_picture,
            'meal_time' : self.meal_time
        }
    
#creates the database
def create_db():
    try:
        os.remove(db_filename)
    except OSError:
        pass
    finally:
        Base.metadata.create_all(engine)


def get_db_session():
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session

