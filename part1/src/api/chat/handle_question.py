import re
from chat.question_bank import DIRECTIONAL_QUESTIONS, INGREDIENT_QUESTIONS
from process_recipe.recipe import Recipe


def classify_question(question: str) -> str:
    question_clean = question.lower()
    question_clean = re.sub(r"[^\w\s]", "", question_clean)
    question_clean = " ".join(question_clean.split())
    # Split into words
    keywords = [w for w in question_clean.split() if w not in ("a", "an", "the")]


    # Compute proportion match scores for each group by comparing cleaned keywords
    def score_against_bank(question_keywords, bank):
        max_score = 0
        best_key = None
        for k in bank:
            k_words = [w for w in k.lower().split() if w not in ("a", "an", "the")]
            if not k_words:
                continue
            match_count = sum(1 for word in k_words if word in question_keywords)
            score = match_count / len(k_words)
            if score > max_score:
                max_score = score
                best_key = k
        return max_score, best_key

    dir_score, dir_key = score_against_bank(keywords, DIRECTIONAL_QUESTIONS)
    ingr_score, ingr_key = score_against_bank(keywords, INGREDIENT_QUESTIONS)

    # Choose group with best score, threshold could be tuned
    if dir_score >= ingr_score and dir_score > 0:
        return DIRECTIONAL_QUESTIONS[dir_key]
    elif ingr_score > 0:
        return INGREDIENT_QUESTIONS[ingr_key]
    else:
        return "none"



def handle_question(question: str, recipe: Recipe) -> str:
    
    question_type = classify_question(question)

    if question_type in ["next_step", "previous_step", "current_step"]:
        # TODO: Flesh out the responses so that they contain relevant information and update states
        return "Step information"
    elif question_type in ["all_ingredients", "step_ingredients"]:
        # TODO: Flesh out the responses so that they contain relevant information
        return "Ingredient information"
    else:
        return "I'm sorry, I don't know the answer to that question."