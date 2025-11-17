import re
from process_recipe.recipe import Recipe

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


# Substitution dictionary
_SUBSTITUTIONS = {
    "butter": [
        "margarine (1:1)",
        "olive oil (about 3/4 as much as butter)",
        "coconut oil (1:1 in many baking recipes)",
    ],
    "milk": [
        "unsweetened almond milk (1:1)",
        "soy milk (1:1)",
        "oat milk (1:1)",
    ],
    "egg": [
        "1 tbsp ground flaxseed + 3 tbsp water (per egg)",
        "1/4 cup unsweetened applesauce (for baking)",
    ],
    "sour cream": [
        "plain Greek yogurt (1:1)",
        "plain yogurt (1:1)",
    ],
    "sugar": [
        "honey (use about 3/4 cup honey for 1 cup sugar and reduce other liquids)",
        "maple syrup (3/4 cup for 1 cup sugar)",
    ],
}


def _canonical_substitution_key(name: str) -> str:
    norm = _normalize_text_for_match(name)
    if "butter" in norm:
        return "butter"
    if "milk" in norm:
        return "milk"
    if "egg" in norm or "eggs" in norm:
        return "egg"
    if "sour cream" in norm or ("cream" in norm and "sour" in norm):
        return "sour cream"
    if "sugar" in norm:
        return "sugar"
    return norm


def return_ingredient_substitution_response(recipe: Recipe, question: str) -> tuple[str, str]:
    # Ingredient substitution, e.g. "What can I use instead of butter?"
    ing = _best_match_ingredient_from_question(question, recipe)
    raw_name = ""
    if ing is not None:
        raw_name = str(ing.get("name") or "").strip()

    if not raw_name:
        q_lower = question.lower()
        m = re.search(r"(?:instead of|substitute for|in place of)\\s+([a-zA-Z\\s]+)", q_lower)
        if m:
            raw_name = m.group(1).strip()

    if not raw_name:
        answer = (
            "I'm not sure which ingredient you want to replace. "
            "Try asking 'What can I use instead of butter?'"
        )
        ingredient_name = ""
    else:
        key = _canonical_substitution_key(raw_name)
        options = _SUBSTITUTIONS.get(key)

        if options:
            items_html = "".join(f"<li>{opt}</li>" for opt in options)
            answer = (
                f"Here are some common substitutes for {key}:"
                f"<ul>{items_html}</ul>"
            )
        else:
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

