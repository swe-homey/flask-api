import json
from flask import Flask, Response, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.schema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, query
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import JSON, Column, String, Integer, create_engine, Insert, select
import mysql.connector
from sqlalchemy.types import Enum, PickleType
import enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
import os
import pickle
from dotenv import load_dotenv



load_dotenv() #load environment variables



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://'+os.getenv("MYSQL_USERNAME")+ ':' + os.getenv("MYSQL_PASSWORD") + '@localhost/homey_db'

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo = True)
Session = sessionmaker(bind = engine)
session = Session()

# enums

class PropertyType(str, enum.Enum):
    RENT = "rent"
    SALE = "sale"

# models in the database are init here. make sure database parameters do not change!
# if changing any of the models, drop the table on sqlworkbench first, then reinitialise them.
# models
class Account(db.Model): 
    __tablename__ = 'UserAccounts'
    userID = Column('userID', Integer, primary_key=True, unique=True)
    userName = Column('userName', String(100), unique=True)
    password = Column('password', String(100))
    email = Column('email', String(100))
    savedListings = Column('savedListings', Integer)
    address = Column('address', String(100))

    def __init__ (self, userID, userName, password, email, savedListings, address):
        self.userID = userID
        self.userName = userName
        self.password = password
        self.email = email
        self.savedListings = savedListings
        self.address = address

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Property(db.Model):
    __tablename__ = 'Property'
    id = Column('id', String(100), primary_key=True)
    clusterId = Column('clusterId', String(100))
    type = Column('type', Enum(PropertyType))
    # UserSaved = Column('UserSaved', )

    def __init__(self, id, clusterId, type):
        self.id = id
        self.clusterId = clusterId
        self.type = type
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserSavedProperty(db.Model):
    __tablename__ = 'savedListings'
    userID = Column('userID', String(100))
    propertyId = Column('propertyId', String(100))
    property = Column('property', PickleType) 
    __table_args__ = (
        PrimaryKeyConstraint(userID, propertyId),
        {},
    )

    def __init__(self, userID, propertyId, property):
        self.userID = userID
        self.propertyId = propertyId
        self.property = property

    def as_dict(self):
        dicout = {}
        for col in self.__table__.columns:

            if col.name=="userID":
                dicout["userID"] = getattr(self, col.name)
            if col.name=="propertyId":
                dicout["propertyId"] = getattr(self, col.name)
            if col.name=="property":
                dicout["property"] = pickle.loads(getattr(self,col.name))

        return dicout


# routes
@app.route("/createUser", methods=["POST"])
def createUser():
    # data = json.loads('{"userID": 12, "userName": "hello", "password": "1234", "email": "hello@gmail.com", "savedListings": 9, "address": "clementi"}')
    data = request.get_json() #get json payload from the post req
    new_row = Account(userID=data['userID'], userName=data['userName'], password=data['password'], email=data['email'], savedListings=data['savedListings'], address=data['address'])
    db.session.add(new_row)
    db.session.commit()

    return "user created"

@app.route("/viewUser/<int:user_id>", methods=["GET"])
def viewUser(user_id):
    if request.method == 'GET':
        account = db.session.query(Account).filter_by(userID = user_id)

        if account.first() is None:
            return f"Account with userID {user_id} does not exist"
        
        else:

            acc = account[0]

            accout = acc.as_dict()
            return json.dumps(accout)

            # return json.dumps("userID: {acc.userID}, userName: {acc.userName}, password: {acc.password}, email: {acc.email}, savedListings: {acc.savedListings}, address: {acc.address}}")



@app.route("/deleteUser/<int:userID>", methods=["GET"])
def deleteUser(userID):
    if request.method == 'GET':
        account = Account.query.filter_by(userID=userID).first()
        if account is None:
            return f"Account with userID {userID} does not exist"
        
        else:
            db.session.delete(account)
            db.session.commit()

            return f"Account with userID {userID} has been deleted"
        
    else: 
        return "method not allowed"
    
