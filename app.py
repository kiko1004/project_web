from flask import Flask, request, jsonify
from functionalities import *
from sqlalchemy import create_engine
from models import *
from Config import config

app = Flask(__name__)


@app.route("/")
def home():
    return "<p>Hello, World!</p>"


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
        prices_lst = []
        for price in prices_data:
            prices_lst.append(HistModel(date=price['Date'], close=price['Close'], ticker=ticker.upper()))
        session.add_all(prices_lst)
        session.commit()

    # upload_via_pandas(ticker, engine)


    return {"status":"OK"}, 200


if __name__ == "__main__":
    engine = create_engine(config("conn_str"), echo=True)
    Base.metadata.create_all(engine)
    app.run()
