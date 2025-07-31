import os
import json
import requests
from datetime import datetime
import shutil
import sys

CACHE_DIR = "cache"
DAY1 = os.path.join(CACHE_DIR, "day1")
DAY2 = os.path.join(CACHE_DIR, "day2")
BASE_CURRENCIES = [
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL",
    "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", "CNY",
    "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP",
    "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL", "GGP", "GHS",
    "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF",
    "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD",
    "JPY", "KES", "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT",
    "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD",
    "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MYR", "MZN",
    "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK",
    "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
    "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD",
    "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY",
    "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES",
    "VND", "VUV", "WST", "XAF", "XCD", "XDR", "XOF", "XPF", "YER", "ZAR",
    "ZMW", "ZWL"
]

def is_already_updated():
    sample_currency = "USD"
    file_path = os.path.join(DAY2, f"{sample_currency}.json")
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            api_date_str = data.get("time_last_update_utc", "")
            if not api_date_str:
                return False

            # Parse API date
            api_date = datetime.strptime(api_date_str, "%a, %d %b %Y %H:%M:%S %z").date()
            today = datetime.utcnow().date()
            print(f"[CHECK] API last update date: {api_date} | Today: {today}")
            return api_date == today
    except Exception as e:
        print(f"[ERROR] Checking update status: {e}")
        return False


def fetch_and_save_all_rates(target_folder):
    os.makedirs(target_folder, exist_ok=True)

    for base in BASE_CURRENCIES:
        url = f"https://open.er-api.com/v6/latest/{base}"
        try:
            res = requests.get(url)
            res.raise_for_status()
            with open(os.path.join(target_folder, f"{base}.json"), "w", encoding="utf-8") as f:
                json.dump(res.json(), f, indent=2)
            print(f"[SAVED] {base} rates to {target_folder}")
        except Exception as e:
            print(f"[ERROR] Failed to fetch {base}: {str(e)}")

def rotate_cache():
    # Move day2 -> day1
    if os.path.exists(DAY2):
        shutil.rmtree(DAY1, ignore_errors=True)
        shutil.copytree(DAY2, DAY1)
        shutil.rmtree(DAY2, ignore_errors=True)

def save_comparison():
    currencies = [
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL",
    "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", "CNY",
    "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP",
    "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL", "GGP", "GHS",
    "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF",
    "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD",
    "JPY", "KES", "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT",
    "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD",
    "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MYR", "MZN",
    "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK",
    "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
    "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD",
    "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY",
    "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES",
    "VND", "VUV", "WST", "XAF", "XCD", "XDR", "XOF", "XPF", "YER", "ZAR",
    "ZMW", "ZWL"
]
    result = {}

    for base in currencies:
        try:
            with open(f"cache/day2/{base}.json", "r", encoding="utf-8") as f2, \
                 open(f"cache/day1/{base}.json", "r", encoding="utf-8") as f1:
                today = json.load(f2)
                yesterday = json.load(f1)

            changes = {}
            for code, today_rate in today.get("rates", {}).items():
                yest_rate = yesterday.get("rates", {}).get(code)
                if yest_rate is None:
                    continue
                if round(today_rate, 4) != round(yest_rate, 4):
                    changes[code] = {
                        "old": round(yest_rate, 4),
                        "new": round(today_rate, 4)
                    }

            if changes:
                result[base] = {
                    "date": today.get("time_last_update_utc", "--"),
                    "changed": changes
                }

        except Exception as e:
            print(f"[ERROR] Comparing {base}: {e}")

    os.makedirs("data", exist_ok=True)

    with open("data/comparison_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

def check_last_update_dates():
    sample_currency = "USD"
    day1_file = os.path.join(DAY1, f"{sample_currency}.json")
    day2_file = os.path.join(DAY2, f"{sample_currency}.json")
    
    try:
        with open(day1_file, "r", encoding="utf-8") as f1, open(day2_file, "r", encoding="utf-8") as f2:
            day1_data = json.load(f1)
            day2_data = json.load(f2)
            
            day1_date = day1_data.get("time_last_update_utc")
            day2_date = day2_data.get("time_last_update_utc")
            
            if day1_date == day2_date:
                print(f"[⚠️ WARNING] No change in API data date: {day1_date}")
            else:
                print(f"[✅ OK] Comparing: Yesterday ({day1_date}) vs Today ({day2_date})")
    except Exception as e:
        print("[ERROR]", e)

force_update = "--force" in sys.argv

if __name__ == "__main__":
    print("[🔍] Checking if cache is already updated today...")

    if is_already_updated() and not force_update:
        print("[🔁] Cache already updated today. Skipping update.")
    else:
        print("[♻️] Fetching fresh data (forced)." if force_update else "[♻️] Fresh update required.")
        rotate_cache()
        fetch_and_save_all_rates(DAY2)
        check_last_update_dates()
        save_comparison()
        print("[✅] Update complete.")