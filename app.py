from functools import wraps

import jwt
from flask import Flask, request, jsonify
from functionalities import *
from sqlalchemy import create_engine
from models import *
from managers import *
from Config import config
import datetime
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import text

SECRET_KEY = config("secret_key")

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if the token is passed in the request headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if auth_header.startswith('Bearer ') else None

        # If the token is missing, return an error
        if not token:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            # Decode the token using the secret key
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = data['user_id']

            # Query the user by ID (you can use this user for protected routes)
            with Session(engine) as session:
                current_user = session.query(User).get(user_id)
                if not current_user:
                    return jsonify({"message": "User not found!"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(current_user, *args, **kwargs)  # Pass the user to the protected route

    return decorated


@login_manager.user_loader
def load_user(user_id, session: Session):
    return session.get(User, user_id)


login_manager.init_app(app)


@app.route("/")
def home():
    return "<p>Hello, World!</p>"


@app.route("/register", methods=["POST"])
def register():
    req = request.json
    username = req['username']
    password = req['password']
    user = User(username=username)
    user.set_password(password)
    with Session(engine) as session:
        user_check = session.query(User).filter_by(username=user.username).first()
        if user_check:
            return jsonify({"message": "User already exists!"}), 401
        session.add(user)
        session.commit()

        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration time
        }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token}), 200


@app.route("/login", methods=["POST"])
def login():
    req = request.json
    username = req['username']
    password = req['password']

    with Session(engine) as session:
        # Query the user by username
        user = session.query(User).filter_by(username=username).first()

        # Check if user exists and if the password is correct
        if user and user.check_password(password):
            # Generate a JWT token
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration time
            }, SECRET_KEY, algorithm="HS256")

            return jsonify({"token": token}), 200
        return jsonify({"message": "Invalid username or password"}), 401


@app.route("/get_user_info", methods=['POST'])
@token_required
def user_info(user):
    return {"username": user.username}


@app.route("/sum", methods=["GET", "POST"])
def sum_page():
    try:
        return {
            "response": sum_numbers(
                *[request.args[k] for k in request.args.keys() if "num" in k]
            )
        }
    except Exception as ex:
        return {"error": str(ex)}, 500


@app.route("/pow/<arg1>/<arg2>")
def pow(arg1, arg2):
    return {"response": int(arg1) ** int(arg2)}


@app.route("/prices", methods=["GET", "POST"])
def prices():
    return jsonify(get_prices(request.args['ticker']))


@app.route("/upload_price", methods=["GET", "POST"])
def upload_prices():
    ticker = request.args['ticker']
    prices_data = get_prices(ticker)
    with Session(engine) as session:
        for price in prices_data:
            entry = HistModel(date=price['Date'], close=price['Close'], ticker=ticker.upper())
            existing_entry = session.query(HistModel).filter_by(date=price['Date'], ticker=ticker.upper()).first()
            if existing_entry:
                existing_entry.close = price['Close']
            else:
                session.add(entry)
        session.commit()

    # upload_via_pandas(ticker, engine)

    return {"status": "OK"}, 200


@app.route("/ask_llm", methods=["GET", "POST"])
def ask_llm():
    request_analyst = request.args['request_analyst']
    sql_query = get_sql_query(request_analyst)
    with engine.connect() as connection:
        result = connection.execute(text(sql_query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return {"status": "OK", "result": df.to_dict('records')}, 200


if __name__ == "__main__":
    engine = create_engine(config("conn_str"), echo=True)
    Base.metadata.create_all(engine)
    app.run(host='0.0.0.0')
