from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    serialize_only=('id','username', 'image_url', 'bio',)
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    
    recipes = db.relationship('Recipe', order_by='Recipe.id', back_populates= 'user', cascade="all, delete-orphan")
    
    
    @property
    def password_hash(self):
        self._password_hash
        raise AttributeError('password_hash is not a readable attribute')
    
    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def authenticate(self, password):
        return bcrypt.check_password_hash( self._password_hash, password)
        
    @validates('username')
    def validates_username(self, key, new_username):
        if not new_username:
            raise ValueError("Must have a username")
        elif User.query.filter(User.username == new_username).first():
            raise ValueError("Username is already in use")
        return new_username
            
    
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    user = db.relationship('User', back_populates= 'recipes')
    
    @validates('title')
    def validates_title(self, key, new_title):
        if not new_title:
            raise ValueError("Must have a title")
        return new_title
        
    @validates('instructions')
    def validates_instructions(self, key, new_instructions):
        if not new_instructions:
            raise ValueError("Must have instructions")
        elif len(new_instructions) < 50:
            raise ValueError("Instructions must be 50 characters long or more.")
        return new_instructions