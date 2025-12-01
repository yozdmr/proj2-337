import re
import os
import requests
from google import genai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, request, jsonify

from llm_context import LLM_CONTEXT


app = Flask(__name__)
CORS(app)

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

# Configure the GenAI client
client = genai.Client()
chat = client.chats.create(model="gemini-2.5-flash")
recipe = None



@app.get("/")
def home():
    return "OK", 200


# Extract text from recipe HTML for only Ingredients and Directions
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

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch URL", "detail": str(e)}), 502

    if response.status_code < 200 or response.status_code >= 300:
        return jsonify({"error": f"Upstream returned status {response.status_code}"}), 502

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")
    
    recipe_text = ""
    
    # Find div containing ingredients
    ingredients_div = soup.find('div', {'class': re.compile('ingredient', re.I)}) or \
                      soup.find('div', {'id': re.compile('ingredient', re.I)})
    
    if ingredients_div:
        print("FOUND INGREDIENTS")
        # Iterate through all HTML tags within the div and extract text
        ingredients_text = ""
        for tag in ingredients_div.find_all(True):  # True finds all tags
            text = tag.get_text(strip=True)
            if text:
                ingredients_text += text + "\n"
        if ingredients_text:
            recipe_text += "INGREDIENTS:\n" + ingredients_text.strip() + "\n\n"
    
    # Find div containing directions/instructions
    directions_div = soup.find('div', {'class': re.compile('instruction|direction|step|method', re.I)}) or \
                      soup.find('div', {'id': re.compile('instruction|direction|step|method', re.I)})
    
    if directions_div:
        print("FOUND DIRECTIONS")
        # Iterate through all HTML tags within the div and extract text
        directions_text = ""
        for tag in directions_div.find_all(True):  # True finds all tags
            text = tag.get_text(strip=True)
            if text:
                directions_text += text + "\n"
        if directions_text:
            recipe_text += "DIRECTIONS:\n" + directions_text.strip()
    
    # Store as global recipe variable
    recipe = recipe_text.strip()

    return jsonify({
        "status": "saved",
        "recipe_url": url,
        "recipe_name": soup.title.get_text(strip=True),
        "num_steps": -1  # Only have this here to match frontend expectations
    }), 200


@app.get("/show-recipe")
def show_recipe():
    global recipe
    return jsonify({"recipe": recipe}), 200

@app.post("/ask-question")
def ask_question():
    global recipe, chat

    data = request.get_json(silent=True) or {}
    question = data.get("question")

    if not question:
        return jsonify({"error": "Missing 'question' field"}), 400
    
    # Build the prompt with context, recipe, and user question
        # TODO: Provide chat history as context?
    #  for message in chat.get_history() ...
    prompt = f"Instructions:{LLM_CONTEXT}\nRecipe: {recipe}\nUser Question: {question}"

    if data.get("nohtml"):
        prompt += "\n\nDo not include any HTML tags in your response."
    
    # Send message using the chat session
    response = chat.send_message(prompt)
    
    result = {
        "answer": response.text,
        "suggestions": None
    }
    return jsonify(result), 200


@app.post("/reset")
def reset():
    global recipe, chat, client
    
    # Reset the global recipe to None
    recipe = None
    
    # Create a new chat session to reset the LLM context
    chat = client.chats.create(model="gemini-2.5-flash")
    
    return jsonify({"status": "reset"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

