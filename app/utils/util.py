from jose import jwt,JWTError
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "super secret secrets"

def encode_token(customer_id):
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(customer_id)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            
            if not token:
                return jsonify({"error": "Token is missing!"}), 401
            
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                print(data)
                customer_id = int(data['sub'])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired!"}), 401
            except JWTError:
                return jsonify({"error": "Invalid token!"}), 401
            
            return f(customer_id, *args, **kwargs)
        
        else:
            return jsonify({"error": "You must be logged in to access this"}), 401
        
    return decorated