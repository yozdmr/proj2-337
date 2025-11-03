import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask import Flask, request, jsonify

from process_recipe.extract_ingredients import extract_ingredients
from process_recipe.extract_steps import extract_steps

app = Flask(__name__)

curr_recipe = None
curr_rec = None
curr_ingredients = None
curr_steps = None
allowed_domains = [
    "foodnetwork.com",
    "seriouseats.com",
    "allrecipes.com",
]

@app.get("/")
def home():
    return "OK", 200

@app.post("/get-recipe")
def get_recipe():
    global curr_recipe
    global curr_rec
    global allowed_domains
    global curr_ingredients
    global curr_steps

    data = request.get_json(silent=True) or {}
    url = data.get("url")

    if not url or not isinstance(url, str):
        return jsonify({"error": "Missing or invalid 'url' field"}), 400

    # Basic URL format validation
    url_pattern = re.compile(r"^(https?://)[^\s/$.?#].[^\s]*$", re.IGNORECASE)
    if not url_pattern.match(url):
        return jsonify({"error": "Invalid URL format"}), 400

    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if not any(hostname == d or hostname.endswith("." + d) for d in allowed_domains):
        return jsonify({"error": "URL must be from foodnetwork.com, seriouseats.com, or allrecipes.com"}), 400

    # Fetch the page and parse HTML with BeautifulSoup
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch URL", "detail": str(e)}), 502

    if response.status_code < 200 or response.status_code >= 300:
        return jsonify({"error": f"Upstream returned status {response.status_code}"}), 502

    soup = BeautifulSoup(response.text, "html.parser")
    curr_recipe = url
    curr_rec = str(soup)

    # Process the recipe and extract necessary information
    ingredients = extract_ingredients(curr_rec)
    curr_ingredients = ingredients

    steps = extract_steps(curr_rec, ingredients)
    curr_steps = steps


    return jsonify({"status": "saved", "curr_recipe": curr_recipe, "num_steps": len(steps)}), 200

@app.get("/get-ingredients")
def get_ingredients():
    global curr_ingredients
    if curr_ingredients is None:
        return jsonify({"error": "No ingredients saved"}), 404
    return jsonify({"ingredients": curr_ingredients}), 200



@app.get("/get-steps")
def get_steps():
    global curr_steps
    if curr_steps is None:
        return jsonify({"error": "No steps saved"}), 404
    return jsonify({"steps": curr_steps}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