@app.route("/updateUser/<int:user_id>", methods=["POST"])
def updateUser(user_id): 
    if request.method =="POST":
        account = db.session.query(Account).filter_by(userID = user_id)
        acc = account[0]
        data = request.get_json()

        acc.userID = data['userID']
        acc.userName = data['userName']
        acc.password = data['password']
        acc.email = data['email']
        acc.savedListings = data['savedListings']
        acc.address = data['address']

        db.session.commit()

        if account.first() is None:
            return "Account no exist"
        else:
            return "Account successfully updated!"
    else: 
        return "update failed"
    

@app.route("/createProperty", methods=["POST"])
def createProperty():
    # data = json.loads('{"id": 1, "clusterId": "1", "type": "RENT"}')
    data = request.get_json() #get json payload from the post req
    print(data)
    if "type" not in data:
        new_row = Property(id=data['id'], clusterId=data['clusterId'], type=PropertyType.RENT)
    else:
        new_row = Property(id=data['id'], clusterId=data['clusterId'], type=data["type"])
    db.session.add(new_row)
    db.session.commit()

    return "property created"

@app.route("/viewProperty/<int:prop_id>", methods=["GET"])
def viewProp(prop_id):
    if request.method == 'GET':
        property = db.session.query(Property).filter_by(id = prop_id)

        if property.first() is None:
            return f"Property with PropID {prop_id} does not exist"
        
        else:

            prop = property[0]
            propout = prop.as_dict()

            return json.dumps(propout)

@app.route("/deleteProperty/<int:prop_id>", methods=["GET"])
def deleteProperty(prop_id):
    if request.method == 'GET':
        property = Property.query.filter_by(id=prop_id).first()
        if property is None:
            return f"Property with Property_ID {prop_id} does not exist"
        
        else:
            db.session.delete(property)
            db.session.commit()

            return f"Property with id {prop_id} has been deleted"
        
    else: 
        return "method not allowed"

@app.route("/updateProperty/<int:prop_id>", methods=["POST"])
def updateProperty(prop_id): 
    if request.method =="POST":
        property = db.session.query(Property).filter_by(id = prop_id)
        prop = property[0]
        data = request.get_json()

        prop.id = data['id']
        prop.clusterId = data['clusterId']
        prop.type = data['type']

        db.session.commit()

        if property.first() is None:
            return "Property no exist"
        else:
            return "Property successfully updated!"
    else: 
        return "update failed"




@app.route("/createUserSavedProperty", methods=["POST"])
def createUserSavedProperty():
    # data = json.loads({"userID" : "1","propertyId" : "1", "property": {"id": 12, "clusterId": "1", "type": "RENT"}})
    data = request.get_json()
    pickledProperty = pickle.dumps(data["property"])
    new_row = UserSavedProperty(userID=data["userID"], propertyId=data["propertyId"], property=pickledProperty)
    db.session.add(new_row)
    db.session.commit()

    return "usp created"

@app.route("/viewUSP/<int:user_id>", methods=["GET"])
def viewUSP(user_id):
    if request.method == 'GET':
        usp = db.session.query(UserSavedProperty).filter_by(userID = user_id).all()
        if len(usp)==0:
            return f"User with userID {user_id} has no saved listings"
        
        else:
            listout = []
            for savedListing in usp:
                listout.append(savedListing.as_dict())
            return json.dumps({"result": listout})

@app.route("/deleteUSP/<int:user_id>/<int:prop_id>", methods=["GET"])
def deleteUSP(user_id,prop_id):
    if request.method == 'GET':
        usp = UserSavedProperty.query.filter_by(userID = user_id, propertyId=prop_id).first()
        if usp is None:
            return f"USP does not exist"
        
        else:
            db.session.delete(usp)
            db.session.commit()

            return f"USP has been deleted"
        
    else: 
        return "method not allowed"
    

if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(host='0.0.0.0', debug=True)



#1) Check if user and property exists
#1.1) If user doesn't exists, exit (NOT_FOUND)
#1.2) if property doesn't exists, create new Property 
#2) if both property and user exists, create a new UserSavedProperty
#3) return all UserSavedProperty with matching userID