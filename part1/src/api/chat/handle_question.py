import re
from chat.question_bank import DIRECTIONAL_QUESTIONS, INGREDIENT_QUESTIONS, TIME_QUESTIONS
from process_recipe.recipe import Recipe


def classify_question(question: str) -> str:
    # Normalize question: lowercase, remove punctuation, normalize whitespace
    question_normalized = question.lower().strip()
    question_normalized = re.sub(r"[^\w\s]", "", question_normalized)
    question_normalized = " ".join(question_normalized.split())
    
    # Get question words (excluding common stop words for better matching)
    stop_words = {"a", "an", "the", "is", "are", "what", "which", "when", "where", "who", "why", "yes", "no"}
    question_words = set(w for w in question_normalized.split() if w not in stop_words)
    
    # All question banks to check
    question_banks = [
        DIRECTIONAL_QUESTIONS,
        INGREDIENT_QUESTIONS,
        TIME_QUESTIONS
    ]
    
    best_match = None
    best_match_score = 0
    
    # Check each question bank for matches
    for bank in question_banks:
        for key_phrase, category in bank.items():
            # Normalize key phrase the same way
            key_normalized = key_phrase.lower().strip()
            key_normalized = re.sub(r"[^\w\s]", "", key_normalized)
            key_normalized = " ".join(key_normalized.split())
            
            # Get key words (excluding stop words)
            key_words = set(w for w in key_normalized.split() if w not in stop_words)
            
            # Step 1: Exact substring match
            if key_normalized in question_normalized or question_normalized in key_normalized:
                # Prefer longer matches (more specific)
                score = len(key_normalized)
                if score > best_match_score:
                    best_match = category
                    best_match_score = score
            # Step 2: Word overlap (makes it more flexible)
            elif key_words and question_words:
                # Calculate overlap: how many key words appear in question
                overlap = len(key_words & question_words)
                # Score based on overlap ratio (prefer matches with more overlap)
                overlap_ratio = overlap / len(key_words)
                # Also consider the length of the key (prefer longer, more specific keys)
                score = overlap_ratio * len(key_normalized)
                
                # Require at least 50% word overlap to consider it a match
                if overlap_ratio >= 0.5 and score > best_match_score:
                    best_match = category
                    best_match_score = score
    
    return best_match if best_match else "none"


def handle_question(question: str, recipe: Recipe) -> str:
    
    question_type = classify_question(question)

    if question_type in ["next_step", "previous_step", "current_step"]:
        # TODO: Flesh out the responses so that they contain relevant information and update states
        return "Step information"
    elif question_type in ["all_ingredients", "step_ingredients"]:
        # TODO: Flesh out the responses so that they contain relevant information
        return "Ingredient information"
    elif question_type in ["time"]:
        # TODO: Flesh out the responses so that they contain relevant information
        return "Time information"
    else:
        # TODO: Add "did you mean this?" functionality
        return "I'm sorry, I don't know the answer to that question."