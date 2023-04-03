from sqlalchemy import Column, String, Boolean
from app import db
from sqlalchemy.types import PickleType, Enum
from sqlalchemy.schema import PrimaryKeyConstraint
import enum
import pickle


class PropertyType(str, enum.Enum):
    RENT = "rent"
    SALE = "sale"

# models in the database are init here. make sure database parameters do not change!
# if changing any of the models, drop the table on sqlworkbench first, then reinitialise them.
# models
class User(db.Model): 
    __tablename__ = 'User'
    id = Column('id', String(25), primary_key=True, unique=True)
    name = Column('name', String(100))
    email = Column('email', String(100), unique=True)
    password = Column('password', String(100))
    propertySaved = Column('propertySaved', PickleType)
    image = Column('image', String(256))


    def __init__ (self, id, name, email,password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.propertySaved = pickle.dumps([])
        self.image = ""


    def as_dict(self):
        dicout = {}
        for col in self.__table__.columns:
            if col.name=="id":
                dicout["id"] = getattr(self,col.name)
            if col.name=="name":
                dicout["name"] = getattr(self,col.name)
            if col.name=="email":
                dicout["email"] = getattr(self,col.name)
            if col.name=="password":
                dicout["password"] = getattr(self,col.name)
            if col.name=="propertySaved":
                dicout["propertySaved"] = pickle.loads(getattr(self,col.name))
            if col.name=="image":
                dicout["image"] = getattr(self, col.name)
        return dicout

class Property(db.Model):
    __tablename__ = 'Property'
    id = Column('id', String(100), primary_key=True)
    clusterId = Column('clusterId', String(100))
    type = Column('type', Enum(PropertyType))
    stringifiedListing = Column('stringifiedListing', String(512))
    isAvailable = Column('isAvailable', Boolean)
    # UserSaved = Column('UserSaved', )

    def __init__(self, id, clusterId, type, stringifiedListing, isAvailable):
        self.id = id
        self.clusterId = clusterId
        self.type = type
        self.stringifiedListing = stringifiedListing
        self.isAvailable = isAvailable
    
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