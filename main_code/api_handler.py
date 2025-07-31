import requests
import json
from flask import Blueprint, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
from pathlib import Path


def get_supported_currencies():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD")
        res.raise_for_status()
        data = res.json()
        print("[DEBUG] Fallback API response:", data)
        if data.get("result") == "success":
            # Build fake descriptions (code itself)
            return {code: {"description": code} for code in data["rates"].keys()}
        else:
            print("[ERROR] API returned failure")
            return {}
    except Exception as e:
        print("[ERROR] Exception while fetching currencies:", str(e))
        return {}


def convert_currency(from_currency, to_currency, amount):
    try:
        res = requests.get(f"https://open.er-api.com/v6/latest/{from_currency}")
        res.raise_for_status()
        data = res.json()
        rate = data["rates"].get(to_currency)
        if rate:
            return {
                "rate": rate,
                "result": round(rate * amount, 6),
                "date": data["time_last_update_utc"]
            }
        else:
            print("[ERROR] Invalid target currency")
            return None
    except Exception as e:
        print("[ERROR] Failed to convert currency:", str(e))
        return None

api_blueprint = Blueprint("api", __name__)
@api_blueprint.route("/api/rates/<base_currency>")
def get_rates(base_currency):
    rates = get_exchange_rates(base_currency)
    if not rates:
        return jsonify({"error": "Failed to fetch data"}), 500
    return jsonify(rates)

def get_exchange_rates(base="USD"):
    try:
        with open(f"cache/day2/{base}.json", "r", encoding="utf-8") as f:
            today_data = json.load(f)

        with open(f"cache/day1/{base}.json", "r", encoding="utf-8") as f:
            yesterday_data = json.load(f)

        with open("currency_meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)

                # Load comparison result
        comparison_data = {}
        try:
            with open("data/comparison_result.json", "r", encoding="utf-8") as f:
                comparison_data = json.load(f)
        except Exception as e:
            print(f"[WARN] Could not load comparison data: {e}")

        today_rates = today_data.get("rates", {})
        yesterday_rates = yesterday_data.get("rates", {})

        rate_comparison = []
        for code, today_rate in today_rates.items():
            yest_rate = yesterday_rates.get(code)
            if yest_rate is None:
                continue
            
            change = 0.0
            indicator = "➖"
    
            change_data = comparison_data.get(base, {}).get("changed", {}).get(code)
            if change_data:
                change = round(change_data["new"] - change_data["old"], 4)
                if change > 0:
                    indicator = "📈"
                elif change < 0:
                    indicator = "📉"
                else:
                    indicator = "➖"


            rate_comparison.append({
                "currency": code,
                "rate": round(today_rate, 4),
                "change": change,
                "indicator": indicator,
                "country": meta.get(code, {}).get("country", "Unknown"),
                "flag": meta.get(code, {}).get("flag", "")
            })

        return {
            "date": today_data.get("time_last_update_utc", today_data.get("date", "")),
            "rates": sorted(rate_comparison, key=lambda x: x["currency"]),
            "base": base
        }

    except Exception as e:
        print("[ERROR] Failed to fetch rates from cache:", str(e))
        return None


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
news_bp = Blueprint('news_bp', __name__)
NEWS_API_KEY = os.getenv('NEWS_KEY')
@news_bp.route('/get_news')
def get_news():
    if not NEWS_API_KEY:
        return jsonify({"error": "API key not set"}), 500

    url =(
         f'https://newsapi.org/v2/everything?q=currency OR forex&'
         f'sortBy=publishedAt&pageSize=10&apiKey={NEWS_API_KEY}'
    )
    response = requests.get(url)
    data = response.json()
    
    if data.get("status") != "ok":
        return jsonify({"error": "Failed to fetch news"}), 500

    articles = data["articles"]
    simplified = [
        {"title": a["title"], "url": a["url"]}
        for a in articles if a.get("title") and a.get("url")
    ]

    return jsonify(simplified)
