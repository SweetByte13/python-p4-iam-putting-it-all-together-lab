#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        params = request.json
        try:
            user = User(username=params.get('username'), image_url=params.get('image_url'), bio=params.get('bio') )
            user.password_hash = params.get('password')
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return make_response(user.to_dict(), 201)
        except ValueError as ve:
            return make_response(jsonify({'error': str(ve)}), 422)
        except Exception as e:
            return make_response({"error": f'An error occurred during signup: {str(e)}'}, 422)

class CheckSession(Resource):
    def get (self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                return make_response(user.to_dict(), 200)
        return make_response({'error': 'Unauthorized: Must login'}, 401)

class Login(Resource):
    def post(self):
        params = request.json
        user = User.query.filter_by( username=params.get('username')).first()
        if not user:
            return make_response({'error': 'user not found'}, 401)
        if user.authenticate(params.get('password')):
            session['user_id']=user.id
            return make_response(user.to_dict())
        else:
            return make_response({'error': 'invalid password' }, 401)

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if user_id:
            session['user_id'] = None
            return make_response({}, 204)
        return make_response({"error": "Unauthorized: Must login"}, 401)

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            recipes=[recipe.to_dict() for recipe in Recipe.query.all()]
            return make_response(recipes, 200)
        return make_response({"error": "Unauthorized: Must login"}, 401) 
    
    def post(self):
        user_id = session.get('user_id')
        if user_id:
            data = request.json
            try:
                recipe = Recipe(
                    title=data.get('title'),
                    instructions=data.get('instructions'),
                    minutes_to_complete=data.get('minutes_to_complete'),
                    user_id=user_id
                )
                db.session.add(recipe)
                db.session.commit()
                return make_response(recipe.to_dict(), 201)
            except Exception:
                return make_response({"error": "Recipe is not valid"}, 422)
        return make_response({"error": "Unauthorized: Must login"}, 401) 

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)