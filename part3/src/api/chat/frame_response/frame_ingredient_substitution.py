import re
import os
import requests
from dotenv import load_dotenv
from process_recipe.recipe import Recipe

# Load environment variables
load_dotenv()

# Helper constants and functions for ingredient matching
_INGREDIENT_STOPWORDS = {
    "a", "an", "the", "of", "to", "for", "with",
    "how", "much", "many", "do", "does", "did",
    "i", "you", "we", "they", "he", "she", "it",
    "need", "needs", "needed", "use", "used", "using",
    "should", "this", "that", "step", "recipe",
    "instead", "can", "could",
}


def _normalize_text_for_match(text: str) -> str:
    text = re.sub(r"[^a-zA-Z\\s]", " ", text.lower())
    return " ".join(text.split())


def _get_ingredient_list(recipe):
    if recipe is None:
        return []
    # recipe class
    if hasattr(recipe, "get_ingredients"):
        try:
            ing = recipe.get_ingredients()
            if ing:
                return list(ing)
        except Exception:
            pass
    # fallback attributes
    if hasattr(recipe, "ingredients"):
        ing = getattr(recipe, "ingredients")
        if ing:
            return list(ing)
    # Dict-style
    if isinstance(recipe, dict):
        ing = recipe.get("ingredients")
        if ing:
            return list(ing)
    return []


def _best_match_ingredient_from_question(question: str, recipe):
    ingredients = _get_ingredient_list(recipe)
    if not ingredients:
        return None

    q_norm = _normalize_text_for_match(question)
    if not q_norm:
        return None

    q_tokens = [
        t for t in q_norm.split()
        if t and t not in _INGREDIENT_STOPWORDS
    ]
    if not q_tokens:
        # Fall back to using all tokens
        q_tokens = q_norm.split()
    q_token_set = set(q_tokens)

    best = None
    best_score = 0.0

    for ing in ingredients:
        # ingredient can be a dict or a simple string
        if isinstance(ing, dict):
            name = str(ing.get("name") or ing.get("ingredient") or ing.get("ingredient_name") or "")
        else:
            name = str(ing)
        name_norm = _normalize_text_for_match(name)
        if not name_norm:
            continue
        name_tokens = name_norm.split()
        name_token_set = set(name_tokens)
        if not name_token_set:
            continue

        overlap = len(q_token_set & name_token_set)
        overlap_ratio = overlap / len(name_token_set)

        substring_bonus = 0.0
        if name_norm in q_norm:
            substring_bonus = 0.5

        score = overlap_ratio + substring_bonus
        if score > best_score:
            best_score = score
            best = ing
            
    if best_score == 0.0:
        return None
    return best


def _get_substitutes_from_spoonacular(ingredient_name: str):
    api_key = os.getenv("SPOONACULAR_API_KEY")
    if not api_key:
        return None
    
    # Clean the ingredient name for the API
    ingredient_clean = ingredient_name.strip()
    if not ingredient_clean:
        return None
    
    url = f"https://api.spoonacular.com/food/ingredients/substitutes"
    params = {
        "ingredientName": ingredient_clean,
        "apiKey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

# Extract ingredient name from question using various patterns.
def _extract_ingredient_from_question(question: str) -> str:
    q_lower = question.lower()
    
    # Pattern 1: "instead of X", "substitute for X", "in place of X"
    patterns = [
        r"(?:instead\s+of|substitute\s+for|in\s+place\s+of)\s+([a-zA-Z\s]+?)(?:\?|$|\.|,|;|:|\s+can|\s+should|\s+could)",
        r"substitute\s+([a-zA-Z\s]+?)(?:\?|$|\.|,|;|:)",
        r"replace\s+([a-zA-Z\s]+?)(?:\?|$|\.|,|;|:|\s+with)",
        r"use\s+instead\s+of\s+([a-zA-Z\s]+?)(?:\?|$|\.|,|;|:)",
    ]
    
    for pattern in patterns:
        m = re.search(pattern, q_lower)
        if m:
            extracted = m.group(1).strip()
            # Remove common stopwords from the end
            extracted = re.sub(r'\s+(the|a|an|for|with|in|on|at|to|of)$', '', extracted)
            if extracted and len(extracted) > 1:
                return extracted
    
    # Pattern 2: Try to find ingredient after common question starters
    # "What can I use instead of X?"
    m = re.search(r"what\s+(?:can|should|could)\s+(?:i|we|you)\s+use\s+(?:instead\s+of|for)\s+([a-zA-Z\s]+?)(?:\?|$|\.)", q_lower)
    if m:
        extracted = m.group(1).strip()
        extracted = re.sub(r'\s+(the|a|an|for|with|in|on|at|to|of)$', '', extracted)
        if extracted and len(extracted) > 1:
            return extracted
    
    # pattern 3: flexible, look for any word that might be ingredient
    # desperation case
    m = re.search(r"(?:^|\s)([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2})\s+(?:substitute|instead)", q_lower)
    if m:
        extracted = m.group(1).strip()
        if extracted and len(extracted) > 1:
            return extracted
    
    return ""


def return_ingredient_substitution_response(recipe: Recipe, question: str) -> tuple[str, str]:
    # Ingredient substitution, e.g. "What can I use instead of butter?"
    raw_name = ""
    
    # first try to match from recipe ingredients
    ing = _best_match_ingredient_from_question(question, recipe)
    if ing is not None:
        raw_name = str(ing.get("name") or "").strip()
    
    # if not found in recipe extract from question text
    if not raw_name:
        raw_name = _extract_ingredient_from_question(question)
    
    # if still no ingredient found return not found message
    if not raw_name:
        answer =  "I'm not sure which ingredient you want to replace. "
        
        ingredient_name = ""
    else:
        # Fetch substitutes from Spoonacular API
        api_response = _get_substitutes_from_spoonacular(raw_name)
        
        if api_response and api_response.get("substitutes"):
            substitutes = api_response.get("substitutes", [])
            count = len(substitutes)
            items_html = "".join(f"<li>{sub}</li>" for sub in substitutes)
            answer = (
                f"<p>Found {count} possible substitute{'s' if count != 1 else ''} for {raw_name}:</p>"
                f"<ul>{items_html}</ul>"
            )
        else:
            # Fallback to Google search if API fails or returns no results
            q_param = f"substitute for {raw_name}".replace(" ", "+")
            url = f"https://www.google.com/search?q={q_param}"
            answer = (
                f"<p>I'm not sure about good substitutes for {raw_name}. "
                f"You can check some ideas "
                f"<span class='hyperlink'><a href='{url}' target='_blank' rel='noopener noreferrer'>"
                f"here</a>"
                f'<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-box-arrow-up-right" viewBox="0 0 16 16" style="display: inline; vertical-align: middle;">'
                f'<path fill-rule="evenodd" d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5"/>'
                f'<path fill-rule="evenodd" d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0z"/>'
                f'</svg></span>'
                f".</p>"
            )
        ingredient_name = raw_name

    return answer, ingredient_name

