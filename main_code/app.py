from flask import Flask, render_template, request , send_from_directory, jsonify, session
from api_handler import get_supported_currencies, convert_currency, api_blueprint, news_bp
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.secret_key = os.getenv("SECRET_KEY") 

app.register_blueprint(api_blueprint)
app.register_blueprint(news_bp)


@app.route('/', methods=['GET', 'POST'])
def index():
    currencies_api = get_supported_currencies()
    json_path = os.path.join(os.path.dirname(__file__), "currency_meta.json")
    with open(json_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    # Merge meta into API result
    currencies = {}
    for code in currencies_api:
        country = meta_data.get(code, {}).get("country", currencies_api[code]["description"])
        flag = meta_data.get(code, {}).get("flag", None)
        currencies[code] = {
            "country": country,
            "flag": flag,
        }

    symbols_path = os.path.join(os.path.dirname(__file__), "currency_symbols.json")
    with open(symbols_path, "r", encoding="utf-8") as f:
        currency_symbols = json.load(f)

    result = session.get('result')
    second_result = session.get('second_result')
    display_amount = session.get('display_amount')

    unit_labels = {
        1_000:   "Thousand",
        1_000_000:   "Million",
        1_000_000_000:   "Billion",
        1_000_000_000_000: "Trillion"
    }

    if request.method == 'POST':
        form_type = request.form.get("form_type", "main_convert")

        from_currency = request.form['from_currency']
        to_currency = request.form['to_currency']

        if form_type == "second_convert":
            # Split form logic
            raw_amount = float(request.form['split_amount'])
            multiplier = float(request.form['unit_multiplier'])
            final_amount = raw_amount * multiplier
            second_result = convert_currency(from_currency, to_currency, final_amount)
            label = unit_labels.get(multiplier, str(multiplier))
            display_amount = f"{raw_amount:.2f} {label}"

            # Save second form result
            session['second_result'] = second_result
            session['display_amount'] = display_amount

        else:
            # Default form
            amount = float(request.form['amount'])
            result = convert_currency(from_currency, to_currency, amount)

            session['result'] = result

    json_path = os.path.join(os.path.dirname(__file__), "currency_name.json")
    with open(json_path, "r", encoding="utf-8") as f:
        currency_names = json.load(f)
    

    return render_template(
        'index.html',
        currencies=currencies,
        currency_symbols=currency_symbols,
        currency_names=currency_names , 
        result=result,
        second_result=second_result,
        display_amount=display_amount
        )


@app.route("/data/currency_meta.json")
def get_currency_meta():
    base_path = os.path.dirname(__file__)  # this is main_code/
    return send_from_directory(base_path, "currency_meta.json")

@app.route('/symbol')
def symbol_page():
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "currency_meta.json")
    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Filter only entries with valid structure
    currencies = {
        code: data
        for code, data in raw_data.items()
        if isinstance(data, dict) and "country" in data and "flag" in data
    }

    symbols_path = os.path.join(base_path, "currency_symbols.json")
    with open(symbols_path, "r", encoding="utf-8") as f:
        currency_symbols = json.load(f)

    currency_names = {}
    try:
        json_path = os.path.join(os.path.dirname(__file__), "currency_name.json")
        with open(json_path, "r", encoding="utf-8") as f:
            currency_names = json.load(f)
    except Exception as e:
        print(f"Error loading currency names: {e}")


    return render_template(
        "symbol.html",
        "chart.html", 
        currencies=currencies , 
        currency_symbols=currency_symbols,
        currency_names=currency_names   
    )

@app.route('/get_quiz')
def get_quiz():
    quiz_path = os.path.join(os.path.dirname(__file__), "currency_quiz.json")
    try:
        with open(quiz_path, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)
        return jsonify(quiz_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/chart")
def chart():
    currencies_api = get_supported_currencies()
    json_path = os.path.join(os.path.dirname(__file__), "currency_meta.json")
    with open(json_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)

    currencies = {}
    for code in currencies_api:
        country = meta_data.get(code, {}).get("country", currencies_api[code]["description"])
        flag = meta_data.get(code, {}).get("flag", None)
        currencies[code] = {
            "country": country,
            "flag": flag,
        }

    return render_template("chart.html", currencies=currencies)

@app.route("/get_chart_data")
def get_chart_data():
    base = request.args.get("base")
    target = request.args.get("target")
    start = request.args.get("start")
    end = request.args.get("end")

    if not all([base, target, start, end]):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start}&end_date={end}&base={base}&symbols={target}"
        headers = {
            "apikey": os.getenv("APILAYER_API_KEY")
        }

        response = requests.get(url, headers=headers)
        data = response.json()


        if not data.get("success") or "rates" not in data:
            print("[ERROR] API returned failure or no rates.",data)
            return jsonify({"error": "Could not fetch historical data."}), 500

        rates = []
        for date, rate_info in data["rates"].items():
            rate = rate_info.get(target)
            if rate is not None:
                rates.append({"date": date, "rate": rate})

        rates.sort(key=lambda x: x["date"])
        print("📤 Returning this JSON:", rates)  
        return jsonify(rates)

    except Exception as e:
        print("[ERROR] /get_chart_data failed:", e)
        return jsonify({"error": "Server error fetching chart data."}), 500



if __name__ == '__main__':
    app.run(debug=True)
