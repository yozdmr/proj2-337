from multiprocessing.connection import answer_challenge
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from flask import Flask, request, jsonify
from flask_cors import CORS

from process_recipe.extract_ingredients import extract_ingredients
from process_recipe.extract_steps import extract_steps
from process_recipe.step_components.extract_methods import extract_methods
from process_recipe.recipe import Recipe
from chat.handle_question import handle_question

app = Flask(__name__)
CORS(app)

recipe = None
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
    global recipe

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
    recipe_url = url
    recipe_text = str(soup)

    # Try to get the name of the page (recipe)
    recipe_name = None
    if soup.title:
        recipe_name = soup.title.get_text(strip=True)
    # Try other selectors if title is absent or looks generic
    if not recipe_name or recipe_name.lower() in ['untitled', 'recipe', 'foodnetwork.com']:
        # Try h1 or class/id commonly used for recipe titles
        h1 = soup.find('h1')
        if h1 and h1.get_text(strip=True):
            recipe_name = h1.get_text(strip=True)

    # Process the recipe and extract necessary information
    ingredients = extract_ingredients(recipe_text)
    recipe = Recipe(
        recipe_name,
        recipe_url,
        extract_ingredients(recipe_text), 
        extract_steps(recipe_text, ingredients)
    )

    return jsonify({
        "status": "saved",
        "recipe_url": recipe.get_url(),
        "recipe_name": recipe.get_name(),
        "num_steps": len(recipe.get_steps())
    }), 200


@app.get("/get-steps")
def get_steps():
    global recipe
    if recipe.get_steps() is None:
        return jsonify({"error": "No steps saved"}), 404
    return jsonify({"steps": recipe.get_steps()}), 200

@app.get("/get-methods")
def get_methods():
    global recipe
    if not recipe or not recipe.get_steps():
        return jsonify({"error": "No recipe loaded"}), 404

    all_methods = []
    for step in recipe.get_steps():
        all_methods.extend(extract_methods(step["description"]))
    return jsonify({"methods": sorted(set(all_methods))}), 200


@app.post("/ask-question")
def ask_question():
    global recipe

    data = request.get_json(silent=True) or {}
    question = data.get("question")


    result = handle_question(question, recipe)
    
    # Handle both old string format and new dict format for backward compatibility
    if isinstance(result, str):
        return jsonify({"answer": result}), 200
    else:
        response = {"answer": result["answer"]}
        if result.get("suggestions"):
            response["suggestions"] = result["suggestions"]
        return jsonify(response), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

