
import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

API_KEY = os.environ.get("API_FOOTBALL_KEY")

@app.route("/")
def home():
    return "Daouda Sports Stats - Serveur actif !"

@app.route("/api/football/live")
def live_matches():
    if not API_KEY:
        return jsonify({"error": "Clé API non configurée"}), 500

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}

    try:
        response = requests.get(
            url,
            headers=headers,
            params={"live": "all"},
            timeout=15
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException:
        return jsonify({"error": "Erreur de connexion à l'API"}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
      
