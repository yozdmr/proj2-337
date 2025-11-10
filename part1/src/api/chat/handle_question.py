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
    exact_match_found = False
    
    # Check each question bank for matches
    for bank in question_banks:
        for key_phrase, category in bank.items():
            # Normalize key phrase the same way
            key_normalized = key_phrase.lower().strip()
            key_normalized = re.sub(r"[^\w\s]", "", key_normalized)
            key_normalized = " ".join(key_normalized.split())
            
            # Get key words (excluding stop words)
            key_words = set(w for w in key_normalized.split() if w not in stop_words)
            
            # Step 1: Exact match (highest priority - should win over everything)
            if key_normalized == question_normalized:
                exact_match_found = True
                best_match = category
                best_match_score = float('inf')  # Highest possible score
                continue
            
            # Step 2: Exact substring match (only if no exact match found yet)
            if not exact_match_found:
                if key_normalized in question_normalized or question_normalized in key_normalized:
                    # For single-word questions, prevent matching against long multi-word keys
                    # This prevents "step" from matching "ingredients are used in this step"
                    question_word_count = len(question_words)
                    key_word_count = len(key_words)
                    
                    # Single-word questions should only match single-word or two-word keys
                    if question_word_count == 1 and key_word_count > 2:
                        continue
                    
                    # Prefer longer matches (more specific)
                    score = len(key_normalized)
                    if score > best_match_score:
                        best_match = category
                        best_match_score = score
                # Step 3: Word overlap (makes it more flexible)
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

    if question_type in ["next_step", "previous_step", "current_step", "first_step"]:
        if question_type == "next_step":
            curr_step = recipe.step_forward()
        elif question_type == "previous_step":
            curr_step = recipe.step_backward()
        elif question_type == "current_step":
            curr_step = recipe.current_step
        elif question_type == "first_step":
            # Avoid updating recipe.first_step so that it remains the same 
            first_step = recipe.first_step
            return f"<h4 class='chat-header'>Step {first_step.step_number}:</h4><p>{first_step.description}</p>"

        # Construct response
        response = f"<h4 class='chat-header'>Step {curr_step.step_number}:</h4><p>{curr_step.description}</p>"
        return response
        
    elif question_type in ["all_ingredients", "step_ingredients"]:
        if question_type == "all_ingredients":
            header = "Ingredients in the recipe:"
            ingredients = recipe.ingredients
        elif question_type == "step_ingredients":
            header = "Ingredients for this step:"
            ingredients = recipe.current_step.ingredients

        if len(ingredients) == 0 and header.split(" ")[-1] == "step:":
            return "There are no ingredients for this step."
        
        # Construct response with custom CSS class
        response = f'<h4 class="chat-header">{header}</h4><ul class="ingredient-list">'

        for ingredient in ingredients:
            response += f"<li>"
            if ingredient['descriptor'] is not None:
                desc_and_name = ingredient['descriptor'] + " " + ingredient['name']
            else:
                desc_and_name = ingredient['name']
            
            if len(desc_and_name) > 1:
                desc_and_name = desc_and_name[0].upper() + desc_and_name[1:]
            
            
            response += f"{desc_and_name}: {ingredient['quantity']}"

            if ingredient['measurement'] is not None:
                response += f" {ingredient['measurement']}"
            
            if ingredient['preparation'] is not None:
                response += f' <span>({ingredient["preparation"]})</span>'
            response += "</li>"
        response += "</ul>"
        
        return response


    elif question_type in ["time"]:
        # TODO: Flesh out the responses so that they contain relevant information
        return "Time information"
    else:
        # TODO: Add "did you mean this?" functionality
        return "I'm sorry, I don't know the answer to that question."