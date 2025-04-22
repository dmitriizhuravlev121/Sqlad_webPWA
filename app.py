from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

BASE_ID = os.getenv("BASE_ID")
API_KEY = os.getenv("API_KEY")

if not BASE_ID or not API_KEY:
    raise ValueError("BASE_ID и API_KEY должны быть установлены в переменных окружения.")

@app.route('/add_stock', methods=['POST'])
def add_stock():
    data = request.json
    product_name = data.get("product_name")
    quantity = data.get("quantity")

    if not product_name or not quantity:
        return jsonify({"error": "Недостаточно данных"}), 400

    url = f"https://api.airtable.com/v0/{BASE_ID}/Поставки"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "records": [
            {
                "fields": {
                    "Товар": [product_name],
                    "Количество": int(quantity)
                }
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ошибка Airtable: {str(e)}"}), 500

@app.route('/subtract_stock', methods=['POST'])
def subtract_stock():
    data = request.json
    product_name = data.get("product_name")
    quantity = data.get("quantity")

    if not product_name or not quantity:
        return jsonify({"error": "Недостаточно данных"}), 400

    url = f"https://api.airtable.com/v0/{BASE_ID}/Списания"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "records": [
            {
                "fields": {
                    "Товар": [product_name],
                    "Количество": int(quantity)
                }
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ошибка Airtable: {str(e)}"}), 500

@app.route('/get_stock', methods=['POST'])
def get_stock():
    data = request.json
    product_name = data.get("product_name")

    if not product_name:
        return jsonify({"error": "Не указан товар"}), 400

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Запрашиваем поставки
    supply_url = f"https://api.airtable.com/v0/{BASE_ID}/Поставки?filterByFormula={{Товар}}='{product_name}'"
    try:
        supply_response = requests.get(supply_url, headers=headers)
        supply_response.raise_for_status()
        supply_records = supply_response.json().get("records", [])
        total_supply = sum(record["fields"].get("Количество", 0) for record in supply_records)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ошибка получения поставок: {str(e)}"}), 500

    # Запрашиваем списания
    withdraw_url = f"https://api.airtable.com/v0/{BASE_ID}/Списания?filterByFormula={{Товар}}='{product_name}'"
    try:
        withdraw_response = requests.get(withdraw_url, headers=headers)
        withdraw_response.raise_for_status()
        withdraw_records = withdraw_response.json().get("records", [])
        total_withdraw = sum(record["fields"].get("Количество", 0) for record in withdraw_records)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ошибка получения списаний: {str(e)}"}), 500

    # Вычисляем остаток
    quantity = total_supply - total_withdraw
    return jsonify({"quantity": max(quantity, 0)}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)