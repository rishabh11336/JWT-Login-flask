from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
with app.app_context():
    db.create_all()

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']

        if not username or not password:
            return {'message': 'Username and password required'}, 400
        if User.query.filter_by(username=username).first():
            return {'message': 'User already exists'}, 400
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User created successfully'}, 201
class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(seconds=30))
            return {'access token': access_token}, 200
        return {'message': 'Incorrect credentials'}, 400
    
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {'message': f'This is a protected resource for user {current_user}'}, 200

    
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(ProtectedResource, '/secure', endpoint='secure')


if __name__ == '__main__':
    app.run(debug=True)