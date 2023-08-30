from flask import Flask, request, jsonify, make_response, render_template, session
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os
import urllib.parse

app = Flask(__name__)
key = os.urandom(24)
app.config['SECRET_KEY'] = key
print(key)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Print or log the decoded data here for debugging
        except jwt.ExpiredSignatureError:
            return jsonify({'Alert': 'Token has expired'}), 401
        except jwt.DecodeError:
            return jsonify({'Alert': 'Invalid Token'}), 401
        return func(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return '<center><h1>Jwt login system Authentication Done!</h1></center>'

@app.route('/public')
def public():
    return 'For Public'

@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified. Welcome to the dashboard.'

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] and request.form['password'] == '123456':
        session['logged_in'] = True
        token_payload = {
            'user': request.form['username'],
            'expiration': str(datetime.utcnow() + timedelta(seconds=60))
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm="HS256")
        encoded_token = urllib.parse.quote(token)
        return f'<a href="http://localhost:5000/auth?token={encoded_token}">auth</a> <br> <p>{encoded_token}</p>'
    else:
        return make_response('Unable to verify', 403, {'www-Authenticate': 'Basic realm:"Authentication Failed!"'})

if __name__ == '__main__':
    app.run(debug=True)